from musct.cli_command import CliFunction
from musct.printer import BufferedPrinter
from musct.settings import Settings


class ListFunction(CliFunction):
    def execute(self, avail_pkgs: list, settings: Settings):
        no_root = settings.cfg_vars["no_root"]
        printer: BufferedPrinter = BufferedPrinter()
        printer.add(":: Available packages:")
        for package in avail_pkgs:
            if no_root and package.root:
                continue
            elif package.root:
                printer.add("%s (requires root)" % package.name)
            else:
                printer.add(package.name)
            printer.add("    %s" % package.desc)
        printer.print()
        return ""
