from argparse import ArgumentParser
import json


def get_cli():
    """Construct a CLI parser for pif-ingestor"""
    parser = ArgumentParser(description="Ingest data files to Citrination")

    # Required:
    parser.add_argument('path',
                        help='Location of the file or directory to import')

    # Optional
    parser.add_argument('-f', '--format', default="auto",
                        help='Format of data to import, coresponding to the name of the converter extension')
    parser.add_argument("-r", "--recursive", action='store_true', default=False,
                        help="Recursively walk through path, ingesting all valid subdirectories")
    parser.add_argument('-d', '--dataset', type=int, default=None,
                        help='ID of the dataset into which to upload PIFs')
    parser.add_argument('--tags', nargs='+', default=None,
                        help='Tags to add to PIFs')
    parser.add_argument('-l', '--license', default=None,
                        help='License to attach to PIFs (string)')
    parser.add_argument('-c', '--contact', default=None,
                        help='Contact information (string)')
    parser.add_argument("-z", "--zip", default=None,
                        help="Zip to this file")
    parser.add_argument("-t", "--tar", default=None,
                        help="Tar to this file")
    parser.add_argument("--globus-collection", dest="globus_collection", default=None,
                        help="Globus Publish collection to upload files")
    parser.add_argument("-m", "--meta", default=None,
                        help="Meta-data in common format")
    # parser.add_argument('--log', default="WARN", dest="log_level",
    #                    help='Logging level')
    parser.add_argument('--args', dest="converter_arguments", default={}, type=json.loads,
                        help='Arguments to pass to converter (as JSON dictionary)')

    return parser

def drive_cli():
    from .core import main
    # Get direction from the user
    parser = get_cli()
    args = parser.parse_args()
    main(args)
