import os

import musct.template


# This template is still WIP
# TODO: Add dir to path
class ExecutableFileTemplate(musct.template.PackageTemplate):
    def __init__(self, env_vars):
        super().__init__("executable_file", env_vars)
        home_dir = env_vars["HOME"]
        if os.path.isdir(os.path.join(home_dir, ".local")):
            self._bin_dir = os.path.join(home_dir, ".local", "bin")
        else:
            self._bin_dir = os.path.join(home_dir, ".bin")

    def on_apply(self, pkg_path: str, args: dict):
        installs = {}
        for file in os.listdir(pkg_path):
            if file == ".MUSCTPKG":
                continue
            source = os.path.join(pkg_path, file)
            dest = os.path.join(self._bin_dir, file)
            installs[dest] = source
        return [installs, {}]

