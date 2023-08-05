import abc
import os

from musct.log import logger
from musct.printer import InputPrinter
from musct.settings import Settings


class CliFunction:
    @abc.abstractmethod
    def execute(self, avail_pkgs: list, settings: Settings) -> str:
        return ""


def parse_package_selection(avail_pkgs: list, settings: Settings, never_ask_user=False, action="default") -> list:
    packages = []
    avail = []
    if settings.cfg_vars["no_root"]:
        for pkg in avail_pkgs:
            if not pkg.root:
                avail.append(pkg)
    else:
        avail = avail_pkgs

    if settings.cfg_vars.get("packages"):
        avail_pkg_map = {package.name: package for package in avail}
        for pkg in settings.cfg_vars["packages"]:
            if pkg in avail_pkg_map:
                packages.append(avail_pkg_map[pkg])
            else:
                logger.print_critical_err("could not find package %s" % pkg, status=os.EX_UNAVAILABLE)
    elif settings.cfg_vars["no_confirm"] or never_ask_user:
        packages = avail
    else:
        packages = _get_from_user(avail, action)
    return packages


def _get_from_user(packages: list, action: str) -> list:
    inp = InputPrinter()
    InputPrinter().print_line(":: Please select packages to %s:" % action)
    for i in range(len(packages), 0, -1):
        package = packages[i - 1]
        inp.add("%s. %s" % (i, package.name))
        inp.add("    %s" % package.desc)

    pkg_str = inp.get_input("Packages to %s (e.g. 1 2 3, [Enter] for all)\n==>" % action)
    if not pkg_str:
        return packages
    install = []
    for id_str in pkg_str.split(" "):
        try:
            pkg_id = int(id_str) - 1
            install.append(packages[pkg_id])
        except (ValueError, IndexError):
            logger.print_critical_err("unknown package %s selected, exiting." % id_str, status=os.EX_UNAVAILABLE)
    return install
