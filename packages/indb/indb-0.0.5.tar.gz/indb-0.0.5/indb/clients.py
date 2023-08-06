import io
import csv
import json
import metadb
import metaform
import metawiki

from typology.ontology.infinity import get_source

from .schemata.infinity import get_schema


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
    def __init__(self, schema, source=None, client=None):
        if schema:
            schema = get_schema(schema)
        if client:
            self.client = client

    def print(self, source, update=False):
        '''
        :exgest: update server storage
        '''
        pass

    def write(self, source, update=False):
        pass


class DictList(Scanner):
    '''
    Reads data, where each record may be the same, or
    different, but have the schema key to separate them out
    (e.g., such as in the SCANME.md files).
    '''

    def read(self, source=None, saveto=None, app='', key='model'):
        '''
        :key: only used, when :app: is not empty. In that case,
        we assume that the data is multischema, and there is some
        key that represents each schema in the precursor of schema name.
        '''
        if source:
            data = get_source(source)
        elif self.source:
            data = get_source(self.source)
        else:
            raise Exception("No source.")

        records = json.loads(data)

        if not app:

            if not saveto:
                raise Exception('Neither `app`, nor `saveto` location parameter provided.')

            if '-' not in saveto[1:-1]:
                raise Exception('saveto has to include a hyphen to separate app name from table name')

            app, _ = saveto.split('-', 1)

            db = metadb.MongoClient().initialize(app=app, table=saveto, types=self.schema)

            for record in records:
                db.create_item(record, saveto)

            print("{} records saved.".format(i+1))
            return

        # else:

        schemata = self.schema

        db = metadb.MongoClient()

        # initialize                                           #
        if not db.app_exists(app):                             # TODO:
            db.create_app(app)                                 #
                                                               #  Move to Scanner...?
        # create tables and schemas for tables                 #
        for skey in schemata.keys():                           # (but we should not create
            table = '{}-{}'.format(app,skey)                   #  tables, if there is no
                                                               #  write operations)
            if not db.table_exists(table):                     #
                db.create_table(table)                         #  Move to metadb...?
                                                               #  [.schemata functionality?]
            if not db.latest_type_is(schemata[skey], table):   #
                db.create_type(schemata[skey], table)          #

        # write records to tables
        fail_count = 0
        for i, record in enumerate(records):
            model = record.get(key)
            if model:
                skey = metaform.utils.slugify(model)
                if skey:
                    # choose table
                    table = '{}-{}'.format(app, skey)
                    db.create_item(record, table)
            else:
                fail_count += 1

        if fail_count:
            print('Notice: Failed to detect schema for '+\
                  '{} out of {} records.'.format(
                    fail_count, i+1))

        print("{} records saved.".format(i+1-fail_count))
        return


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

            db = metadb.MongoClient().initialize(app=app, table=saveto, types=self.schema)
            # Needs to assure that schema exists #

            for i, record in enumerate(records):
                db.create_item(record, saveto)

            print("Created {} records saved.".format(i+1))
            return

        else:

            normalized_records = metaform.normalize(records, [self.schema])

        return normalized_records


class Tsv(Csv):
    '''
    Tab separated values file or source stream.
    '''
    pass


class PostgreSQL(Scanner):
    '''
    PostgreSQL protocol.
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


# Higher order clients

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

class ReactJSApp(Client):
    '''
    A reactJS application
    '''
    pass


class RESTAPI(Client):
    '''
    General prototype ofr a RestAPI.
    # A bit like what WolframAlpha demoed one-liner to create a Rest API.
    '''

    pass


class DjangoRESTFrameWorkAPI(RESTAPI):
    '''
    A REST API implemented by Django Rest Framework.
    '''
    pass



class DjangoManager(Client):
    '''
    Manages Django from its environment.
    '''
    def __init__(self, server, location, initialization):
        pass

    def dump_data(self, server, path):
        # playbook =
        pass
