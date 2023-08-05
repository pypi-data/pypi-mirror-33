from ..installers.pipinstall import PipInstaller
from .common import Resolver
import re

matcher = re.compile(r"python(\d(\.\d)*)?-([\w\-_]+)")


class PipResolver(Resolver):
    def __init__(self, config_content: str, data):
        super().__init__(config_content, data)
        self.name = config_content.splitlines(False)[1]

    def provides(self, package_name):
        return bool(matcher.fullmatch(package_name))

    def get_resolver_name(self):
        return self.name

    def resolve_to_installer(self, package_name):
        match = matcher.match(package_name)
        return PipInstaller(match.group(3), match.group(1))  # temp i can't be botered to figure out regexes at 3am

    @classmethod
    def get_check_line(cls):
        return "PIP"
