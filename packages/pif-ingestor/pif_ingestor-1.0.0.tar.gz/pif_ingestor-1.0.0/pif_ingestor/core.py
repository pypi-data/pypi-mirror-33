from .ui import get_cli
from .manager import IngesterManager
from .enrichment import add_tags, add_license, add_contact
from .uploader import upload
from .packager import create_package
from .globus import push_to_globus
import os.path
from os import walk, listdir
from pypif import pif
from pypif.obj.system import System
import json
import logging
import types
from .ext.matmeta_wrapper import add_metadata
from pypif_sdk.func import replace_by_key


def _stream_write(fname, pifs_iterable):
    with open(fname, "w") as f:
        f.write("[\n")
        first = True
        for p in pifs_iterable:
            if not first:
                f.write(",\n")
            first = False
            pif.dump(p, f)
        f.write("\n]")


def _handle_pif(path, ingest_name, convert_args, enrich_args, metadata, ingest_manager, path_replace):
    """Ingest and enrich pifs from a path, returning affected paths"""
    # Run an ingest extension
    if ingest_name == "auto":
        pifs = ingest_manager.run_extensions([path], convert_args)
    else:
        pifs = ingest_manager.run_extension(ingest_name, path, convert_args)

    if isinstance(pifs, System):
        pifs = [pifs]

    if len(metadata) > 0:
        pifs = [add_metadata(x, metadata) for x in pifs]

    if len(path_replace) > 0:
        pifs = [replace_by_key(x, "relative_path", path_replace, new_key="url", remove=False) for x in pifs]

    # Perform enrichment
    add_tags(pifs, enrich_args['tags'])
    add_license(pifs, enrich_args['license'])
    add_contact(pifs, enrich_args['contact'])

    # Write the pif
    if os.path.isfile(path):
        pif_name = "{}_{}".format(path, "pif.json")
        res = [path, pif_name]
    else:
        pif_name = os.path.join(path, "pif.json")
        res = [path]

    _stream_write(pif_name, pifs)
    logging.info("Created pif at {}".format(pif_name))

    return res


def _enumerate_files(path, recursive):
    if os.path.isfile(path):
        return [path]
    if os.path.isdir(path) and not recursive:
        return [x for x in listdir(path) if os.path.isfile(x)]
    res = []
    for root, dirs, files in walk(path):
        res.extend(os.path.join(root, x) for x in files)
    return res 


def main(args):
    """Main driver for pif-ingestor"""

    enrichment_args = {
        'tags':    args.tags,
        'license': args.license,
        'contact': args.contact
    }

    # Load the ingest extensions
    ingest_manager = IngesterManager()

    path_replace = {}
    if args.globus_collection:
        globus_remap = push_to_globus(_enumerate_files(args.path, args.recursive), collection=args.globus_collection)
        path_replace = {k: v["http_url"] for k, v in globus_remap.items() if "http_url" in v}

    metadata = {}
    if args.meta:
        with open(args.meta, "r") as f:
            metadata = json.load(f) 

    all_files = []
    exceptions = {}
    if args.recursive:
        for root, dirs, files in walk(args.path):
            try:
                new = _handle_pif(root, args.format, args.converter_arguments, enrichment_args, metadata, ingest_manager, path_replace)
                all_files.extend(new)
            except Exception as err:
                exceptions[root] = err
    else:
        all_files.extend(_handle_pif(args.path, args.format, args.converter_arguments, enrichment_args, metadata, ingest_manager, path_replace))

    if len(all_files) == 0 and len(exceptions) > 0:
        raise ValueError("Unable to parse any subdirectories.  Exceptions:\n{}".format(
            "\n".join(["{}: {}".format(k, str(v)) for k, v in exceptions.items()]))
        )

    with open("ingestor.log", "w") as f:
        f.write("Exceptions:\n")
        for root, err in exceptions.items():
            f.write("{}: {}\n".format(root, str(err)))

    # Upload the pif and associated files
    if args.dataset:
        upload(all_files, args.dataset)

    if args.zip:
        if args.zip[-4:] == ".zip":
            zipname = args.zip
        else:
            zipname = args.zip + ".zip"
        create_package(all_files, zipname, format="zip")

    if args.tar:
        if args.tar[-4:] == ".tar":
            tarname = args.tar
        else:
            tarname = args.tar + ".tar"
        create_package(all_files, tarname, format="tar")
