import os

from yaml import YAMLError

from musct.log import logger, format_yaml_err
from musct.reference import INFO_REV, INFO_FILE, PKG_REV, PKG_FILE
from musct.settings import Settings
from musct.template import PackageTemplate, TemplateManager
from musct.yaml_wrapper import parse_file


class Package:
    name: str
    desc: str
    root: bool
    path: str
    cmd_deps: dict
    font_deps: dict
    tpl: PackageTemplate
    tpl_args: dict
    pre_msg: str
    post_msg: str
    script: dict
    substitute_username: dict

    def __init__(self, pkg_path: str, pkg_info: dict, tpl_manager: TemplateManager):
        self.name = os.path.basename(pkg_path)
        self.path = pkg_path
        keys = pkg_info.keys()
        essentials = ["pkg_template"]
        for key in essentials:
            if key not in keys:
                raise LookupError("required key '%s' not found in '%s'" % (key, pkg_path))
        tpl_name = get_from_dict(pkg_info, "pkg_template", str, raise_err=True, err_location=pkg_path)
        self.tpl = tpl_manager.get_template(tpl_name)
        if not self.tpl:
            raise ModuleNotFoundError("cannot load template '%s' for '%s':Template not found" % (pkg_path, tpl_name))
        self.desc = get_from_dict(pkg_info, "pkg_desc", str, default="No description was provided for this package.",
                                  raise_err=True, err_location=pkg_path)
        self.tpl_args = get_from_dict(pkg_info, "template_args", dict, raise_err=True, err_location=pkg_path)
        self.script = get_from_dict(pkg_info, "script", dict, raise_err=True, err_location=pkg_path)
        self.root = self.tpl.on_apply(self.path, self.tpl_args)[1] or self.script.get("root")
        self.pre_msg = get_from_dict(pkg_info, "pre_msg", str, raise_err=True, err_location=pkg_path)
        self.post_msg = get_from_dict(pkg_info, "post_msg", str, raise_err=True, err_location=pkg_path)
        self.cmd_deps = get_from_dict(pkg_info, "cmd_deps", dict, raise_err=True, err_location=pkg_path)
        self.font_deps = get_from_dict(pkg_info, "font_deps", list, raise_err=True, err_location=pkg_path)
        self.substitute_username = get_from_dict(pkg_info, "substitute_username", dict, raise_err=True,
                                                 err_location=pkg_path)

    def apply(self) -> list:
        return self.tpl.on_apply(self.path, self.tpl_args)


def get_from_dict(dictionary, key, value_type, default=None, raise_err=False, err_location=""):
    value = dictionary.get(key)
    if key in dictionary:
        if isinstance(value, value_type):
            return value
        elif raise_err:
            raise TypeError("bad type for '%s': Expected '%s': %s" % (key, value_type, err_location))
    if default:
        return default
    return value_type()


def _read_info_file(path: str):
    if not os.path.isfile(path):
        logger.print_critical_err("cannot detect packages: No valid %s" % INFO_FILE, status=os.EX_IOERR)
    try:
        info = parse_file(path)
    except (OSError, IOError) as err:
        logger.print_critical_err(err, status=os.EX_IOERR)
    except YAMLError as err:
        logger.print_yaml_err(path, err)
    if not isinstance(info, dict):
        logger.print_critical_err("cannot load %s: Bad YAML type" % INFO_FILE,
                                  status=os.EX_CONFIG)
    if get_from_dict(info, "musctinfo_rev", int, default=9001) > INFO_REV:
        logger.print_critical_err("cannot load %s: Unknown file version" % INFO_FILE, status=os.EX_CONFIG)
    return info


def get_available_packages(settings: Settings, tpl_manager: TemplateManager, store_errs=False) -> list:
    packages: list = []
    cwd: str= os.getcwd()
    info_path: str = os.path.join(cwd, INFO_FILE)

    errs = []
    info = _read_info_file(info_path)

    for pkg_name in get_from_dict(info, "provides", list):
        pkg_path = os.path.join(cwd, pkg_name, PKG_FILE)
        if not os.path.isfile(pkg_path):
            msg = "invalid package '%s': No %s found" % (pkg_name, PKG_FILE)
            if not store_errs:
                logger.print_critical_err(msg, status=os.EX_IOERR)
            errs.append(msg)
        pkg = {}
        try:
            pkg = parse_file(pkg_path)
        except (OSError, IOError) as err:
            if not store_errs:
                logger.print_critical_err(err, status=os.EX_IOERR)
            errs.append(str(err))
        except YAMLError as err:
            if not store_errs:
                logger.print_yaml_err(pkg_path, err)
            errs.append(format_yaml_err(pkg_path, err))

        if not isinstance(pkg, dict):
            msg = "invalid package '%s': Bad YAML type" % pkg_name
            if not store_errs:
                logger.print_critical_err(msg, status=os.EX_CONFIG)
            errs.append(msg)
        if get_from_dict(pkg, "musctpkg_rev", int, default=9001) > PKG_REV:
            msg = "invalid package '%s': unknown file version" % pkg_name
            if not store_errs:
                logger.print_critical_err(msg, status=os.EX_CONFIG)
            errs.append(msg)

        try:
            packages.append(Package(os.path.dirname(pkg_path), pkg, tpl_manager))
        except (TypeError, ModuleNotFoundError, LookupError) as err:
            if not store_errs:
                logger.print_critical_err(err, status=os.EX_IOERR)
            errs.append(str(err))
    if len(errs):
        settings.rt_vars["pkg_syntax_errs"] = errs
    if not packages:
        logger.print_critical_err("no packages found", status=os.EX_DATAERR)
    return packages


def find_executable_packages(packages: list) -> list:
    exec_packages = []
    for package in packages:
        if package.tpl.name == "executable_file":
            exec_packages.append(package)
    return exec_packages
