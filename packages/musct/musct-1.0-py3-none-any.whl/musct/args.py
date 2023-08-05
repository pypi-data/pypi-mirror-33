import os
from argparse import ArgumentParser, ArgumentTypeError
from sys import argv

from musct.reference import VERSION, PROG_NAME


def _file(path: str):
    abspath = os.path.abspath(os.path.expanduser(path))
    if os.path.isfile(abspath):
        return abspath
    raise ArgumentTypeError("Not a file")


def _dir(path: str):
    abspath = os.path.abspath(os.path.expanduser(path))
    if os.path.isdir(abspath):
        return abspath
    raise ArgumentTypeError("Not a directory")


def _executable(exepath: str):
    dirname, basename = os.path.split(exepath)
    if dirname:
        abspath = os.path.abspath(os.path.expanduser(exepath))
        if os.path.isfile(abspath) and os.access(abspath, os.X_OK):
            return abspath
    for path in os.environ.get("PATH").split(os.pathsep):
        abspath = os.path.join(path, basename)
        if os.path.isfile(abspath) and os.access(abspath, os.X_OK):
            return abspath
    raise ArgumentTypeError("Not an executable")


def get_argument_settings() -> dict:
    parser = ArgumentParser(
        prog=PROG_NAME,
        description="A tool used to apply different configuration files",
    )

    subparsers = parser.add_subparsers(metavar="<command>", dest="command",
                                       help="Run 'musct <command> --help' for more info")
    list_parser = subparsers.add_parser("list", help="list available packages in the working directory")
    install_parser = subparsers.add_parser("install", help="install packages from the working directory")
    backup_parser = subparsers.add_parser("backup", help="backup current config files that would conflict with"
                                                         "installation")
    check_parser = subparsers.add_parser("check", help="check packages for errors and missing dependencies")

    parser.add_argument("-c", "--config", action="store", metavar="<path>", type=_file,
                        help="specify an alternative config file to use")
    parser.add_argument("-C", "--change-dir", action="store", metavar="<path>", type=_dir,
                        help="run as if musct was started in <path> instead of the current working directory")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="set logging to verbose mode")
    parser.add_argument("-V", "--version", action="version", version="%(prog)s version " + VERSION,
                        help="print version number and quit")

    # list
    list_parser.add_argument("-r", "--no-root", action="store_true",
                             help="exclude packages that require root permissions to install")

    # install
    install_parser.add_argument("packages", action="store", metavar="<packages>", nargs="*",
                                help="specify which packages to install")
    install_parser.add_argument("-r", "--no-root", action="store_true",
                                help="ignore packages that require root permissions to install")
    install_parser.add_argument("-y", "--no-confirm", action="store_true",
                                help="bypass any and all 'Are you sure?' messages")
    install_parser.add_argument("-s", "--ignore-scripts", action="store_true",
                                help="deny any and all external scripts from running")
    install_parser.add_argument("-S", "--ignore-msg", action="store_true",
                                help="suppress individual package messages")
    install_parser.add_argument("-N", "--ignore-cmd-check", action="store_true",
                                help="suppress unfulfilled command dependency warnings")
    install_parser.add_argument("-F", "--force", action="store_true",
                                help="force installation to overwrite existing files")
    install_parser.add_argument("-e", "--editor", action="store", metavar="<path>", type=_executable,
                                help="specify the editor used to view external scripts")
    install_parser.add_argument("-E", "--editor-flags", action="store", metavar="<flags>",
                                help="provide additional flags to editor")
    # backup
    backup_parser.add_argument("packages", action="store", metavar="<packages>", nargs="*",
                               help="specify which packages to backup")
    backup_parser.add_argument("-b", "--backup-file", action="store", metavar="<path>",
                               help="specify the location of the created archive")
    backup_parser.add_argument("-y", "--no-confirm", action="store_true",
                               help="bypass any and all 'Are you sure?' messages")
    backup_parser.add_argument("-t", "--tar", action="store", metavar="<path>", type=_executable,
                               help="specify an alternative bsdtar to use")
    backup_parser.add_argument("-T", "--compression-method", action="store", choices=["none", "gzip", "bzip2", "xz"],
                               help="specify the compression method used to create backups, the default is gzip")
    backup_parser.add_argument("-f", "--full", action="store_true",
                               help="perform full backup instead of only files conflicting with install")

    # check
    check_parser.add_argument("packages", action="store", metavar="<packages>", nargs="*",
                              help="specify which packages to check")
    check_parser.add_argument("-r", "--no-root", action="store_true",
                              help="ignore checks on packages that require root permissions")
    check_parser.add_argument("-m", "--ignore-missing-files", action="store_true",
                              help="ignore checking of missing files")
    check_parser.add_argument("-M", "--ignore-cmd-check", action="store_true",
                              help="ignore checking of missing command dependencies")
    check_parser.add_argument("-s", "--ignore-scripts", action="store_true",
                              help="ignore checking of script paths and permissions")

    argument_settings = parser.parse_args()
    if len(argv) == 1:
        parser.print_usage()
        exit(os.EX_NOINPUT)
    return vars(argument_settings)
