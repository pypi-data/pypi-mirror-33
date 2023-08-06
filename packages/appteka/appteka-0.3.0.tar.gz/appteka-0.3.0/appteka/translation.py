""" Helper for localization. """

import locale
import gettext
from pkg_resources import resource_filename as resource


def _echo(text):
    return text


def init_translation(package_name, resource_name, module_name):
    """ Returns function for specifying of places to be translated. """
    lang = locale.getdefaultlocale()[0]
    gettext.install(module_name)

    try:
        trans = gettext.translation(
            module_name,
            resource(package_name, resource_name),
            languages=[lang],
        )
        return trans.gettext
    except (ImportError, FileNotFoundError):
        return _echo
