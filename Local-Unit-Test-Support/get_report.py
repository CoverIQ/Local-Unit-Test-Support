from pathlib import Path
from diff_parser import GitDiffParser,load_file_from_previous_commit
import argparse
from typing import List
import ast
import faiss
import numpy as np
import json
from dotenv import load_dotenv 
import os
from google import genai
from google.genai.types import EmbedContentConfig
from test_linker import extract_call_graph, expand_calls
from ast_analyzer import analyze_ast_diff
from llm_engine import GeminiSuggester
from reporter import generate_suggestion_markdown

def get_code_files(repo_path: str, include_pattern="*.py", exclude_dirs=["venv", "__pycache__"]) -> List[str]:
    repo = Path(repo_path).resolve()
    code_files = []
    for file in repo.rglob(include_pattern):
        if not any(ex in file.parts for ex in exclude_dirs):
            #relative_path = file.relative_to(repo).as_posix()
            code_files.append(file)
    return code_files

def extract_code_blocks(file_path: Path, repo_path: str):
    repo_path = Path(repo_path)
    code_blocks = {}
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    relative_path = file_path.relative_to(repo_path)
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            block_type = "function" if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else "class"
            name = node.name
            start_line = node.lineno - 1
            end_line = node.end_lineno
            code_chunk = "\n".join(source.splitlines()[start_line:end_line])
            key = (str(relative_path), name)
            code_blocks[key] = {
                "symbol_type": block_type,
                "symbol_name": name,
                "file_path": str(relative_path),
                "code": code_chunk
            }
    return code_blocks

def get_embedding(text: str):
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    response = client.models.embed_content(
        model="text-embedding-004",
        contents=[
            text
        ],
        config=EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
        ),
    )
    return response.embeddings[0].values

def save_to_faiss(embeddings, metadata, save_path="index.faiss", meta_path="metadata.json"):
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))
    faiss.write_index(index, save_path)

    json_metadata = [
        {
            "file_path": key[0],
            "symbol_name": key[1],
            **value
        }
        for key, value in metadata.items()
    ]

    with open("metadata.json", "w", encoding="utf-8") as f:
        json.dump(json_metadata, f, ensure_ascii=False, indent=2)

def main(repo_url, from_commit, to_commit, keep_repo, output_filename):
    output_filename += ".md"
    whole_git_diff = ""
    whole_test_code = ""
    affected_metadata_list = []
    git_diff_message_list = []
    report_path = os.path.join(os.path.dirname(__file__), output_filename)
    git_parser = GitDiffParser(repo_url, from_commit, to_commit, keep_repo)
    repo_path = git_parser.repo_path
    # get all code files
    code_files = get_code_files(repo_path)
    # divide into chunks
    code_blocks = {}
    for file in code_files:
        code_block = extract_code_blocks(file, repo_path)
        code_blocks.update(code_block)
    # create embeddings
    embeddings = [get_embedding(b["code"]) for b in code_blocks.values()]
    # save to vector database
    save_to_faiss(embeddings, code_blocks)
    changed_files = git_parser.get_changed_files()
    changed_functions = {}
    for file in changed_files:
        filename = file.split('/')[-1]
        if "test_" in filename or "_test" in filename or not filename.endswith(".py"):
            continue

        before_code = git_parser.load_file_from_previous_commit(file)
        after_code = load_file_from_previous_commit(repo_path, file, to_commit)
        changes = analyze_ast_diff(before_code, after_code)
        changed_functions[file] = changes
        git_diff_message = git_parser.get_diff(file)
        git_diff_message_list.append(git_diff_message)
    whole_git_diff = "\n".join(git_diff_message_list)
    all_changed = []
    for file, changes in changed_functions.items():
        all_changed = (
            changes.get("added", []) +
            changes.get("removed", []) +
            changes.get("modified", []) +
            changes.get("indirect_dependents", [])
        )
    for root, _, files in os.walk(repo_path):
        for filename in files:
            if ("test_" in filename or "_test" in filename) and filename.endswith(".py"):
                test_path = os.path.join(root, filename)
                print(test_path)
                relative_path = str(Path(test_path).relative_to(Path(repo_path)))
                with open(test_path, "r") as tf:
                    try:
                        test_code = tf.read()
                        call_map = extract_call_graph(test_code)
                        test_func2call_func = expand_calls(call_map)
                        filename_code = relative_path + "\n" + test_code
                        affected_test_function = [k for k, v in test_func2call_func.items() if any(func in all_changed for func in v)]
                        path_funcname_pair = [(relative_path, func_name) for func_name in affected_test_function]
                        affected_metadata = [code_blocks[k] for k in path_funcname_pair if k in code_blocks]
                        affected_metadata_list.extend(affected_metadata)
                        whole_test_code += filename_code + "\n"
                    except Exception as e:
                        print(f"Error parsing {test_path}: {e}")
                        continue
    gemini_suggester = GeminiSuggester()
    suggestions = gemini_suggester.get_test_suggestions(affected_metadata_list, whole_test_code, whole_git_diff)
    if suggestions:
        report = generate_suggestion_markdown(suggestions)
        with open(report_path, "w") as f:
            f.write("# Test Maintenance Report\n\n")
            f.write("This report generates suggestions for updating your unit tests based on file changes. \n")
            f.write(report)
    else:
        print("No suggestions--------------------------------")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show git diff between two commits in a GitHub repo")
    parser.add_argument("repo_url", help="GitHub repository URL")
    parser.add_argument("--from", dest="from_commit", default="HEAD^", help="Base commit (default: HEAD^)")
    parser.add_argument("--to", dest="to_commit", default="HEAD", help="Target commit (default: HEAD)")
    parser.add_argument("--keep",  action="store_true", help="Keep cloned repo after diff (default: delete)")
    parser.add_argument("--output", default="report")
    args = parser.parse_args()
    
    main(args.repo_url, args.from_commit, args.to_commit, args.keep, args.output)