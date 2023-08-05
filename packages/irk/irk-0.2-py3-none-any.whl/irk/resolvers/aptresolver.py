from irk.installers.aptinstall import AptInstaller
from .common import Resolver
from ..util.proc import run


class AptResolver(Resolver):
    def __init__(self, config_content, data):
        super().__init__(config_content, data)
        self.name = config_content.splitlines(False)[1]
        self.executable = config_content.splitlines(False)[2]

    def provides(self, package_name):
        return True

    def get_resolver_name(self):
        return self.name

    def resolve_to_installer(self, package_name):
        return AptInstaller(package_name, self.executable)

    @classmethod
    def get_check_line(cls):
        return "APT"

    def update_resolver(self):
        print("Updating apt cache")
        run([self.executable, "update"])
        print("Done updating apt cache")
