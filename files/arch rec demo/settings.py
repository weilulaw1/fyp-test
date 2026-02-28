import os

## Basic settings
CACHE_PATH = '.cache'
if os.name == 'nt':
    CTAG_PATH = './ext_tools/ctag/ctags.exe'
else:
    CTAG_PATH = './ext_tools/ctags_linux/ctags'

MOJO_PATH = './ext_tools/mojo.jar'
DEPENDS_PATH = './ext_tools/depends-1.0.0.jar'
DEPENDS_PUB_PATH = './ext_tools/depends-0.9.7.jar'
DEPENDS_TIMEOUT_SEC = 120000

DISABLE_CACHE = False


SUPPORTED_FILE_TYPES = (
    '.c', '.h', # c
    '.cpp', '.hpp', '.cxx', '.hxx', '.cc', # cpp
    '.cpp', '.hpp', '.cxx', '.hxx', # c#
    '.java', # java
    '.py', # python
    '.go', # go
    '.php', # php
    '.js', '.jsx', '.ts', '.tsx', # javascript / typescript (frontend)
    '.html', '.css', '.scss', '.sass', # web    
    '.json', '.yml', '.yaml', # config / project files    
    '.md', # documentation
)

## LLM settings

OLLAMA_ENDPOINT = "http://localhost:11434"

# GPT_4_MODEL = 'gpt-4-turbo-2024-04-09'
GPT_4O_MINI_MODEL = 'gpt-4o-mini-2024-07-18'
GPT_4O_MODEL = 'gpt-4o-2024-08-06'
# GPT_35_MODEL = 'gpt-3.5-turbo-0125'
# LLAMA_33_MODEL = 'gpt-3.5-turbo-0125'
LLAMA_33_MODEL = "qwen3-coder:30b"
DS_R1_MODEL = 'DeepSeek-R1'
GPT_41_NANO_MODEL = 'gpt-4.1-nano-2025-04-14'

MODEL2PRICE_PER_TOKEN_PROMPT = {
    # 'gpt-4-turbo-2024-04-09': 2.5/10**6,
    'gpt-4o-2024-08-06': 2.5/10**6,
    'gpt-4o-mini-2024-07-18': 0.15/10**6,
    # 'gpt-3.5-turbo-0125': 0.5/10**6,
    'gpt-4.1-nano-2025-04-14': 0.1/10**6,
    'DeepSeek-R1': 0,
    'llama3.3:70b': 0,
    'qwen3-coder:30b': 0,

}

MODEL2PRICE_PER_TOKEN_RESPONSE = {
    # 'gpt-4-turbo-2024-04-09': 30/10**6,
    'gpt-4o-2024-08-06': 10/10**6,
    'gpt-4o-mini-2024-07-18': 0.6/10**6,
    # 'gpt-3.5-turbo-0125': 1.5/10**6,
    'gpt-4.1-nano-2025-04-14': 0.4/10**6,
    'DeepSeek-R1': 0,
    'llama3.3:70b': 0,
    'qwen3-coder:30b': 0,

}

MODEL2CONTEXT_WINDOW = {
    'gpt-4o-2024-08-06': 128000,
    'gpt-4o-mini-2024-07-18': 128000,
    'gpt-4.1-nano-2025-04-14': 1047576,
    # 'DeepSeek-R1': 120000,
    # 'llama3.3:70b': 120000,
    'qwen3-coder:30b': 32768,
}

## DB settings
MONGO_ADDR = 'mongodb://localhost:27030/'
GPT_MONGO_DB = 'chatgpt'
GPT_MONGO_COLLECTION = 'all_usages'

