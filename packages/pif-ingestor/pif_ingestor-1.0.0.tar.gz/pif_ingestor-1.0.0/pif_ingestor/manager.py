import itertools
import stevedore
import logging
from types import GeneratorType

from pypif.obj import System


def _callback(manager, entrypoint, exception):
    """Log errors in loading extensions as warnings"""
    logging.warning("Failed to load '{}' due to {}".format(entrypoint, exception))
    return


class IngesterManager:
    """Load ingest extensions and invoke them on demand"""

    def __init__(self):
        self.extension_manager = stevedore.extension.ExtensionManager(
            namespace='citrine.dice.converter',
            invoke_on_load=False,
            on_load_failure_callback=_callback
        )

    def run_extension(self, name, path, args):
        """Run extension by name on path with arguments"""
        if name in self.extension_manager:
            extension = self.extension_manager[name]
            pifs = extension.plugin.convert([path], **args)
            return pifs
        else:
            logging.error("{} is an unknown format\nAvailable formats: {}".format(name, self.extension_manager.names()))
            exit(1)

    def run_extensions(self, files, args={}, include=None, exclude=[]):
        """Run any extensions in include but not exclude

        Returns list of pifs converted.
        """
        if not include:
            include = self.extension_manager.entry_points_names()
        include = [x for x in include if x in self.extension_manager and x not in exclude]

        for name in include:
            extension = self.extension_manager[name]
            try:
                pifs = extension.plugin.convert(files, **args)
                # Return value from convert can be System, list of Systems, or generator
                # If System, make into list
                if isinstance(pifs, System):
                    pifs = [pifs]
                # Get first item, if there is one
                if isinstance(pifs, GeneratorType):
                    try:
                        first_pif = next(pifs)
                    except StopIteration:
                        first_pif = None
                    else:
                        # Reconstitute generator
                        pifs = itertools.chain([first_pif], pifs)
                elif isinstance(pifs, list):
                    try:
                        first_pif = pifs[0]
                    except IndexError:
                        first_pif = None
                else:
                    raise TypeError("Unexpected return type '{}' from extension '{}'".format(str(type(pifs)), name))
                # TODO: make this selection logic smarter
                if first_pif:
                    return pifs
            except Exception:
                pass
        logging.warning("None of these ingesters worked: {}".format(include))
        return []
