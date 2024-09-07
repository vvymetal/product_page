import os
import json
import fnmatch
from pathlib import Path

def load_gitignore(project_path):
    gitignore_path = os.path.join(project_path, '.gitignore')
    ignore_patterns = [
        'venv/', '*.pyc', '__pycache__/', '.env',
        '*.log', '.idea/', '.vscode/', '*.egg-info/',
        '.git/'  # Přidáno ignorování složky .git
    ]
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    ignore_patterns.append(line)
    return ignore_patterns

def should_ignore(path, ignore_patterns, project_path):
    rel_path = os.path.relpath(path, project_path)
    for pattern in ignore_patterns:
        if pattern.endswith('/') and os.path.isdir(path):
            if fnmatch.fnmatch(rel_path + '/', pattern):
                return True
        elif fnmatch.fnmatch(rel_path, pattern):
            return True
    return False

def extract_project_files(project_path):
    file_contents = {}
    ignore_patterns = load_gitignore(project_path)
    
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), ignore_patterns, project_path)]
        for file in files:
            file_path = os.path.join(root, file)
            if not should_ignore(file_path, ignore_patterns, project_path):
                relative_path = os.path.relpath(file_path, project_path)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        file_contents[relative_path] = content
                except UnicodeDecodeError:
                    pass  # Tiché přeskočení binárních souborů
    
    return file_contents

def save_project_files(file_contents, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(file_contents, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    project_path = os.getcwd()
    output_file = "project_files.json"
    
    file_contents = extract_project_files(project_path)
    save_project_files(file_contents, output_file)
    
    print(f"Project files saved to {output_file}")