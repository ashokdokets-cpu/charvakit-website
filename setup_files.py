import os 
 
def create_file(filepath, content): 
    os.makedirs(os.path.dirname(filepath), exist_ok=True) 
    with open(filepath, 'w', encoding='utf-8') as f: 
        f.write(content) 
    print(f'Created: {filepath}') 
