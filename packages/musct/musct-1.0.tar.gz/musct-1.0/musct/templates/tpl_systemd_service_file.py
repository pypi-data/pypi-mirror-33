import os

import musct.template


class SystemdServiceFileTemplate(musct.template.PackageTemplate):
    def __init__(self, env_vars):
        super().__init__("systemd_service_file", env_vars)
        self._service_dir = "/etc/systemd/system"

    def on_apply(self, pkg_path: str, args: dict):
        installs_root = {}
        for file in os.listdir(pkg_path):
            if file.endswith(".service"):
                source = os.path.join(pkg_path, file)
                dest = os.path.join(self._service_dir, file)
                installs_root[dest] = source
        return [{}, installs_root]
