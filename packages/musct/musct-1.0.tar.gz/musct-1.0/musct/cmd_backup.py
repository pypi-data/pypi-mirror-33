import os
import shutil
from subprocess import run

from musct.cli_command import CliFunction, parse_package_selection
from musct.fileutils import find_conflicting
from musct.log import logger
from musct.printer import BufferedPrinter
from musct.reference import PROG_NAME
from musct.settings import Settings


class BackupFunction(CliFunction):
    def execute(self, avail_pkgs: list, settings: Settings):
        packages = parse_package_selection(avail_pkgs, settings, action="backup")
        pkg_name = os.path.basename(os.getcwd())
        if pkg_name.startswith("."):
            pkg_name = pkg_name[1:]
        prog_tmp_dir = os.path.join("/", "tmp", PROG_NAME)
        session_tmp_dir = os.path.join(prog_tmp_dir, pkg_name)
        printer = BufferedPrinter()

        if os.path.exists(session_tmp_dir):
            logger.print_critical_err("backup already in progress: If you think this is a mistake delete "
                                      "'%s' and try again" % session_tmp_dir, status=os.EX_CANTCREAT)

        printer.print_line(":: Getting file information")
        backups = _list_backup_files(packages, settings)

        printer.print_line(":: Copying backup targets to %s" % session_tmp_dir)
        _copy_backup_files(session_tmp_dir, backups)

        printer.print_line(":: Creating archive")
        _create_archive(pkg_name, prog_tmp_dir, settings)

        printer.print_line(":: Backup complete")
        return ""


def _get_compression_flag(settings: Settings) -> str:
    comp_method = settings.cfg_vars.get("compression_method", "gzip")
    if comp_method == "none":
        return ""
    elif comp_method == "bzip2":
        return "j"
    elif comp_method == "xz":
        return "J"
    return "z"


def _get_compression_suffix(settings: Settings) -> str:
    comp_method = settings.cfg_vars.get("compression_method", "gzip")
    if comp_method == "none":
        return ".tar"
    elif comp_method == "bzip2":
        return ".tar.bz2"
    elif comp_method == "xz":
        return ".tar.xz"
    return ".tar.gz"


def _get_verbosity(settings: Settings) -> str:
    if settings.cfg_vars["verbose"]:
        return "v"
    return ""


def _is_writable_file(path: str) -> bool:
    abspath = os.path.abspath(os.path.expanduser(path))
    if os.path.exists(abspath) or not os.access(os.path.dirname(abspath), os.W_OK):
        return False
    return True


def _list_backup_files(packages: list, settings: Settings) -> dict:
    backups = {}
    for package in packages:
        files, root_files = package.apply()
        files.update(root_files)
        if settings.cfg_vars["full"]:
            backups.update(files)
            continue
        for dest, source in files.items():
            pkg_backups = find_conflicting(dest, source)
            backups.update(pkg_backups)
    return backups


def _copy_backup_files(dest_dir: str, files: dict):
    if not files:
        logger.print_critical_err("No files to backup. Operation stopped.", status=os.EX_DATAERR)
    try:
        os.makedirs(dest_dir, exist_ok=True)
        for source, mirror in files.items():
            dest = os.path.join(dest_dir, os.path.relpath(mirror, os.getcwd()))
            parent = os.path.dirname(dest)
            os.makedirs(parent, exist_ok=True)
            if os.path.isdir(source) and not os.path.exists(dest):
                shutil.copytree(source, dest, ignore_dangling_symlinks=True)
            elif os.path.isfile(source):
                shutil.copy2(source, dest)
            else:
                logger.print_warn("Ignoring copy '%s' to '%s': path exists" % (source, dest))
    except (OSError, IOError) as err:
        logger.print_critical_err(err, status=os.EX_IOERR)


def _create_archive(pkg_name: str, prog_tmp_dir: str, settings: Settings):
    session_tmp_dir = os.path.join(prog_tmp_dir, pkg_name)
    if settings.cfg_vars.get("backup_file"):
        path = settings.cfg_vars["backup_file"]
    else:
        path = os.path.join(os.getcwd(), "%s-backup%s" % (pkg_name, _get_compression_suffix(settings)))
    if not _is_writable_file(path):
        logger.print_critical_err("failed to create %s: Cannot write to location" % path, status=os.EX_CONFIG)
        shutil.rmtree(session_tmp_dir, ignore_errors=True)
    tar_cmd = [
        settings.cfg_vars["tar"],
        "-c%sHf" % (_get_compression_flag(settings) + _get_verbosity(settings)),
        path,
        "-C",
        prog_tmp_dir,
        pkg_name
    ]
    tar = run(tar_cmd)
    shutil.rmtree(os.path.join(prog_tmp_dir, pkg_name), ignore_errors=True)
    if tar.returncode:
        exit(tar.returncode)
