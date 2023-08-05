from os import walk
import os.path
import zipfile
import tarfile


def _add_to_package(arg, dirname, names):
    """Helper function for os.walk"""
    for name in names:
        full_name = os.path.join(dirname, name)
        if full_name not in arg["members"]:
            arg["file"].write(full_name)
            arg["members"].append(full_name)


def create_package(paths, filename, format="tar"):
    """Package paths into a zip or tar file"""
    members = []
    if format == "tar":
        f = tarfile.TarFile.open(filename, "w")
    elif format == "zip":
        f = zipfile.ZipFile(filename, "w")
    else:
        raise ValueError("Expected format to be 'zip' or 'tar'")
    args = {"file": f, "members": members}
    for path in paths:
        for root, dirs, files in walk(path):
            _add_to_package(args, root, files)
    f.close()
