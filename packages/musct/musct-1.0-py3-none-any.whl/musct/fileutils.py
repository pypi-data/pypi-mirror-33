import hashlib
import os
import subprocess


def is_executable(exepath: str) -> bool:
    dirpath, name = os.path.split(exepath)
    if dirpath:
        abspath = os.path.abspath(os.path.expanduser(exepath))
        if os.path.isfile(abspath) and os.access(abspath, os.X_OK):
            return True
    for path in os.environ.get("PATH").split(os.pathsep):
        abspath = os.path.join(path, name)
        if os.path.isfile(abspath) and os.access(abspath, os.X_OK):
            return True
    return False


def is_executable_in(exepath: str, exec_packages: list) -> bool:
    if exec_packages:
        dirname, basename = os.path.split(exepath)
        for package in exec_packages:
            new_dirpath = package.path
            abspath = os.path.join(new_dirpath, basename)
            if os.path.isfile(abspath) and os.access(abspath, os.X_OK):
                return True
    return False


def md5sum(path) -> str:
    with open(path, 'rb') as inf:
        return hashlib.md5(inf.read()).hexdigest()


def find_conflicting(dest_path, source_path, include_missing=False) -> dict:
    if os.path.isfile(source_path) and os.path.isfile(dest_path) and md5sum(source_path) == md5sum(dest_path):
        return {}
    elif os.path.isdir(source_path) and os.path.isdir(dest_path):
        conflicts = {}
        for path in os.listdir(source_path):
            dest_child = os.path.join(dest_path, path)
            source_child = os.path.join(source_path, path)
            conflicts_child = find_conflicting(dest_child, source_child)
            conflicts.update(conflicts_child)
        return conflicts
    elif os.path.exists(dest_path):
        return {dest_path: source_path}
    elif include_missing:
        return {dest_path: source_path}
    return {}


def copy_as_root(files: dict):
    args = []
    for dest, source in files.items():
        args.append(source)
        args.append(dest)
    root_script = os.path.join(os.path.abspath(os.path.dirname(__file__)), "root.py")
    cp_cmd = [
        "sudo",
        os.path.join("usr", "bin", "env"),
        "python3",
        root_script,
        "copy"
    ]
    cp_cmd.extend(args)
    copy = subprocess.run(cp_cmd)
    return copy.returncode


def run_as_root(scripts: list):
    root_script = os.path.join(os.path.abspath(os.path.dirname(__file__)), "root.py")
    rs_cmd = [
        "sudo",
        os.path.join("usr", "bin", "env"),
        "python3",
        root_script,
        "run"
    ]
    rs_cmd.extend(scripts)
    runscript = subprocess.run(rs_cmd)
    return runscript.returncode
