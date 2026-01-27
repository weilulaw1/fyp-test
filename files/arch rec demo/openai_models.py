import openai
import requests
import json
import random
import pymongo
import hashlib
import os
from functools import partial
import time
from multiprocessing import Manager
from multiprocessing.pool import ThreadPool
import threading

from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
try:
    from langchain_ollama import ChatOllama
except ImportError:
    ChatOllama = None
    
AzureAIChatCompletionsModel = None
HumanMessage = SystemMessage = AIMessage = None
ChatOllama = None


from datetime import datetime
from traceback import format_exc
from typing import Dict, List, Any, Union
# import utils.global_vars as gv
from keys import OPENAI_API_KEY
# from keys import AZUREAI_4O_MINI_ENDPOINT, AZUREAI_4O_MINI_KEY, AZUREAI_ENDPOINT_KEY
from settings import LLAMA_33_MODEL, GPT_4O_MINI_MODEL, DS_R1_MODEL
from settings import MODEL2CONTEXT_WINDOW, MODEL2PRICE_PER_TOKEN_RESPONSE, MODEL2PRICE_PER_TOKEN_PROMPT
from settings import OLLAMA_ENDPOINT


import logging
logger = logging.getLogger(__name__)
try:
    from settings import MONGO_ADDR, GPT_MONGO_DB, GPT_MONGO_COLLECTION
except:
    logger.warning("Settings not found, using default values")
    MONGO_ADDR = None

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


import tiktoken
gpt_encoder = tiktoken.encoding_for_model(GPT_4O_MINI_MODEL)
MAX_MULTI_THREAD_REQUESTS = 4


OFFLINE_ONLY = True


def map_message(message):
    role = message.get('role')
    content = message.get('content', '')

    if role == 'user':
        return HumanMessage(content=content)
    elif role == 'system':
        return SystemMessage(content=content)
    elif role == 'assistant':
        return AIMessage(content=content)
    else:
        raise ValueError(f"Unknown role: {role}")

def strip_oversized_message(messages, max_tokens):
    msg_ind2tkn_cnt = {}
    for i, m in enumerate(messages):
        # encode the message
        tkns = gpt_encoder.encode(m["content"])
        msg_ind2tkn_cnt[i] = len(tkns)
    msg_ind2tkn_cnt_all = msg_ind2tkn_cnt.copy()
    
    msg_ind_to_pop = []
    while sum(msg_ind2tkn_cnt.values()) > max_tokens:
        ind = max(msg_ind2tkn_cnt.keys())
        msg_ind_to_pop.append(ind)
        msg_ind2tkn_cnt.pop(ind)
    if msg_ind_to_pop:
        messages = messages[:len(messages)-len(msg_ind_to_pop)+1]
        remaining_tkn = max_tokens - sum(msg_ind2tkn_cnt.values())
        keep_pct = remaining_tkn / msg_ind2tkn_cnt_all[msg_ind_to_pop[-1]] * 0.9
        messages[-1]["content"] = messages[-1]["content"][:int(len(messages[-1]["content"])*keep_pct)]
    return messages

