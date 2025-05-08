import os
import zipfile
import datetime
import shutil

def create_zipfile():
    # Get current date for zip file name
    current_date = datetime.datetime.now().strftime('%Y%m%d')
    zip_filename = f'quiz-master-app.zip'
    
    # Create a temporary directory for source_code
    source_code_dir = 'source_code'
    if os.path.exists(source_code_dir):
        shutil.rmtree(source_code_dir)
    os.makedirs(source_code_dir, exist_ok=True)
    
    # Directories and files to copy to source_code
    source_dirs = ['app']
    source_files = [
        'create_db.py',
        'README.md',
        'requirements.txt',
        'run.py',
        'SwaggerFile.json'
    ]
    
    # Patterns to exclude
    exclude_patterns = [
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.db',
        '*.sqlite',
        '.git',
        '.gitignore',
        '.DS_Store',
        'venv',
        'env',
        '*.zip'
    ]
    
    def should_exclude(filepath):
        # Check if the file matches any exclude pattern
        for pattern in exclude_patterns:
            if pattern.startswith('*.'):
                ext = pattern[1:]  # Get extension
                if filepath.endswith(ext):
                    return True
            elif pattern in filepath:
                return True
        return False
    
    try:
        # Copy individual files to source_code
        for file in source_files:
            if os.path.exists(file) and not should_exclude(file):
                print(f"Copying file: {file} to {source_code_dir}")
                shutil.copy2(file, os.path.join(source_code_dir, file))
        
        # Copy directories to source_code
        for directory in source_dirs:
            if os.path.exists(directory):
                dest_dir = os.path.join(source_code_dir, directory)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir, exist_ok=True)
                
                for root, dirs, files in os.walk(directory):
                    # Skip excluded directories
                    dirs[:] = [d for d in dirs if not should_exclude(d)]
                    
                    for file in files:
                        src_path = os.path.join(root, file)
                        if not should_exclude(src_path):
                            # Calculate relative path
                            rel_path = os.path.relpath(src_path, directory)
                            dest_path = os.path.join(dest_dir, rel_path)
                            
                            # Create subdirectories if they don't exist
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                            
                            print(f"Copying: {src_path} to {dest_path}")
                            shutil.copy2(src_path, dest_path)
        
        # Create a fresh instance directory in source_code
        instance_dir = os.path.join(source_code_dir, 'instance')
        if not os.path.exists(instance_dir):
            os.makedirs(instance_dir, exist_ok=True)
            print(f"Created empty instance directory in {source_code_dir}")
        
        # Create zip file
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add check.py to the root of the zip
            if os.path.exists('check.py'):
                print("Adding file: check.py")
                zipf.write('check.py')
            else:
                print("Warning: check.py not found!")
            
            # Add the entire source_code directory
            for root, dirs, files in os.walk(source_code_dir):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not should_exclude(d)]
                
                for file in files:
                    filepath = os.path.join(root, file)
                    if not should_exclude(filepath):
                        # Add file to zip, preserving directory structure
                        print(f"Adding to zip: {filepath}")
                        zipf.write(filepath)
        
        print(f"\nZip file created: {zip_filename}")
        print(f"Size: {os.path.getsize(zip_filename) / (1024 * 1024):.2f} MB")
        
    finally:
        # Clean up: remove temporary source_code directory
        if os.path.exists(source_code_dir):
            print(f"Cleaning up: Removing temporary {source_code_dir} directory")
            shutil.rmtree(source_code_dir)

if __name__ == "__main__":
    create_zipfile() 