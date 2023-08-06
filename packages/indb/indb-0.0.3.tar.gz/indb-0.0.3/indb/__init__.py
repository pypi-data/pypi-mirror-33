import io
import sys

from .clients import *

from .utils import (
    get_scanner,
    get_printer
)

class IO(object):

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
        Exemple:
        >>> IO('<schema location>').<METHOD>('<data location>')

        OR:
        >>> KeysIO = IO(
            schema='<schema location>',
            source='<data location>')
        )
        >>> KeysIO.<METHOD>([params])

        E.g.:
        >>> KeysIO.read(saveto='my-keys')
        >>> KeysIO.write(update='your-keys')
        """

        # Initialization
        self.scanner = get_scanner(source, schema, client)
        self.printer = get_printer(source, schema, client)

        # Methods
        self.scan = self.scanner.scan
        self.read = self.scanner.read
        setattr(self, 'print',  getattr(self.printer, 'print'))
        self.write = self.printer.write
