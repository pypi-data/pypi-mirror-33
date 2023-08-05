import os
import shlex

from yaml import YAMLError

import musct.printer
from musct.args import get_argument_settings
from musct.log import logger
from musct.yaml_wrapper import parse_file

# Priority:
# Commandline Arguments
# Settings file
# Default Settings
_DEFAULT_CONFIG = {
    "verbose": False,
    "no_root": False,
    "no_confirm": False,
    "ignore_scripts": False,
    "ignore_msg": False,
    "ignore_missing_files": False,
    "ignore_cmd_check": False,
    "force": False,
    "editor": "vim",
    "editor_flags": "",
    "backup_file": None,
    "tar": "bsdtar",
    "compression_method": "gzip",
    "full": False,
    "command": None,
    "packages": None
}

_CONFIG_FILE_ALLOW = [
    "verbose",
    "no_root",
    "no_confirm",
    "ignore_scripts",
    "ignore_msg",
    "ignore_missing_files",
    "ignore_cmd_check",
    "editor",
    "editor_flags",
    "tar",
    "compression_method",
    "full",
]


class Settings:
    env_vars: dict
    cfg_vars: dict
    rt_vars = {
        "pkg_syntax_errs": None
    }

    def __init__(self):
        self.env_vars = _get_env_vars()
        runtime_flags = get_argument_settings()
        if runtime_flags.get("change_dir"):
            os.chdir(runtime_flags["change_dir"])
        if runtime_flags.get("config"):
            cfg_file = _load_config(runtime_flags["config"])
        else:
            cfg_file = _load_config(os.path.join(self.env_vars["USER_CONFIG_HOME"], "musct", "config"))
        self.cfg_vars = _update_config(cfg_file, runtime_flags)
        _validate_config(self.cfg_vars)

        logger.set_verbose(self.cfg_vars["verbose"])
        musct.printer.no_confirm = self.cfg_vars["no_confirm"]
        logger.print_debug("ENVIRONMENT_VARS: %s" % self.env_vars)
        logger.print_debug("CONFIG_VARS: %s" % self.cfg_vars)


def _get_env_vars() -> dict:
    env_vars = {
        "HOME": os.environ.get("HOME"),
        "USER": os.environ.get("USER")
    }
    env_vars["USER_CONFIG_HOME"] = os.environ.get(
        "XDG_CONFIG_HOME", os.path.join(env_vars["HOME"], ".config"))
    env_vars["USER_CACHE_HOME"] = os.environ.get(
        "XDG_CACHE_HOME", os.path.join(env_vars["HOME"], ".cache"))
    env_vars["USER_DATA_HOME"] = os.environ.get(
        "XDG_DATA_HOME", os.path.join(env_vars["HOME"], ".local", "share"))
    return env_vars


def _load_config(filepath: str):
    dirname = os.path.dirname(filepath)
    try:
        if os.path.isfile(filepath):
            return parse_file(filepath)
        os.makedirs(dirname, exist_ok=True)
        with open(filepath, "w+") as out:
            out.write(_EXAMPLE_CONFIG_FILE)
    except (OSError, IOError) as err:
        logger.print_critical_err(err, status=os.EX_IOERR)
    except YAMLError as err:
        logger.print_yaml_err(filepath, err, should_exit=True)
    return {}


def _find_executable(exepath: str):
    dirname, basename = os.path.split(exepath)
    if dirname:
        abspath = os.path.abspath(os.path.expanduser(exepath))
        if os.path.isfile(abspath) and os.access(abspath, os.X_OK):
            return abspath
    for path in os.environ.get("PATH").split(os.pathsep):
        abspath = os.path.join(path, basename)
        if os.path.isfile(abspath) and os.access(abspath, os.X_OK):
            return abspath
    logger.print_critical_err("cannot run '%s': Not an executable" % exepath, status=os.EX_UNAVAILABLE)


def _update_config(file: dict, flags: dict) -> dict:
    cfg_vars = _DEFAULT_CONFIG
    if isinstance(file, dict):
        for key, value in file.items():
            if key in _CONFIG_FILE_ALLOW and isinstance(value, type(cfg_vars[key])):
                cfg_vars[key] = value
            elif key in _CONFIG_FILE_ALLOW:
                logger.print_critical_err("cannot load '%s' in config: Bad config type" % key, status=os.EX_CONFIG)
    elif file:
        logger.print_critical_err("cannot load config: Bad config type", status=os.EX_CONFIG)
    for key, value in flags.items():
        if key in _DEFAULT_CONFIG and value:
            cfg_vars[key] = value
    return cfg_vars


def _validate_config(cfg_vars: dict) -> None:
    # Slice variables to list for subprocess.run()
    cfg_vars["editor_flags"] = shlex.split(cfg_vars["editor_flags"])
    # Validate external commands exist
    cfg_vars["editor"] = _find_executable(cfg_vars["editor"])
    cfg_vars["tar"] = _find_executable(cfg_vars["tar"])


_EXAMPLE_CONFIG_FILE = """
###############################################
#        Example MUSCT configuration          #
# For more info, see:                         #
# https://gitlab.com/xythrez/musct/wikis/home #
###############################################

################## GENERAL ####################
#verbose: false
#no_root: false
#no_confirm: false

################## INSTALL ####################
#ignore_scripts: false
#ignore_msg: false
#editor: vim
#editor_flags: -N --nofork

################## BACKUPS ####################
#tar: /usr/bin/bsdtar
#compression_method: gzip
#full: false

################### CHECK #####################
#ignore_cmd_check: false
#ignore_missing_files: false
"""
