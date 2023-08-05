# Epistle

__epistle /ɪˈpɪs(ə)l/ **noun**__ *formal, humourous* - A letter.

![Danny](danny.png)

Take notes using Vim. Save them in a remote git repository.  This supports sharing notes across devices.

Can be configured to use a private (or public) gist.

## Requirements

* Python 3.6
* Vim
* Git

Both Vim and Git must be in your `PATH`.

## Installation

Via PyPI

    $ pip install epistle

Or, clone this repo and run pip install directly:

    $ git clone git@github.com:msharp/epistle.git
    $ pip install epistle/

## Usage
  
Epistle is a command-line tool.

To create a new note:

    $ epistle new my_note

This will open Vim, where you can compose the note.  After you exit Vim, the note will be saved, added to the repo and pushed to the remote.

The following commands are available:

* __list__    List available Epistles
* __view__    View the contents of an Epistle
* __new__     Create a new Epistle
* __edit__    Edit an Epistle
* __rename__  Rename an Epistle
* __delete__  Delete an Epistle
* __git__     Run `push` or `pull` to the remote Git repository

When you first run the `epsitle` command, it will discover your Vim and ask for the clone URL of the remote repository you want to use.  
It will then clone this repository and store the URL in its config.
