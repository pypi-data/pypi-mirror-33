import os
import subprocess
import tempfile

from irk.installers.common import Installer, InstallerState


class ScriptInstaller(Installer):
    def __init__(self, script_contents, package):
        self.script_contents = script_contents
        self.package = package

    def install(self, dry_run):
        if dry_run:
            print("Would run a custom script, unable to show contents.")
            return InstallerState.OK
        f, n = tempfile.mkstemp(text=True)
        os.write(f, bytes(self.script_contents, encoding="ascii"))
        os.chmod(n, 0o775)
        os.close(f)
        code = subprocess.call(n + " " + self.package, shell=True)
        os.unlink(n)
        if code == 0:
            return InstallerState.OK
        if code == 101:
            return InstallerState.INVALID_NAME
        return InstallerState.FAILED

    def remove(self, dry_run):
        print("NOTIMPL: You can't remove script-based things yet..")
