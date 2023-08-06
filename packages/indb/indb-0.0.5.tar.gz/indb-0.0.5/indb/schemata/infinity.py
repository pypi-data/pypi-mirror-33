import bs4
import yaml
import slugify
import mistune
import metawiki

from boltons.iterutils import remap
from typology.ontology.infinity import get_source

MAX_HEADER_LEVEL_TO_LOOK = 7

def get_schema(path):
    '''
    Retrieves all app schemas.

    :path: e.g.,
    https://github.com/mindey/indb/blob/master/apps/kbdmouse.md#key-presses

    '''
    page = get_source(path)

    anchor = None

    if '#' in path:
        url, anchor = path.rsplit('#', 1)


    soup = bs4.BeautifulSoup(
        mistune.markdown(page),
        'html.parser')


    headers = []

    for header_level in range(1, MAX_HEADER_LEVEL_TO_LOOK):
        headers.extend(soup.find_all('h{}'.format(header_level)))


    if anchor:

        header = None

        for header in headers:
            anchor_slug = slugify.slugify(header.text)

            if anchor_slug == anchor:
                break

        if header:
            content = header.find_next_sibling()

            if content:

                target = content.find(
                    'code', {'class': 'lang-yaml'})

                if target:

                    schema = keys_to_str(yaml.load(target.text))
                    schema = values_to_name(schema)

                    schema['_clients'] = available_clients(target.text)
                return schema

    else:

        schemas = {}

        for header in headers:
            content = header.find_next_sibling()

            target = content.find(
                'code', {'class': 'lang-yaml'})

            if target:
                anchor_slug = slugify.slugify(header.text)

                schema = keys_to_str(yaml.load(target.text))
                schema = values_to_name(schema)

                schema['_clients'] = available_clients(target.text)
                schemas[anchor_slug] = schema

        return schemas


def available_clients(data):
    splitters = ['clients:', 'clients=']

    for line in data.split('\n'):
        if line[:1] in ['#']:
            for splitter in splitters:
                if splitter in line:
                    return [str(scanner.strip()) for scanner in
                            line.rsplit(splitter,1)[-1].strip().split(',')]
    return []


def keys_to_str(data):

    def visit(path, key, value):
        return str(key), value

    remapped = remap(data, visit=visit)

    return remapped


def values_to_name(data):

    def visit(path, key, value):

        if isinstance(value, str):
            if metawiki.isurl(value):
                value = metawiki.url_to_name(value)

        return key, value

    remapped = remap(data, visit=visit)

    return remapped
