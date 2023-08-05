import os
import shutil
import subprocess

from musct.cli_command import CliFunction, parse_package_selection
from musct.fileutils import find_conflicting, copy_as_root, run_as_root, is_executable, is_executable_in
from musct.log import logger
from musct.package import get_from_dict, find_executable_packages, Package
from musct.printer import ConfirmationPrinter
from musct.settings import Settings


class InstallFunction(CliFunction):
    def execute(self, avail_pkgs: list, settings: Settings):
        packages = parse_package_selection(avail_pkgs, settings, action="install")

        printer = ConfirmationPrinter()

        cmd_deps = {}
        font_deps = []
        pre_msg = {}
        post_msg = {}

        sub_files = {}

        installs = {}
        installs_root = {}

        scripts = []
        scripts_root = []

        exec_packages = find_executable_packages(packages)

        # general housekeeping (update dicts and lists)
        printer.print_line(":: Generating package info, this may take a while.")
        for package in packages:
            for cmd, desc in package.cmd_deps.items():
                if is_executable(cmd) or is_executable_in(cmd, exec_packages):
                    continue
                if cmd not in cmd_deps:
                    cmd_deps[cmd] = desc

            for font in package.font_deps:
                if font not in font_deps:
                    font_deps.append(font)

            if package.pre_msg:
                pre_msg[package.name] = package.pre_msg

            if package.post_msg:
                post_msg[package.name] = package.post_msg

            if package.substitute_username:
                _add_substitutes(package, sub_files)

            if package.script:
                _add_script(package, scripts, scripts_root)

            _add_files(package, installs, installs_root, settings)

        if not installs and not installs_root:
            printer.print_line("No new files need to be installed. Exiting.")
            exit(0)

        if cmd_deps and not settings.cfg_vars["ignore_cmd_check"]:
            _show_cmd_deps(cmd_deps, printer)

        if font_deps:
            _show_font_deps(font_deps, printer)

        if pre_msg and not settings.cfg_vars["ignore_msg"]:
            _show_pre_msg(pre_msg, printer)

        if scripts or scripts_root:
            _audit_scripts(scripts, scripts_root, printer, settings)

        if sub_files:
            _substitute_usernames(sub_files, settings, printer)

        _install_files(installs, installs_root, printer)
        _run_scripts(scripts, scripts_root, settings, printer)

        printer.print_line("\n:: Installation Complete.")

        if post_msg and not settings.cfg_vars["ignore_msg"]:
            _show_post_msg(post_msg, printer)
        return ""


def _add_substitutes(package: Package, sub_list: dict):
    for file, match in package.substitute_username.items():
        abspath = os.path.join(package.path, file)
        sub_list[abspath] = match


def _add_script(package: Package, scripts: list, scripts_root: list):
    root = get_from_dict(package.script, "root", bool)
    rel_src = get_from_dict(package.script, "src", str)
    if not rel_src:
        logger.print_critical_err("cannot run script in '%s': No src provided" % package.name,
                                  status=os.EX_CONFIG)
    abs_src = os.path.join(os.getcwd(), rel_src)
    if os.path.isfile(abs_src) and os.access(abs_src, os.X_OK):
        if root and abs_src not in scripts_root:
            scripts_root.append(abs_src)
        elif not root and abs_src not in scripts:
            scripts.append(abs_src)
    else:
        logger.print_critical_err("cannot run script in %s: File not found" % package.name,
                                  status=os.EX_CONFIG)


def _add_files(package: Package, installs: dict, installs_root: dict, settings: Settings):
    files, files_root = package.apply()
    for dest, source in files.items():
        diff = find_conflicting(dest, source, include_missing=True)
        installs.update(diff)
    for dest, source in files_root.items():
        diff = find_conflicting(dest, source, include_missing=True)
        installs_root.update(diff)
    if not settings.cfg_vars["force"]:
        for dest, source in files.items():
            conflicts = find_conflicting(dest, source)
            if conflicts:
                logger.print_critical_err("cannot install: configuration exists, backup configs or use "
                                          "'--force' instead: '%s'" % list(conflicts.keys()),
                                          status=os.EX_CANTCREAT)
        for dest, source in files_root.items():
            conflicts = find_conflicting(dest, source)
            if conflicts:
                logger.print_critical_err("cannot install: configuration exists, backup configs or use "
                                          "'--force' instead: '%s'" % list(conflicts.keys()),
                                          status=os.EX_CANTCREAT)


