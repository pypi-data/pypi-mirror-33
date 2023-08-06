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
                's', # : scan (streaming read)
                'r', # : read
                'p'  # : print (streaming write)
                'w', # : write
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
        """

        # Initialization
        self.scanner = get_scanner(source, schema, client)
        self.printer = get_printer(source, schema, client)

        # Methods
        self.scan = self.scanner.scan
        self.read = self.scanner.read
        setattr(self, 'print',  getattr(self.printer, 'print'))
        self.write = self.printer.write
