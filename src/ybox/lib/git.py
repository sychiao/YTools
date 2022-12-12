import subprocess
import time
import sys
import re
import threading
from rich.progress import Progress
from collections.abc import Sequence

class HomoList(Sequence):
    def __init__(self, lst):
        self._lst = lst
        self._type = type(lst[0])
    
    def __getattr__(self, key):
      if callable(getattr(self._type, key, None)):
        def map_func(*args, **kwargs):
            return HomoList([getattr(e, key)(*args, **kwargs) for e in self._lst])
        return map_func
      else:
        return HomoList([getattr(e, key) for e in self._lst])

    def __getitem__(self, item):
        return self._lst[item]

    def __len__(self):
        return len(self._lst)

    def __iter__(self):
        return iter(self._lst)

class GitRepo:
    progress = Progress()
    repos = list()

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.completed = 0
        self.task_bar = None
        self.task = None
        #GitRepo.repos.append(repos)
    
    def add_progress_bar(self, progress):
        self.task_bar = progress.add_task(f"[green]{self.name}...", total=100)

    @staticmethod
    def clone_all(repos):
        repos = HomoList(repos)
        repos.clone_task().start()
        
        with Progress() as progress:
            repos.add_progress_bar(progress)

            while not all(repos.done(progress)):
                repos.update(progress)

    def clone(self):
        proc = subprocess.Popen(f"git clone {self.url} --progress",
        shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True)

        while proc.poll() is None:
            nextline = proc.stderr.readline()
            if match := re.match("Receiving objects: +(\d+)% .+", nextline):
                self.completed = int(match.group(1))
        proc.wait()

    def clone_task(self):
        self.task = threading.Thread(target = GitRepo.clone, args = (self,))
        return self.task
    
    def update(self, progress):
        progress.update(self.task_bar, completed=self.completed)
    
    def done(self, progress):
        if ret := not self.task.is_alive():
            progress.update(self.task_bar, completed=100)
        return ret

cmd1 = "https://github.com/32bitmicro/riscv-compiler-rt.git"
cmd2 = "https://github.com/gitpython-developers/GitPython.git"

repo1 = GitRepo("riscv-compiler-rt", cmd1)
repo2 = GitRepo("GitPython", cmd2)
GitRepo.clone_all([repo1, repo2])

print("Done.")
