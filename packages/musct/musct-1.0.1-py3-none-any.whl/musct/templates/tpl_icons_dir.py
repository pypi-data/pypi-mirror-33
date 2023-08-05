import os

import musct.template


class IconsDirTemplate(musct.template.PackageTemplate):
    def __init__(self, env_vars):
        super().__init__("icons_dir", env_vars)
        home_dir = env_vars["HOME"]
        xdg_data_home = env_vars["USER_DATA_HOME"]
        non_compat_dir = os.path.join(xdg_data_home, "icons")
        if os.path.isdir(non_compat_dir):
            self._icon_dir = non_compat_dir
        else:
            self._icon_dir = os.path.join(home_dir, ".icons")

    def on_apply(self, pkg_path: str, args: dict):
        installs = {}
        for file in os.listdir(pkg_path):
            if file == ".MUSCTPKG":
                continue
            source = os.path.join(pkg_path, file)
            dest = os.path.join(self._icon_dir, file)
            installs[dest] = source
        return [installs, {}]
