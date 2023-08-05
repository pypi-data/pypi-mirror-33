import os
import subprocess
import configparser


class Git():
    def __init__(self, directory, remote):
        self.directory = directory
        self.remote = remote

    def clone(self): 
        os.system(f"git clone {self.remote} {self.directory}")

    def pull(self):
        self._cd_and_git("pull")

    def push(self):
        self._cd_and_git("push")

    def add(self, name):
        self._cd_and_git(f"add {name}")

    def commit(self, msg):
        self._cd_and_git(f"commit -m '{msg}'")

    def rename(self, name, new_name):
        self._cd_and_git(f"mv {name} {new_name}")

    def delete(self, name):
        self._cd_and_git(f"rm {name}")

    def _cd_and_git(self, rest):
        os.system(f"cd {self.directory} && git {rest}")

