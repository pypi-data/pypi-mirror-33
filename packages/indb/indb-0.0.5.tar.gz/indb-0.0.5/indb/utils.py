import requests
import mistune
import slugify
import yaml
import bs4
import sys

# from typology.ontology.infinity import get_concept, get_source

from .schemata.infinity import get_schema



def get_printer(data, schema, client=None):
    class_name = 'Printer'

    try:
        printer = getattr(sys.modules['indb.clients'], class_name)
    except:
        raise Exception("The client '{}' not found.".format(class_name))

    return printer


def get_scanner(source, schema, client=None):

    if isinstance(schema, str):
        schema = get_schema(schema)

    if not isinstance(schema, dict):
        print(schema)
        raise Exception("Schema should be a dict.")

    # client prep
    if client is None:
        if '_clients' in schema.keys():
            clients = schema.get('_clients')
            if clients:
                # Use first client by default
                client = clients[0]
            else:
                raise Exception('No client gettable.')
        else:
            raise Exception('No client specified.')

    # Once we have the client string representation, we get it's class.
    import_path, class_name = client.rsplit('.',1)

    local_clients = ['', 'indb', 'indb.clients']

    if import_path in local_clients:
        try:
            client = getattr(sys.modules['indb.clients'], class_name)
        except:
            raise Exception("The client '{}' not found.".format(class_name))

    # Once we have the client class, we get data, and instantiate a specific client.
    if source:
        return client(schema, source)
    else:
        return client(schema)

