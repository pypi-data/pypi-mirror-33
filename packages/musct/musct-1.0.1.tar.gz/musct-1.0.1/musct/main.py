#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import signal
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from musct.log import logger
from musct.settings import Settings
from musct.template import TemplateManager
from musct.reference import VERSION, PROG_NAME
from musct.cmd_backup import BackupFunction
from musct.cmd_check import CheckFunction
from musct.cmd_list import ListFunction
from musct.cmd_install import InstallFunction
from musct.package import get_available_packages

__version__ = VERSION


def main():
    _settings = Settings()
    _manager = TemplateManager(_settings)

    def handle_ungraceful_exit(*args):
        prog_tmp_dir = "/tmp/%s" % PROG_NAME
        session_tmp_dir = os.path.join(prog_tmp_dir, os.path.basename(os.getcwd()))
        shutil.rmtree(session_tmp_dir, ignore_errors=True)
        logger.print_critical_err("Received signal to stop. Goodbye", status=125)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    signal.signal(signal.SIGINT, handle_ungraceful_exit)

    if _settings.env_vars["USER"] == "root":
        logger.print_critical_err("Application cannot be run as root", status=os.EX_NOUSER)
    controller = CliController(_settings, _manager)
    controller.start()


class CliController:
    settings: Settings
    tpl_manager: TemplateManager
    _functions: dict
    _packages: dict = None

    def __init__(self, settings: Settings, tpl_manager: TemplateManager):
        self.settings = settings
        self.tpl_manager = tpl_manager
        self._functions = dict(
            install=InstallFunction(),
            list=ListFunction(),
            backup=BackupFunction(),
            check=CheckFunction(),
        )

    def call(self, command: str):
        return self._functions[command].execute(self._packages, self.settings)

    def start(self):
        # Since check suppresses all errors from exiting musct it needs to be handled differently
        # This also means that nothing can loop back to check internally
        command = self.settings.cfg_vars["command"]

        if not self._packages and command == "check":
            self._packages = get_available_packages(self.settings, self.tpl_manager, store_errs=True)
        elif not self._packages:
            self._packages = get_available_packages(self.settings, self.tpl_manager)

        while True:
            command = self.call(command)
            if command == "":
                break


if __name__ == "__main__":
    main()
