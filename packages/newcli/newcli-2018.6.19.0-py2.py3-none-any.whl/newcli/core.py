import os
import shutil
from findreplace.core import findreplace

ROOT_DIR = os.path.dirname(__file__)
PROJECT_TEMPLATE_DIR = os.path.join(ROOT_DIR, 'templates', '{{project}}')

def copy_template(source_dir, dest_dir):
    shutil.copytree(source_dir, dest_dir)

def setup_new_project(dest_dir=os.getcwd()):
    config = prompt_config()
    dest_dir = os.path.join(dest_dir, config.get('{{project}}'))
    copy_template(PROJECT_TEMPLATE_DIR, dest_dir)
    findreplace(base_dir=dest_dir, find_replace_dict=config)

def prompt_config():
    config = {}
    config['{{project}}'] = input("Project Name: ")
    config['{{name}}'] = input("Name: ")
    config['{{email}}'] = input("Email: ")
    config['{{github_user}}'] = input("GitHub Username: ")
    config['{{github_repo}}'] = input("GitHub Repository: [https://github.com/{}/{}] ".format(config.get('{{github_user}}'), config.get('{{project}}')))
    config['{{description}}'] = input("Description: ")
    return config
