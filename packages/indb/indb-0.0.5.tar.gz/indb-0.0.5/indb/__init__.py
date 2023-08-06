import io
import sys

from .clients import *

from .utils import (
    get_scanner,
    get_printer
)

class OOIO:

    def __init__(
            self,
            schema,
            source=None,
            client=None,
            methods=[
                'r', # : read,
                'w', # : write,
                's', # : scan (streaming read)
                'p'  # : print (streaming write)
            ]):
        """
        :app: str without hyphens - means, that client represents an
        app in the metadb, and the record of schema has
        multiple schemas, and should be written into separate tables
        of same one app, and the app has to be non-empty string.

        Exemple:
        >>> IO('<schema location>').<METHOD>('<data location>')

        OR:
        >>> KeysIO = OOIO(
            schema='<schema location>',
            source='<data location>'
            )
        >>> KeysIO.<METHOD>([params])

        E.g.:
        >>> KeysIO.read(saveto='my-keys')
        >>> KeysIO.write(update='your-keys')

        >>> BigIO = OOIO(
            app='myapp',
            schema='<schema location>',
            source='<data location>'
            )
        >>> BigIO.read(saveto='appname')
        """

        # Initialization
        self.scanner = get_scanner(source, schema, client)
        self.printer = get_printer(source, schema, client)

        # Methods
        self.scan = self.scanner.scan
        self.read = self.scanner.read
        setattr(self, 'print',  getattr(self.printer, 'print'))
        self.write = self.printer.write
