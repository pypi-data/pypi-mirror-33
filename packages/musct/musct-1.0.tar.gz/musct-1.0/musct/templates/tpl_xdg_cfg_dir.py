import os

import musct.template


class XDGCfgDirTemplate(musct.template.PackageTemplate):
    def __init__(self, env_vars):
        super().__init__("xdg_cfg_dir", env_vars)
        self._xdg_cfg_home = env_vars["USER_CONFIG_HOME"]

    def on_apply(self, pkg_path: str, args: dict):
        installs = {}
        dest_dir = os.path.basename(pkg_path)
        for file in os.listdir(pkg_path):
            if file == ".MUSCTPKG":
                continue
            source = os.path.join(pkg_path, file)
            dest = os.path.join(self._xdg_cfg_home, dest_dir, file)
            installs[dest] = source
        return [installs, {}]
