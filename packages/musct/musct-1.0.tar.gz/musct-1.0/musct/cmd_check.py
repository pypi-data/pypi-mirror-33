import os

from musct.cli_command import CliFunction, parse_package_selection
from musct.fileutils import is_executable, is_executable_in
from musct.package import get_from_dict, find_executable_packages
from musct.printer import BufferedPrinter
from musct.settings import Settings


class CheckFunction(CliFunction):
    _has_errs = False
    printer = BufferedPrinter()

    def execute(self, avail_pkgs: list, settings: Settings):
        packages = parse_package_selection(avail_pkgs, settings, never_ask_user=True, action="check")

        self.printer.print_line(":: Checking for errors in .MUSCTINFO and .MUSCTPKG.")
        self._print_results_if_any(settings.rt_vars.get("pkg_syntax_errs"))
        self.printer.print_line(":: Syntax check completed.")

        if not settings.cfg_vars["ignore_missing_files"]:
            self.printer.print_line(":: Checking for files used in packages.")
            self._print_results_if_any(_check_missing_files(packages, settings))
            self.printer.print_line(":: File check completed.")

        if not settings.cfg_vars["ignore_cmd_check"]:
            self.printer.print_line(":: Checking for commands used in packages.")
            self._print_results_if_any(_check_commands(packages, settings))
            self.printer.print_line(":: Command check completed.")

        # TODO: Check fonts

        if not settings.cfg_vars["ignore_scripts"]:
            self.printer.print_line(":: Checking for Scripts used in packages.")
            self._print_results_if_any(_check_scripts(packages, settings))
            self.printer.print_line(":: Script check completed.")

        self.printer.print_line(":: All checks completed.")
        if self._has_errs:
            self.printer.print_line(":: Errors were detected.")
            exit(os.EX_CONFIG)
        self.printer.print_line(":: No error detected.")
        return ""

    def _print_results_if_any(self, results: list):
        if results:
            self._has_errs = True
            self.printer.extend_buffer(results)
            self.printer.print()


def _check_missing_files(packages: list, settings: Settings):
    warnings = []
    for package in packages:
        if settings.cfg_vars["no_root"] and package.root:
            continue
        filelist, filelist_root = package.apply()
        filelist.update(filelist_root)
        for dest, source in filelist.items():
            if not os.path.exists(source):
                warnings.append("not found: '%s' does not contain '%s'" % (package.name, source))
    return warnings


def _check_commands(packages: list, settings: Settings):
    warnings = []
    exec_packages = find_executable_packages(packages)
    for package in packages:
        if settings.cfg_vars["no_root"] and package.root:
            continue
        elif package.cmd_deps:
            for cmd, desc in package.cmd_deps.items():
                if is_executable(cmd) or is_executable_in(cmd, exec_packages):
                    continue
                warnings.append("missing command '%s' for %s: %s" % (cmd, package.name, desc))
    return warnings


def _check_scripts(packages: list, settings: Settings):
    warnings = []
    for package in packages:
        if settings.cfg_vars["no_root"] and package.root:
            continue
        elif package.script:
            script_info = package.script
            rel_path = get_from_dict(script_info, "src", str)
            pkg_root = os.path.dirname(package.path)
            abspath = os.path.join(pkg_root, rel_path)
            if not os.path.isfile(abspath) or not os.access(abspath, os.X_OK):
                warnings.append("script error: '%s' is not an executable script" % rel_path)
    return warnings