def _show_cmd_deps(cmd_deps: dict, printer: ConfirmationPrinter):
    printer.add(":: Certain command dependencies are not fulfilled:")
    for cmd, desc in cmd_deps.items():
        printer.add("%s:" % cmd)
        printer.add("    %s" % desc)
    if not printer.get_input("Do you want to continue?"):
        exit(os.EX_NOINPUT)


def _show_font_deps(font_deps: list, printer: ConfirmationPrinter):
    printer.add(":: Listing fonts required for packages pending install:")
    font_str = ""
    for font in font_deps:
        font_str += "%s, " % font
    printer.add(font_str)
    printer.add(":: Musct currently has no way of detecting fonts installed.")
    printer.add(":: You can manually check by using 'fc-match'.")
    if not printer.get_input("Do you want to continue?"):
        exit(os.EX_NOINPUT)


def _show_pre_msg(pre_msg, printer: ConfirmationPrinter):
    printer.add(":: Displaying individual package messages:\n")
    for pkg_name, msg in pre_msg.items():
        printer.add("========================================")
        printer.add("%s:" % pkg_name)
        printer.add("    %s" % msg)
    printer.add("========================================")
    if not printer.get_input("Do you want to continue?"):
        exit(os.EX_NOINPUT)


def _show_post_msg(post_msg, printer: ConfirmationPrinter):
    printer.add(":: Displaying post installation package messages:\n")
    for pkg_name, msg in post_msg.items():
        printer.add("========================================")
        printer.add("%s:" % pkg_name)
        printer.add("    %s" % msg)
    printer.add("========================================")
    printer.print()


def _audit_scripts(scripts: list, scripts_root: list, printer: ConfirmationPrinter, settings: Settings):
    printer.add(":: Third-party scripts are included in this installation.")
    if printer.get_input("Would you like to view these scripts?"):
        editor = settings.cfg_vars["editor"]
        editor_flags = settings.cfg_vars["editor_flags"]
        for script in scripts:
            edit_cmd = [editor, script]
            edit_cmd.extend(editor_flags)
            edit = subprocess.run(edit_cmd)
            if edit.returncode:
                logger.print_critical_err("Editor received non-zero exit code, terminating",
                                          status=edit.returncode)
        for script in scripts_root:
            edit_cmd = [editor, script]
            edit_cmd.extend(editor_flags)
            edit = subprocess.run(edit_cmd)
            if edit.returncode:
                logger.print_critical_err("Editor received non-zero exit code, terminating",
                                          status=edit.returncode)


def _substitute_usernames(sub_files: dict, settings: Settings, printer: ConfirmationPrinter):
    printer.print_line(":: Substituting username strings")
    username = settings.env_vars["USER"]
    try:
        for path, replace_str in sub_files.items():
            with open(path, "r") as file:
                lines = file.readlines()
            with open(path, "w") as file:
                for line in lines:
                    file.write(line.replace(replace_str, username))
    except (OSError, IOError) as err:
        logger.print_critical_err(err, status=os.EX_IOERR)


def _install_files(installs: dict, installs_root: dict, printer: ConfirmationPrinter):
    printer.print_line(":: Installing config files")
    if installs_root:
        status = copy_as_root(installs_root)
        if status:
            logger.print_critical_err("Copy as root exited with return code %s" % status, status=status)
    try:
        for dest, source in installs.items():
            parent = os.path.dirname(dest)
            os.makedirs(parent, exist_ok=True)
            if os.path.isfile(dest):
                os.remove(dest)
            elif os.path.isdir(dest):
                shutil.rmtree(dest)
            if os.path.isdir(source):
                shutil.copytree(source, dest, ignore_dangling_symlinks=True)
            elif os.path.isfile(source):
                shutil.copy2(source, dest)
    except (OSError, IOError) as err:
        logger.print_critical_err(err, status=os.EX_IOERR)


def _run_scripts(scripts: list, scripts_root: list, settings: Settings, printer: ConfirmationPrinter):
    if scripts or scripts_root:
        printer.print_line(":: Running scripts.")
    if not settings.cfg_vars["ignore_scripts"] and scripts_root:
        status = run_as_root(scripts_root)
        if status:
            logger.print_critical_err("Run script as root exited with return code %s" % status, status=status)
    if not settings.cfg_vars["ignore_scripts"]:
        for script_path in scripts:
            script_run = subprocess.run(script_path)
            if script_run.returncode:
                logger.print_critical_err("Run script exited with return code %s: %s" % (script_run, script_path),
                                          status=script_run.returncode)
