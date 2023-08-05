import os
import subprocess
import configparser
from pathlib import Path
from datetime import datetime

import click
from epistle.git import Git


class Epistle():

    EPISTLE_DIR = os.path.join(os.path.expanduser('~'), ".epistle")
    EPISTLE_CFG = os.path.join(EPISTLE_DIR, "epistle.cfg")
    EPISTLES_DIR = os.path.join(EPISTLE_DIR, "epistles")

    def __init__(self):
        self.ensure_files()
        self.read_config()

        self.ensure_git()
        self.ensure_vim()

        _eps = Path(self.EPISTLES_DIR)
        if not _eps.is_dir(): 
            self.git.clone()

    def ensure_files(self):
        _dir = Path(self.EPISTLE_DIR)
        _cfg = Path(self.EPISTLE_CFG)
        if not _dir.is_dir(): _dir.mkdir
        if not _cfg.is_file(): _cfg.touch()

    def read_config(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.EPISTLE_CFG)

        try:
            self.config.add_section("Epistle")
        except configparser.DuplicateSectionError:
            pass

        try:
            self.config.add_section("Git")
        except configparser.DuplicateSectionError:
            pass
    
    def save_config(self):
        with open(self.EPISTLE_CFG, 'w') as configfile:
            self.config.write(configfile)

    def epistle_path(self, name):
        return os.path.join(self.EPISTLES_DIR, name)

    def exists(self, name):
        return Path(self.epistle_path(name)).is_file()

    def ensure_vim(self):
        try:
            self.vim = self.config.get("Epistle", "Vim")
        except configparser.NoOptionError:
            v = subprocess.check_output(['which vim'], shell=True)
            self.vim = v.decode('utf8').strip()
            self.config.set("Epistle", "Vim", self.vim)
            self.save_config()

    def ensure_git(self):
        try:
            remote = self.config.get("Git", "Remote")
            self.git = Git(self.EPISTLES_DIR, remote)
        except configparser.NoOptionError:
            remote = click.prompt('Enter your git clone URL', type=str)

            self.config.set("Git", "Remote", remote)
            self.save_config()

            click.echo(f"Cloning {remote} into {self.EPISTLES_DIR}")
            self.git = Git(self.EPISTLES_DIR, remote)
            self.git.clone

    def list(self):
        click.echo(click.style("Available Epistles\n--------------", fg="green"))

        epistles = [ f for f in os.listdir(self.EPISTLES_DIR) if os.path.isfile(os.path.join(self.EPISTLES_DIR, f))]
        for e in epistles:
            click.echo(e)

        click.echo(click.style("--------------", fg="green"))

    def view(self, name):
        os.system(f"cat {self.epistle_path(name)}")

    def edit(self, name):
        self.git.pull()

        if self.exists(name):
            self._compose_epistle(name)
        else:
            click.echo(click.style(f"No such Epistle!", fg="yellow"))

    def new(self, name):
        self.git.pull()

        if self.exists(name):
            click.echo(click.style(f"This Epistle already exists!", fg="yellow"))
        else:
            os.system(f"touch {self.epistle_path(name)}")  # make the file
            self._compose_epistle(name)

    def _compose_epistle(self, name):
        click.echo(f"Using vim from: {self.vim}")

        epistle = self.epistle_path(name)
        click.echo(f"Got epistle file: {epistle}")

        # launch vim and wait for exit code
        subprocess.check_call([self.vim, epistle])

        # add and commit the changes.
        self.git.add(epistle)
        self.git.commit(f"epistle:{datetime.now().strftime('%Y%m%d%H%m')}")
        self.git.push()


