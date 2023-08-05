#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from os import path, remove, makedirs
from shutil import copy2, copytree, rmtree
from subprocess import run
from sys import argv


def main():
    command = argv[1]
    if command == "run":
        run_script()
    elif command == "copy":
        copy()


def run_script():
    for src in argv[2::]:
        cmd = run(["sudo", "src"])
        if cmd.returncode:
            exit(cmd.returncode)


def copy():
    for i in range(2, len(argv), 2):
        source = argv[i]
        dest = argv[i+1]
        makedirs(path.dirname(dest), exist_ok=True)
        if path.isfile(dest):
            remove(dest)
        elif path.isdir(dest):
            rmtree(dest)
        if path.isfile(source):
            copy2(source, dest)
        elif path.isdir(source):
            copytree(source, dest)


if __name__ == "__main__":
    main()
