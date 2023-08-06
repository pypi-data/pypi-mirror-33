import os
from importlib import util

class Reqtxt:
    def __init__(self, project_path):
        self.project_path = project_path.replace('/', '\\')
        self.paths = []
        self.modules = set()
        self.get_structure(self.project_path)
        self.get_imports()
        self.create_file()
    
    def get_structure(self, directory):
        for dirname, dirnames, filenames in os.walk(directory):
            for subdirname in dirnames:
                self.paths.append(os.path.join(dirname, subdirname))
            for filename in filenames:
                self.paths.append(os.path.join(dirname, filename))
    
    def get_imports(self):
        for path in self.paths:
            if self.is_python_file(path):
                with open(path, 'r') as f:
                    for line in f.readlines():
                        line = line.strip()
                        if 'import' in line.split(' '):
                            if not self.is_comment(line):
                                self.get_modules(line)
    
    def get_modules(self, line):
        line = line.replace('import', '').replace('from', '').replace('*', '').strip()
        line_arr = line.split(' ')
        module = module = line_arr[0]
        if '.' in line_arr[0]:
            module = line_arr[0].split('.')[0]
        
        if self.check_module(module):
            self.modules.add(module)
    
    def check_module(self, module):
        return util.find_spec(module) != None
    
    def is_comment(self, line):
        return line.split(' ')[0] == '#' or line[0] == '#' or '"' in line
    
    def is_python_file(self, path):
        return os.path.isfile(path) and path.split('.')[-1] == 'py'
    
    def create_file(self):
        with open(os.path.join(self.project_path, 'requirements.txt'), 'a+') as f:
            for module in self.modules:
                f.write(module + '\n')