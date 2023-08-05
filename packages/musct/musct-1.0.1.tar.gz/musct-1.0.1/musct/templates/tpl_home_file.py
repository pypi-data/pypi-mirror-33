import os

import musct.template
from musct.package import get_from_dict


class HomeFileTemplate(musct.template.PackageTemplate):
    def __init__(self, env_vars):
        super().__init__("home_file", env_vars)
        self._home_dir = env_vars["HOME"]

    def on_apply(self, pkg_path: str, args: dict):
        installs = {}
        add_dot_prefix = get_from_dict(args, "add_dot_prefix", bool)
        for file in os.listdir(pkg_path):
            if file == ".MUSCTPKG":
                continue
            source = os.path.join(pkg_path, file)
            if add_dot_prefix and not file.startswith("."):
                dest = os.path.join(self._home_dir, ".%s" % file)
            else:
                dest = os.path.join(self._home_dir, file)
            installs[dest] = source
        return [installs, {}]
