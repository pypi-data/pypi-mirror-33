import abc
import importlib
import inspect
import os
import sys

from musct.log import logger


class PackageTemplate(abc.ABC):
    name: str = "generic"
    env_vars: dict

    @abc.abstractmethod
    def __init__(self, name: str, env_vars: dict):
        self.name = name
        self.env_vars = env_vars

    @abc.abstractmethod
    def on_apply(self, pkg_path: str, args: dict) -> list:
        return [{}, {}]


class TemplateManager:
    _templates: dict = {}

    # Imports all templates within the templates module
    def __init__(self, settings):
        env_vars = settings.env_vars
        template_dir = os.path.join(os.path.dirname(sys.modules[__name__].__file__), "templates")

        for file_name in os.listdir(template_dir):
            if file_name.startswith("tpl_") and file_name.endswith(".py"):
                module_name = file_name[:-3]
                module = importlib.import_module("musct.templates.%s" % module_name)

                for name, class_obj in inspect.getmembers(module):
                    if inspect.isclass(class_obj):
                        template_obj = class_obj(env_vars)
                        if isinstance(template_obj, PackageTemplate):
                            self.register_template(template_obj)

        logger.print_debug("TEMPLATES LOADED: %s" % self.get_templates_names())

    def register_template(self, template_obj: PackageTemplate):
        if isinstance(template_obj, PackageTemplate) and template_obj.name not in self._templates:
            self._templates[template_obj.name] = template_obj
        elif template_obj.name in self._templates:
            logger.print_warn("ignoring duplicate template: %s" % template_obj.name)
        else:
            logger.print_warn("ignoring unknown object: %s" % str(template_obj))

    def get_template(self, tpl_name: str):
        return self._templates.get(tpl_name, None)

    def get_templates_names(self):
        return list(self._templates.keys())
