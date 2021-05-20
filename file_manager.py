import os

# Directiory management

def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def read_file(path):
    with open(path, 'rb') as file: 
            file_content = file.read() 
    return file_content

def write_to_file(path,file_content):
    with open(path, 'wb') as file: 
            file.write(file_content)