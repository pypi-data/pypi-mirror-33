from irk.installers.common import InstallerState
from irk.util.proc import elevate
from irk.util.storage import resolv
from irk.util.storage.database import search_entry, delete_entry, write_database


def remove(package, specific_resolver=None, dry_run=False, force=False):
    entry = search_entry(package)
    if entry is None and not force:
        print("ERR: That package is not installed. Run with -f/--force to bypass this (you will need to specify a "
              "resolver with -r)")
        return 1
    if force and specific_resolver is None:
        print("ERR: You must specify a resolver if forcefully removing a package")
        return 1
    if entry is not None and specific_resolver is None:
        specific_resolver = entry[0][1]
    for resolver in resolv.get_matching_resolvers(package):
        if specific_resolver is None or resolver.get_resolver_name() == specific_resolver:
            print(f"Using resolver {resolver.get_resolver_name()}")
            code = resolver.resolve_to_installer(package).remove(dry_run)
            if code == InstallerState.OK:
                print("Removed {}".format(package))
                if entry is not None:
                    delete_entry(package)
                write_database()
                return 0
            elif code == InstallerState.INVALID_NAME:
                return 1
            elif code == InstallerState.FAILED:
                return 1
            elif code == InstallerState.NEEDS_SUDO:
                print("ERR: You probably need to run me as sudo!")
                elevate()
                return 1
    print("ERR: Invalid package!")
    return 2