import enum


class InstallerState(enum.Enum):
    OK = 0x00,
    INVALID_NAME = 0x01,
    FAILED = 0x02,
    NEEDS_SUDO = 0x03,
    HAS_DEPS = 0x04


class Installer:
    def install(self, dry_run):
        return InstallerState.OK

    def remove(self, dry_run):
        return InstallerState.OK

    def get_dependencies(self):
        return []