class GPTModel:
    
    static_gpt_price = 0
    static_cache_hit_count = 0
    static_ask_count = 0
    
    def __init__(self, tools: Union[Dict|List] = None, model: str = GPT_4O_MINI_MODEL, record_usage: bool = (MONGO_ADDR is not None), use_cache: bool = False):
        # self.tools = tools
        self.model: str = model
        self.total_prompt_tokens: int = 0
        self.total_response_tokens: int = 0
        self.total_price: float = 0
        self.record_usage: bool = record_usage
        self.col_mongo = None
        self.use_cache = use_cache
        if record_usage:
            self.col_mongo = pymongo.MongoClient(MONGO_ADDR)[GPT_MONGO_DB][GPT_MONGO_COLLECTION]
        
        self.price_per_token_prompt = MODEL2PRICE_PER_TOKEN_PROMPT[self.model]
        self.price_per_token_response = MODEL2PRICE_PER_TOKEN_RESPONSE[self.model]
        try:
            self.max_tokens = MODEL2CONTEXT_WINDOW[self.model]
        except:
            self.max_tokens = 128000
            logger.warning(f"Model {self.model} not found in MODEL2CONTEXT_WINDOW, using default max_tokens = 128000")
        self.tool_name2tool = {}
        if tools is not None:
            if isinstance(tools, Dict):
                tools = [tools]
            for tool in tools:
                self.tool_name2tool[tool["function"]["name"]] = tool
        
        self.is_langchain_model = False
    '''
    Ask without tool
    '''
    def ask(self, msg: Union[str|List], seed=None, response_json = False) -> str:
        if GPTModel.static_gpt_price > 100:
            raise
        messages = self._get_messages(msg)
        seed = seed if seed is not None else random.randint(0, 1000000)
        
        messages_stripped = messages
        if len(messages_stripped) != len(messages):
            logger.warning(f"Stripped {len(messages) - len(messages_stripped)} messages")
        messages = messages_stripped
        
        if self.use_cache:
            cache = self._get_cache(messages, seed, response_json=response_json)
            if cache is not None:
                return cache["response"]
        
        self.is_langchain_model = False
        if self.model in [DS_R1_MODEL, ]:
        # if self.model in [DS_R1_MODEL]:
            langchain_messages = [map_message(msg) for msg in messages]
            model = 'csl-malicious-4o-mini' if self.model == GPT_4O_MINI_MODEL else self.model
            client = AzureAIChatCompletionsModel(
                endpoint=AZUREAI_4O_MINI_ENDPOINT,
                credential=AZUREAI_4O_MINI_KEY,
                model_name=model,
                # api_version='2024-02-15-preview'
                # api_version='2023-07-01-preview'
            )

            # Generate a response
            response = client.invoke(langchain_messages)
            self.is_langchain_model = True
            pass
        elif self.model == LLAMA_33_MODEL:
            # Ollama HTTP backend (no langchain needed)
            url = OLLAMA_ENDPOINT.rstrip("/") + "/api/chat"

            payload = {
                "model": self.model,
                "messages": messages,          # OpenAI-style messages works with Ollama /api/chat
                "stream": False,
                "options": {
                    "seed": int(seed) if seed is not None else 0,
                    "temperature": 0,
                }
            }

            # Ask for JSON-only when needed
            if response_json:
                payload["format"] = "json"

            r = requests.post(url, json=payload, timeout=600)
            r.raise_for_status()
            data = r.json()

            # Ollama /api/chat response shape: {"message": {"role": "...", "content": "..."}, ...}
            content = (data.get("message") or {}).get("content", "")

            # mark as "langchain model" to skip _update_states (no token usage object)
            self.is_langchain_model = True
            response = type("OllamaResp", (), {"content": content, "usage_metadata": {"input_tokens": 0, "output_tokens": 0}, "response_metadata": {}})()

        # !!!
        # elif self.model == GPT_4O_MINI_MODEL:
        # elif False:
        #     try:
        #         client = AzureOpenAI(
        #             azure_endpoint=AZUREAI_4O_MINI_ENDPOINT,
        #             api_key=AZUREAI_4O_MINI_KEY,
        #             api_version="2024-05-01-preview"
        #             )
        #         response = client.chat.completions.create(
        #             model="csl-malicious-4o-mini",
        #             messages=messages,
        #             response_format={ "type": "text" } if not response_json else { "type": "json_object" },
        #             temperature=0,
        #             seed=seed,
        #         )
        #         pass
        #     except:
        #         logger.error(format_exc())
        #         logger.error("Failed to use Azure AI, switch to OpenAI")
        #         client = openai.OpenAI()
                
        #         response = client.chat.completions.create(
        #             model=self.model,
        #             messages=messages,
        #             response_format={ "type": "text" } if not response_json else { "type": "json_object" },
        #             temperature=0,
        #             seed=seed,
        #         )
            
        else:
            if OFFLINE_ONLY:
                raise RuntimeError(
                    f"OFFLINE_ONLY is enabled but model='{self.model}' is not routed to Ollama. "
                    f"Set gpt_type=LLAMA_33_MODEL or update routing."
        )
            client = openai.OpenAI()
            
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={ "type": "text" } if not response_json else { "type": "json_object" },
                temperature=0,
                seed=seed,
            )
            
        if not self.is_langchain_model:
            self._update_states(response)
        self._record_usage(messages, response, seed, response_json=response_json)
        if self.is_langchain_model:
            return response.content
        return response.choices[0].message.content

    
    
    '''
    Ask with one tool
    '''
    def ask_with_tool(self, msg: str, tool_name: str, force_tool_usage = True, seed=None) -> str:
        if GPTModel.static_gpt_price > 100:
            raise
        messages = self._get_messages(msg)
        seed = seed if seed is not None else random.randint(0, 1000000)
        
        assert tool_name in self.tool_name2tool, f"Tool {tool_name} not found"
        tool = self.tool_name2tool[tool_name]
        
        tool_choice = "auto"
        if force_tool_usage:
            tool_choice = {'type': 'function', 'function': {"name": tool_name}}
        
        if self.use_cache:
            cache = self._get_cache(messages, seed, tools=[tool], tool_choice=tool_choice, response_json = False)
            if cache is not None:
                return json.loads(cache["function_result"])
        
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=[tool],
            tool_choice=tool_choice,
            seed=seed,
            temperature=0,
        )
        
        self._update_states(response)
        self._record_usage(messages, response, seed, tools=[tool], tool_choice=tool_choice)
        
        return json.loads(response.choices[0].message.tool_calls[0].function.arguments)

    def get_total_price(self) -> Dict[str, int]:
        try:
            query_result = self.col_mongo.aggregate([
                {
                    "$group": {
                        "_id": None,
                        "total_price": {"$sum": "$price"},
                    }
                }
            ])
            total_price_mongo = list(query_result)[0]["total_price"]
        except:
            total_price_mongo = None
        return {
            "session": self.total_price,
            "mongo": total_price_mongo
        }

    def _update_states(self, response):
        
        self.total_prompt_tokens += response.usage.prompt_tokens
        self.total_response_tokens += response.usage.completion_tokens
        
        price_last = self.total_price
        price_now = self.total_prompt_tokens * self.price_per_token_prompt + self.total_response_tokens * self.price_per_token_response
        
        price_increase = price_now - price_last
        self.total_price = price_now
        GPTModel.static_gpt_price += price_increase
        GPTModel.static_ask_count += 1
        
        logger.debug(f"Price this request: ${price_increase:.5f}; Total Price: ${price_now:.5f}")

    def _record_usage(self, messages, response, seed, tools=None, tool_choice=None, response_json = False):
        if self.record_usage:
            try:
                doc = self._get_mongo_doc(messages, response, seed, tools, tool_choice, response_json)
                self.col_mongo.insert_one(doc)
            except:
                logger.error("Failed to record usage to MongoDB")
                logger.error(format_exc())
    
    def _get_mongo_doc(self, msgs, response, seed, tools=None, tool_choice=None, response_json = False):
        
        func_name = None
        func_result = None
        if not self.is_langchain_model:
            if 'tool_calls' in response.choices[0].message.model_fields and response.choices[0].message.tool_calls is not None:
                func_name = response.choices[0].message.tool_calls[0].function.name
                func_result = response.choices[0].message.tool_calls[0].function.arguments
        input_hash = self._get_input_hash(msgs, seed, tools, tool_choice, response_json)
        
        if len(msgs) == 1:
            msgs = msgs[0]["content"]
        if self.is_langchain_model:
            finish_reason = response.response_metadata['done_reason'] if 'done_reason' in response.response_metadata else None
        else:
            finish_reason = response.choices[0].finish_reason
        return {
            "time": datetime.now(),
            "prompt": msgs,
            "response": response.choices[0].message.content if not self.is_langchain_model else response.content,
            "finish_reason": finish_reason,
            "function_name": func_name,
            "function_result": func_result,
            "seed": seed,
            "response_json": response_json,
            "model": self.model,
            "key": OPENAI_API_KEY[-4:],
            "prompt_tokens": response.usage.prompt_tokens if not self.is_langchain_model else response.usage_metadata['input_tokens'],
            "response_tokens": response.usage.completion_tokens if not self.is_langchain_model else response.usage_metadata['output_tokens'],
            "price": response.usage.prompt_tokens*self.price_per_token_prompt + response.usage.completion_tokens*self.price_per_token_response if not self.is_langchain_model else 0,
            "tools": tools,
            "tool_choice": tool_choice,
            "hash": input_hash,
            "system_fingerprint": response.system_fingerprint if not self.is_langchain_model else None,
        }
        
    def _get_messages(self, msg: str) -> List[Dict[str, str]]:
        if type(msg) == str:
            return [{
                "role": "user",
                "content": msg
            }]
        else:
            assert all('role' in m and 'content' in m for m in msg)
            return msg

    def _get_input_hash(self, messages, seed, tools, tool_choice, response_json = False):
        hash_dict = {}
        hash_dict["messages"] = messages
        hash_dict["seed"] = seed
        if tools is not None:
            hash_dict["tools"] = tools
        if tool_choice is not None:
            hash_dict["tool_choice"] = tool_choice
        if response_json:
            hash_dict["response_json"] = response_json
        hash_dict["model"] = self.model
        return hashlib.sha256(json.dumps(hash_dict).encode()).hexdigest()
    
    def _get_cache(self, messages, seed, tools=None, tool_choice=None, response_json=False):
        input_hash = self._get_input_hash(messages, seed, tools, tool_choice, response_json)
        result = self.col_mongo.find_one({"hash": input_hash}, {"_id": 0, "response": 1})
        if result is not None:
            logger.debug("Cache Hit")
            GPTModel.static_cache_hit_count += 1
        return result

    def ask_batch(self, messages_list: List[Union[str|List]], seeds: Union[int|List[int]] = None, response_json: bool = False, max_workers: int = MAX_MULTI_THREAD_REQUESTS) -> List[str]:
        """
        Process multiple conversation threads in parallel using multiprocessing with progress reporting.
        
        Args:
            messages_list: List of conversation threads, where each thread is either a string or a list of messages
            seeds: Optional seed or list of seeds for each thread. If None, random seeds will be generated.
                  If a single integer is provided, that seed will be used for all threads.
            response_json: Whether to request JSON response format
            max_workers: Maximum number of worker processes. If None, uses number of CPU cores
            
        Returns:
            List of responses, one for each conversation thread
        """
        if GPTModel.static_gpt_price > 100:
            raise
        
        if seeds is None:
            seeds = [random.randint(0, 1000000) for _ in range(len(messages_list))]
        elif isinstance(seeds, int):
            seeds = [seeds] * len(messages_list)
        elif len(seeds) != len(messages_list):
            raise ValueError("Number of seeds must match number of conversation threads")
            
        # Create a partial function with fixed arguments
        ask_func = partial(self._ask_single, response_json=response_json)
        
        with ThreadPool(processes=max_workers) as pool:
            # Create a simple counter for progress tracking
            total = len(messages_list)
            counter = 0
            lock = threading.Lock()
            
            def progress_callback(_):
                nonlocal counter
                with lock:
                    counter += 1
                    logger.info(f"Progress: {counter}/{total} ({counter/total*100:.1f}%)")
            
            # Create a partial function with fixed arguments
            ask_func = partial(self._ask_single, response_json=response_json)
        
            # Create tasks with progress callback
            tasks = []
            for msg, seed in zip(messages_list, seeds):
                task = pool.apply_async(ask_func, args=(msg, seed))
                tasks.append(task)
        
            # Get results
            results = [task.get() for task in tasks]
            pass
        
        # logger.info(f"Completed: {counter}/{total} ({counter/total*100:.1f}%)")
        return results

    def _ask_single(self, msg: Union[str|List], seed: int, response_json: bool = False) -> str:
        """
        Helper method to process a single conversation thread.
        This is used by the multiprocessing pool.
        """
        return self.ask(msg, seed=seed, response_json=response_json)
