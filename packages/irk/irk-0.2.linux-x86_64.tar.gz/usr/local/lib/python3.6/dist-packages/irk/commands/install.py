from irk.installers.common import InstallerState
from irk.util.proc import elevate
from irk.util.storage import resolv
from irk.util.storage.database import search_entry, insert_entry, installed_database, write_database


def try_to_install(resolver, package, dry_run, reinstall):
    installer = resolver.resolve_to_installer(package)
    for dep in installer.get_dependencies():
        print("Installing dependency {}".format(dep))
        install(dep, dry_run=dry_run, reinstall=reinstall)
    code = installer.install(dry_run)
    if code == InstallerState.HAS_DEPS:
        print("WARN: Detected dependency errors, attempting to installing dependencies")
        for dep in installer.get_dependencies():
            print("Installing dependency {}".format(dep))
            install(dep, dry_run, reinstall=reinstall)
        code = installer.install(dry_run)
    return code


def install(package, specific_resolver=None, dry_run=False, exclude_installers=(), reinstall=False):
    entry = search_entry(package)
    i = -1
    if entry is not None and not reinstall:
        return
    if entry is not None:
        entry, i = entry
    for resolver in resolv.get_matching_resolvers(package):
        resolver_name = resolver.get_resolver_name()
        if resolver_name in exclude_installers:
            print(f"Skipping installer {resolver_name}")
            continue
        if specific_resolver is None or resolver_name == specific_resolver:
            print(f"Using resolver {resolver.get_resolver_name()}")
            code = try_to_install(resolver, package, dry_run, reinstall)
            if code == InstallerState.OK:
                if not dry_run:
                    entry = (package, resolver_name)
                    if i == -1:
                        insert_entry(entry)
                    else:
                        installed_database[i] = entry
                print("Installed {}".format(package))
                write_database()
                return 0
            elif code == InstallerState.INVALID_NAME:
                print("Trying next resolver...")
                continue
            elif code == InstallerState.FAILED:
                return 1
            elif code == InstallerState.NEEDS_SUDO:
                print("ERR: You probably need to run me as sudo!")
                elevate()
                return 1
    print("ERR: Invalid package!")
    return 2


