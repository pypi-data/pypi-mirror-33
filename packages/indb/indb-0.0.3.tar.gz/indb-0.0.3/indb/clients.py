import io
import csv

from metaform import normalize

from typology.ontology.infinity import (
    get_source,
)

from .schemata.infinity import get_schema

from metadb import MongoClient
import metawiki




class Client(object):
    pass


class Scanner(Client):
    def __init__(self, schema, source=None):

        self.source = source

        if isinstance(schema, str):
            self.schema = get_schema(schema)
        else:
            self.schema = schema


    def scan(self, source, saveto=False):
        '''
        :ingest: update client storage
        '''
        pass

    def read(self, source, saveto=False):
        pass


class Printer(Client):
    def __init__(self, schema, source=None):
        if schema:
            schema = get_schema(schema)

    def print(self, source, update=False):
        '''
        :exgest: update server storage
        '''
        pass

    def write(self, source, update=False):
        pass


class Browser(Scanner):
    '''
    e.g., Selenium
    '''
    def __init__(self):
        pass


class Android(Scanner):
    '''
    e.g., Selendroid ( http://selendroid.io/ )
    '''
    def __init__(self):
        pass


def Windows(Scanner):
    '''
    e.g., TeamViewer as a UI client.
    '''
    def __init__(self):
        pass


def iOS(Scanner):
    '''
    e.g., Selendroid ( with extension )
    '''
    pass


class Api(Scanner):
    def __init__(self):
        pass


class RestAPI(Api):
    '''
    REST API endpoint, e.g., with slumber.
    '''
    pass


class JSONLines(Scanner):
    pass


class Csv(Scanner):

    def read(self, source=None, saveto=None):

        if source:
            data = get_source(source)
        elif self.source:
            data = get_source(self.source)
        else:
            raise Exception("No source.")

        f = io.StringIO(data)
        reader = csv.reader(f)

        records = [
            {str(i): elem for i, elem in enumerate(row)}
            for row in reader
        ]


        if saveto:

            app, _ = saveto.split('-', 1)

            db = MongoClient().initialize(app=app, table=saveto)

            for i, record in enumerate(records):
                db.create_item(record, saveto)

            print("Created {} records saved.".format(i+1))
            return

        else:

            normalized_records = normalize(records, [self.schema])

        return normalized_records


class Tsv(Csv):
    '''
    Tab separated values file or source stream.
    '''
    pass


class MongoDB(Scanner):
    '''
    MongoDB protocol.
    '''
    pass


class PostgreSQL(Scanner):
    '''
    PostgreSQL protocol.
    '''
    pass
