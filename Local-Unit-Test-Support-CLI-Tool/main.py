import os
import logging
from pathlib import Path
import argparse
from typing import List, Dict, Set, Tuple
import json
import faiss

from diff_extractor import GitDiffExtractor
from ast_parser import analyze_ast_diff, extract_code_blocks, extract_call_graph, expand_calls
from rag_retrieval import get_code_files, get_embedding, save_to_faiss
# from rag_augmentation import augment_coverage_suggestion_prompt, augment_test_suggestion_prompt
from rag_generation import GeminiSuggester
from report_formatter import generate_suggestion_markdown

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_existing_index(index_path: str = "index.faiss", meta_path: str = "metadata.json") -> Tuple[Dict, bool]:
    """Load existing FAISS index and metadata if available."""
    if os.path.exists(index_path) and os.path.exists(meta_path):
        try:
            # Load metadata
            with open(meta_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Convert metadata list to dictionary format
            code_blocks = {}
            for item in metadata:
                key = (item['file_path'], item['symbol_name'])
                code_blocks[key] = {
                    'symbol_type': item['symbol_type'],
                    'symbol_name': item['symbol_name'],
                    'file_path': item['file_path'],
                    'code': item['code']
                }
            
            logger.info(f"Loaded existing index with {len(code_blocks)} code blocks")
            return code_blocks, True
        except Exception as e:
            logger.error(f"Error loading existing index: {str(e)}")
            return {}, False
    return {}, False

def process_code_files(repo_path: str) -> Dict:
    """Process all code files in the repository and create embeddings."""
    # Try to load existing index first
    code_blocks, index_exists = load_existing_index()
    if index_exists:
        return code_blocks

    logger.info("Processing code files")
    code_files = get_code_files(repo_path)
    logger.debug(f"Found {len(code_files)} code files")
    
    code_blocks = {}
    for file in code_files:
        code_block = extract_code_blocks(file, repo_path)
        if code_block:  # Only update if we got valid blocks
            code_blocks.update(code_block)
    
    logger.debug(f"Extracted {len(code_blocks)} code blocks")
    
    if not code_blocks:
        logger.error("No code blocks were extracted from the repository")
        raise ValueError("No code blocks found in repository")

    # Create embeddings
    logger.info("Creating embeddings")
    embeddings = []
    for block in code_blocks.values():
        try:
            embedding = get_embedding(block["code"])
            embeddings.append(embedding)
        except Exception as e:
            logger.error(f"Failed to get embedding for block {block['symbol_name']}: {str(e)}")
            continue
            
    if not embeddings:
        logger.error("No embeddings were created")
        raise ValueError("Failed to create any embeddings")
        
    logger.debug(f"Created {len(embeddings)} embeddings")
    save_to_faiss(embeddings, code_blocks)
    
    return code_blocks

def analyze_changed_files(git_diff_extractor: GitDiffExtractor) -> Tuple[Dict[str, Dict], List[str], str]:
    """Analyze changed files and collect git diff messages."""
    logger.info("Processing changed files")
    changed_files = git_diff_extractor.get_changed_files()
    logger.debug(f"Found {len(changed_files)} changed files")
    
    changed_functions = {}
    git_diff_message_list = []
    
    for file in changed_files:
        # Skip test files, non-Python files, and Local-Unit-Test-Support files
        if ("test_" in file or "_test" in file or 
            not file.endswith(".py") or 
            "Local-Unit-Test-Support" in file):
            continue

        before_code = git_diff_extractor.load_file_from_previous_commit(file, git_diff_extractor.from_commit)
        after_code = git_diff_extractor.load_file_from_previous_commit(file, git_diff_extractor.to_commit)
        changes = analyze_ast_diff(before_code, after_code)
        changed_functions[file] = changes
        git_diff_message = git_diff_extractor.get_diff(file)
        git_diff_message_list.append(git_diff_message)

    whole_git_diff = "\n".join(git_diff_message_list)
    all_changed = []
    for file, changes in changed_functions.items():
        all_changed.extend(
            changes.get("added", []) +
            changes.get("removed", []) +
            changes.get("modified", []) +
            changes.get("indirect_dependents", [])
        )
    
    logger.debug(f"Found {len(all_changed)} changed functions")
    return changed_functions, all_changed, whole_git_diff

def process_test_files(repo_path: str, all_changed: List[str], code_blocks: Dict) -> Tuple[List[Dict], str]:
    """Process test files and find affected test functions."""
    logger.info("Processing test files")
    test_files_processed = 0
    affected_metadata_list = []
    whole_test_code = ""
    
    for root, _, files in os.walk(repo_path):
        for filename in files:
            if ("test_" in filename or "_test" in filename) and filename.endswith(".py"):
                test_path = os.path.join(root, filename)
                logger.info(f"Processing test file: {test_path}")
                relative_path = str(Path(test_path).relative_to(Path(repo_path)))
                if "Local-Unit-Test-Support" in relative_path:
                    continue
                try:
                    with open(test_path, "r") as tf:
                        test_code = tf.read()
                        call_map = extract_call_graph(test_code)
                        test_func2call_func = expand_calls(call_map)
                        filename_code = relative_path + "\n" + test_code
                        affected_test_function = [
                            k for k, v in test_func2call_func.items() 
                            if any(func in all_changed for func in v)
                        ]
                        path_funcname_pair = [(relative_path, func_name) for func_name in affected_test_function]
                        affected_metadata = [code_blocks[k] for k in path_funcname_pair if k in code_blocks]
                        affected_metadata_list.extend(affected_metadata)
                        whole_test_code += filename_code + "\n"
                        test_files_processed += 1
                except Exception as e:
                    logger.error(f"Error processing test file {test_path}: {str(e)}")
                    continue

    logger.debug(f"Processed {test_files_processed} test files")
    logger.debug(f"Found {len(affected_metadata_list)} affected test functions")
    return affected_metadata_list, whole_test_code

def generate_report(affected_metadata_list: List[Dict], whole_test_code: str, whole_git_diff: str, output_filename: str) -> None:
    """Generate and save the test maintenance report."""
    logger.info("Generating suggestions")
    gemini_suggester = GeminiSuggester()
    suggestions = gemini_suggester.get_test_suggestions(
        affected_metadata_list, 
        whole_test_code, 
        whole_git_diff
    )

    if suggestions:
        report = generate_suggestion_markdown(suggestions)
        report_path = os.path.join(os.path.dirname(__file__), output_filename)
        with open(report_path, "w") as f:
            f.write("# Test Maintenance Report\n\n")
            f.write("This report generates suggestions for updating your unit tests based on file changes. \n")
            f.write(report)
        logger.info(f"Report generated successfully at {report_path}")
    else:
        logger.info("No suggestions generated")

def main(repo_url: str, from_commit: str, to_commit: str, keep_repo: bool, output_filename: str):
    """Main function to analyze repository changes and generate test suggestions."""
    try:
        output_filename += ".md"
        
        # Initialize git diff extractor
        logger.info(f"Initializing GitDiffExtractor for {repo_url}")
        git_diff_extractor = GitDiffExtractor(repo_url, from_commit, to_commit, keep_repo)
        repo_path = git_diff_extractor.repo_path

        # Process code files and create embeddings
        code_blocks = process_code_files(repo_path)
        
        # Analyze changed files
        _, all_changed, whole_git_diff = analyze_changed_files(git_diff_extractor)
        
        # Process test files
        affected_metadata_list, whole_test_code = process_test_files(repo_path, all_changed, code_blocks)
        
        # Generate report
        generate_report(affected_metadata_list, whole_test_code, whole_git_diff, output_filename)

    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze repository changes and generate test suggestions")
    parser.add_argument("repo_url", help="GitHub repository URL")
    parser.add_argument("--from", dest="from_commit", default="HEAD^", help="Base commit (default: HEAD^)")
    parser.add_argument("--to", dest="to_commit", default="HEAD", help="Target commit (default: HEAD)")
    parser.add_argument("--keep", action="store_true", help="Keep cloned repo after diff (default: delete)")
    parser.add_argument("--output", default="report", help="Output filename without extension (default: report)")
    
    args = parser.parse_args()
    
    main(args.repo_url, args.from_commit, args.to_commit, args.keep, args.output) 