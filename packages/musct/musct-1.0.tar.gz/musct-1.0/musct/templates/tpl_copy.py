import os

import musct.template
from musct.package import get_from_dict


class CopyTemplate(musct.template.PackageTemplate):
    def __init__(self, env_vars):
        super().__init__("copy", env_vars)
        self.sub_vars = {
            "HOME": env_vars["HOME"],
            "XDG_CONFIG_HOME": env_vars["USER_CONFIG_HOME"],
            "XDG_CACHE_HOME": env_vars["USER_CACHE_HOME"],
            "XDG_DATA_HOME": env_vars["USER_DATA_HOME"],
            "FILE_NAME": "",
            "PKG_NAME": ""
        }

    def _format_installs(self, pkg_path: str, copies: dict, fallback_pkg="") -> dict:
        installs = {}
        # TODO allow multiple copy locations of one file
        for source, dest in copies.items():
            self.sub_vars["FILE_NAME"] = source
            source_path = os.path.join(pkg_path, source)
            if fallback_pkg and not os.path.exists(source_path):
                source_path = os.path.join(os.path.dirname(pkg_path), fallback_pkg, source)

            for key, var in self.sub_vars.items():
                dest = dest.replace("${%s}" % key, var)

            installs[dest] = source_path
        return installs

    def on_apply(self, pkg_path: str, args: dict):
        self.sub_vars["PKG_NAME"] = os.path.basename(pkg_path)
        installs = {}
        installs_root = {}
        fallback_pkg = get_from_dict(args, "fallback_pkg", str)
        copies = get_from_dict(args, "copy", dict)
        copies_root = get_from_dict(args, "copy_root", dict)
        if copies:
            installs = self._format_installs(pkg_path, copies, fallback_pkg=fallback_pkg)
        if copies_root:
            installs_root = self._format_installs(pkg_path, copies_root, fallback_pkg=fallback_pkg)
        return [installs, installs_root]
