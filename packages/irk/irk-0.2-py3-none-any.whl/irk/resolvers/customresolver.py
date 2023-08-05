import re

from irk.installers.script import ScriptInstaller
from .common import Resolver


class RegexResolver(Resolver):
    def __init__(self, config_content, data):
        super().__init__(config_content, data)
        self.name = config_content.splitlines(False)[1]
        self.regex = re.compile(config_content.splitlines(False)[2])
        self.script = data

    def provides(self, package_name):
        return bool(self.regex.fullmatch(package_name))

    def get_resolver_name(self):
        return self.name

    def resolve_to_installer(self, package_name):
        return ScriptInstaller(self.script, package_name)

    @classmethod
    def get_check_line(cls):
        return "CREGX"

    def update_resolver(self):
        pass
