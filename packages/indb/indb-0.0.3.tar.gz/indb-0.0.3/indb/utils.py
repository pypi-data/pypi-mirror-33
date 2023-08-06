import requests
import mistune
import slugify
import yaml
import bs4
import sys

# from typology.ontology.infinity import get_concept, get_source

from .schemata.infinity import get_schema



def get_printer(source, schema, printer=None):
    class_name = 'Printer'

    try:
        printer = getattr(sys.modules['indb.clients'], class_name)
    except:
        raise Exception("The scanner '{}' not found.".format(class_name))

    return printer


def get_scanner(source, schema, scanner=None):

    if isinstance(schema, str):
        schema = get_schema(schema)

    if not isinstance(schema, dict):
        print(schema)
        raise Exception("Schema should be a dict.")

    # scanner prep
    if scanner is None:
        if '_clients' in schema.keys():
            scanners = schema.get('_clients')
            if scanners:
                # Use first scanner by default
                scanner = scanners[0]
        else:
            raise Exception('No scanner specified.')

    # Once we have the scanner string representation, we get it's class.

    import_path, class_name = scanner.rsplit('.',1)

    local_scanners = ['', 'indb', 'indb.clients']

    if import_path in local_scanners:
        try:
            scanner = getattr(sys.modules['indb.clients'], class_name)
        except:
            raise Exception("The scanner '{}' not found.".format(class_name))

    # Once we have the scanner class, we get data, and instantiate a specific scanner.
    if source:
        return scanner(schema, source)
    else:
        return scanner(schema)

