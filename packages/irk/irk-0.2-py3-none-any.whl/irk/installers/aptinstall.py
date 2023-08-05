from .common import Installer, InstallerState
from ..util import proc


class AptInstaller(Installer):
    def __init__(self, package, exec):
        self.package = package
        self.exec = exec

    def install(self, dry_run):
        args = [self.exec, "install", self.package, "-y"]
        if dry_run:
            print(f"Would run {' '.join(args)}")
            return InstallerState.OK
        code, stdout = proc.run(args)
        if code == 0:
            return InstallerState.OK
        elif "are you root?" in stdout:
            return InstallerState.NEEDS_SUDO
        elif "E: Unable to locate package" in stdout:
            return InstallerState.INVALID_NAME
        else:
            return InstallerState.FAILED

    def remove(self, dry_run):
        args = [self.exec, "remove", self.package, "-y"]
        if dry_run:
            print(f"Would run {' '.join(args)}")
            return InstallerState.OK
        code, stdout = proc.run(args)
        if code == 0:
            return InstallerState.OK
        elif "are you root?" in stdout:
            return InstallerState.NEEDS_SUDO
        elif "E: Unable to locate package" in stdout:
            return InstallerState.INVALID_NAME
        else:
            return InstallerState.FAILED

    def get_dependencies(self):
        return []