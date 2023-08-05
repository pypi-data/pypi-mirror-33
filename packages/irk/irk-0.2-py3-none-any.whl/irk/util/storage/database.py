from bisect import bisect_left

from . import etcfile

installed_database = []
packages = []
DB_FILE = etcfile.EtcFile("instdb")


def search_entry(package):
    i = bisect_left(packages, package)
    if i != len(packages) and packages[i] == package:
        return installed_database[i], i
    return None


def delete_entry(package):
    global packages, installed_database
    i = bisect_left(packages, package)
    if i != len(packages) and packages[i] == package:
        del installed_database[i]
        del packages[i]
    else:
        raise ValueError()


def insert_entry(e):
    global packages, installed_database
    i = bisect_left(packages, e[0])
    packages.insert(i, e[0])
    installed_database.insert(i, e)


def load_installed_database():
    global installed_database, packages
    packages = []
    installed_database = []
    if not DB_FILE.fullpath.exists():
        write_database()
    print("(Reading database... ", end="")
    with DB_FILE.open("r") as f:
        i = 0
        while True:
            line = f.readline()
            if line == "": break
            i += 1
            line = line[:-1]
            line = line.split(" ")
            packages.append(line[0])
            installed_database.append(line)
    print(f" {i} packages installed.)")


def write_database():
    global installed_database
    print("Writing package database... ", end="")
    with DB_FILE.open("w") as f:
        for i in installed_database:
            f.write(" ".join(i))
            f.write("\n")
    print("done.")
