import subprocess
import os

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def get_git_tag():
    try:
        return subprocess.check_output(['git', 'describe', '--exact-match', 'HEAD']).strip()
    except subprocess.CalledProcessError,e:
        return "(no tag)"

def get_git_branch():
    branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
    if branch == "HEAD":
        return "(no branch)"
    else:
        return branch

def get_git_revision_hash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()

def get_version_info(mongo_path):
    version_info = {}
    with cd(mongo_path):
        version_info['branch'] = get_git_branch()
    with cd(mongo_path):
        version_info['hash'] = get_git_revision_hash()
    with cd(mongo_path):
        version_info['tag'] = get_git_tag()
    return version_info
