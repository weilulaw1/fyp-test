import os
import json
import pickle
import anytree
from anytree import RenderTree
from tqdm import tqdm
import logging
import concurrent.futures

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Assuming the script is run from the root of the project
import sys
sys.path.append('.')

from openai_models import GPTModel
from utils.mytree import ModuleNode
from settings import SUPPORTED_FILE_TYPES, LLAMA_33_MODEL


class SimpleFileNode:
    """A simple node to represent a file, replacing the need for FileTree."""
    def __init__(self, path):
        self._path = path
        self.name = os.path.basename(path)
        self.summary = None
        self.functions = [] # To store function summaries

    def get_full_path(self):
        return self._path

def summarize_file_and_functions(file_path, model, seed=0):
    """
    Summarizes a file and all its functions in a single LLM call.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None, None

    json_structure = '''
{
  "file_summary": "A one-sentence summary of the file.",
  "functions": [
    {
      "name": "function_name_1",
      "summary": "A one-sentence summary of function_name_1."
    }
  ]
}
'''
    prompt = (
        "Analyze the following code file. Your task is to:\n"
        "1. Provide a one-sentence summary of the file's overall functionality.\n"
        "2. For each function implementation in the code, provide its name and a one-sentence summary.\n\n"
        "Respond in a single JSON object with the exact structure below. The 'functions' list should contain an object for each function found.\n"
        f"{json_structure}\n\n"
        f"File: {os.path.basename(file_path)}\n\n"
        f"Code:\\n{content}"
    )

    result_json_str = model.ask(prompt, seed=seed, response_json=True)
    
    file_summary = None
    function_summaries = []

    try:
        data = json.loads(result_json_str)
        if isinstance(data, dict):
            file_summary = data.get('file_summary')
            function_summaries = data.get('functions', [])
            if not isinstance(function_summaries, list):
                function_summaries = []
    except (json.JSONDecodeError, TypeError):
        logging.error(f"Failed to decode combined summary for {file_path}. Response: {result_json_str}")

    return file_summary, function_summaries

def create_module_tree_from_paths(paths):
    """
    Creates a ModuleNode tree directly from a list of file paths.
    """
    root = ModuleNode("")  # Root node, name will be replaced by project name
    file_nodes = {path: SimpleFileNode(path) for path in paths}

    for path in sorted(paths):
        parts = path.split('/')
        current_node = root
        # Traverse/create directory nodes
        for part in parts[:-1]:
            child_node = next((child for child in current_node.children if child.name == part), None)
            if not child_node:
                child_node = ModuleNode(part, parent=current_node)
            current_node = child_node
        
        # Add file to the leaf directory node
        current_node.add_file(file_nodes[path])
    
    return root, file_nodes


def summarize_module(module, model, seed=0, use_ground_truth_name=False):
    """
    Summarizes a module, either a leaf (with files) or a higher-level module (with submodules).
    If use_ground_truth_name is True, it uses the module's existing name and only asks for a summary.
    """
    if use_ground_truth_name:
        prompt_base = f"The module is named '{module.name}'. Summarize its functionality in one sentence. You should answer in JSON format with the key 'Summary'."
    else:
        prompt_base = "Summarize the following software module's functionality in one sentence. Also give a name to the module to reflect its domain and functionality. You should answer in JSON format with the keys 'Summary' and 'Name'."

    if module.is_leaf:
        # It's a leaf module with files
        all_file_summaries = "\\n\\n".join([f"{file.get_full_path()}:\\n{file.summary}" for file in module.get_sorted_files()])
        
        prompt_summarize_module = prompt_base
        prompt_summarize_module += f"\\n\\nFiles in the module: {', '.join([file.get_full_path() for file in module.get_sorted_files()])}"
        prompt_summarize_module += f"\\n\\nFiles Summaries: \\n{all_file_summaries}"
        log_context = "leaf module"
    else:
        # It's a higher-level module with submodules
        all_submodule_summaries = "\\n\\n".join([f"{submodule.name}: {getattr(submodule, 'summary', 'No summary available.')}" for submodule in module.children])
        prompt_summarize_module = f"{prompt_base}\\n\\nSubmodules in this module:\\n\\n{all_submodule_summaries}"
        log_context = "higher module"

    result_module_summary = model.ask(prompt_summarize_module, seed=seed, response_json=True)
    try:
        module_summary = json.loads(result_module_summary)
        if not use_ground_truth_name:
            module.name = module_summary.get('Name', module.name)
        module.summary = module_summary.get('Summary', '')
    except json.JSONDecodeError:
        logging.error(f"Failed to decode JSON for {log_context} summary: {result_module_summary}")
        module.summary = "Summary not available due to formatting error."


def summarize_project(project_path, gpt_type=LLAMA_33_MODEL, use_cache=True, seed=0, use_ground_truth_module_names=True):
    """
    Generates a hierarchical summary of a project based on its folder structure.
    """
    project_name = os.path.basename(project_path)
    logging.info(f"Starting summarization for project: {project_name}")

    # 1. Find all relevant files except for excluded dirs
    EXCLUDED_DIRS = {
    ".venv", "venv", "env",
    "node_modules",
    "__pycache__",
    ".git",
    ".idea", ".vscode",
    "dist", "build", "out",
    ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "site-packages",
    }
    all_files = []
    for root, dirs, files in os.walk(project_path):

        # prune dirs in-place so os.walk won't descend into them
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            if any(file.endswith(ext) for ext in SUPPORTED_FILE_TYPES):
                full_path = os.path.join(root, file)
                # We need relative paths from the project root
                relative_path = os.path.relpath(full_path, project_path)
                all_files.append(relative_path.replace('\\', '/'))

    logging.info(f"Found {len(all_files)} files to process.")

    # 2. Create module tree directly from file paths
    module_root, filename2file = create_module_tree_from_paths(all_files)
    
    # Add project name to root
    module_root.name = project_name
    
    # 3. Summarize all files
    logging.info("Summarizing individual files...")
    
    # The filename2file map is now directly available from create_module_tree_from_paths
    
    # Create absolute paths for summarization function
    files_to_summarize_abs = [os.path.join(project_path, f) for f in filename2file.keys()]

    summary_cache_path = f'data/cache/file_summaries/{project_name}_file_summaries.pkl'
    if use_cache and os.path.exists(summary_cache_path):
        with open(summary_cache_path, 'rb') as f:
            filename2summary = pickle.load(f)
    else:
        filename2summary = {}

    files_needing_summary_abs = []
    for f_rel, f_abs in zip(filename2file.keys(), files_to_summarize_abs):
        if f_rel not in filename2summary:
            files_needing_summary_abs.append(f_abs)
        else:
            # Load from cache
            cached_data = filename2summary[f_rel]
            filename2file[f_rel].summary = cached_data.get('summary')
            filename2file[f_rel].functions = cached_data.get('functions', [])

    if files_needing_summary_abs:
        logging.info(f"Summarizing {len(files_needing_summary_abs)} new files using multithreading.")
        model = GPTModel(model=gpt_type, use_cache=use_cache)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_f_abs = {executor.submit(summarize_file_and_functions, f_abs, model, seed=seed): f_abs for f_abs in files_needing_summary_abs}

            for future in tqdm(concurrent.futures.as_completed(future_to_f_abs), total=len(files_needing_summary_abs), desc="Summarizing files"):
                f_abs = future_to_f_abs[future]
                try:
                    file_summary, function_summaries = future.result()
                    
                    if file_summary is not None:
                        f_rel = os.path.relpath(f_abs, project_path).replace('\\', '/')
                        filename2file[f_rel].summary = file_summary
                        filename2file[f_rel].functions = function_summaries
                        # Update cache
                        filename2summary[f_rel] = {'summary': file_summary, 'functions': function_summaries}
                except Exception as exc:
                    logging.error(f"'{f_abs}' generated an exception: {exc}")

        os.makedirs(os.path.dirname(summary_cache_path), exist_ok=True)
        with open(summary_cache_path, 'wb') as f:
            pickle.dump(filename2summary, f)
    else:
        logging.info("All file summaries loaded from cache.")

    # 4. Summarize modules hierarchically (bottom-up)
    logging.info("Summarizing modules hierarchically...")
    model = GPTModel(model=gpt_type, use_cache=use_cache)
    
    for module in tqdm(anytree.PostOrderIter(module_root), desc="Summarizing modules", total=len(list(anytree.PostOrderIter(module_root)))-1):
        if module.is_root:
            continue
        summarize_module(module, model, seed=seed, use_ground_truth_name=use_ground_truth_module_names)

    # 5. Summarize the root of the project
    logging.info("Summarizing project root...")
    
    prompt_base = f"The project is named '{project_name}'. Summarize the software project based on the summaries of its modules. You should answer in JSON format with the key 'Summary'."
    all_submodule_summaries = "\\n\\n".join([f"{submodule.name}: {getattr(submodule, 'summary', 'No summary available.')}" for submodule in module_root.children])
    prompt_summarize_root = f"{prompt_base}\\n\\nModules in this project:\\n\\n{all_submodule_summaries}"
    
    result_root_summary = model.ask(prompt_summarize_root, seed=seed, response_json=True)
    try:
        root_summary = json.loads(result_root_summary)
        module_root.summary = root_summary.get('Summary', '')
    except json.JSONDecodeError:
        logging.error(f"Failed to decode JSON for project root summary: {result_root_summary}")
        module_root.summary = "Project summary not available due to formatting error."

    logging.info("Project summarization complete.")
    return module_root

def node_to_dict(node):
    """
    Recursively converts a ModuleNode to a dictionary for JSON serialization.
    """
    result = {
        'name': getattr(node, 'name', 'Unnamed'),
        'summary': getattr(node, 'summary', '')
    }
    if node.is_leaf:
        # For leaf modules, add file details
        files_data = []
        for f in node.get_sorted_files():
            file_info = {
                'path': f.get_full_path(), 
                'summary': getattr(f, 'summary', '')
            }
            functions = getattr(f, 'functions', [])
            if functions:
                file_info['functions'] = functions
            files_data.append(file_info)
        result['files'] = files_data
    
    children = [node_to_dict(child) for child in node.children]
    if children:
        result['children'] = children
        
    return result

def main():
    projects_dir = 'data/projects'
    output_dir = 'data/summaries'
    os.makedirs(output_dir, exist_ok=True)

    projects = [d for d in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, d))]

    for project_name in projects:
        project_path = os.path.join(projects_dir, project_name)
        summary_tree = summarize_project(
            project_path,
            gpt_type=LLAMA_33_MODEL,
            use_ground_truth_module_names=False,
            use_cache=True,
            seed=0
            )

        # Print to console
        print("\\n" + "="*80)
        print(f"Hierarchical Summary for {project_name}")
        print("="*80)
        for pre, _, node in RenderTree(summary_tree):
            summary = getattr(node, 'summary', '')
            if node.is_leaf:
                 print(f"{pre}{node.name} ({len(node.files)} files)")
                 if summary:
                     print(f"{pre}  └── Summary: {summary}")
            else:
                print(f"{pre}{node.name}")
                if summary:
                    print(f"{pre}  └── Summary: {summary}")
        print(f"Price: {GPTModel.static_gpt_price:.6f}")
        # Save to JSON file
        summary_file_path = os.path.join(output_dir, f"{project_name}_summary.json")
        summary_dict = node_to_dict(summary_tree)
        with open(summary_file_path, 'w', encoding='utf-8') as f:
            json.dump(summary_dict, f, indent=4, ensure_ascii=False)
        logging.info(f"Summary for {project_name} saved to {summary_file_path}")

if __name__ == "__main__":
    main() 