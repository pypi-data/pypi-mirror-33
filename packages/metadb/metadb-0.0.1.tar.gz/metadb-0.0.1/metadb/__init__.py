from pymongo import MongoClient

from metaform import normalize, remap
from typology.ontology.wikidata import Concept

from .utils import DictList


TYPE = '_type'

NAMESPACE = '_names'
TYPESPACE = '_types'
TERMSPACE = '_terms'
DEFAULT_LANGUAGE = 'en'

"""
Comment:

TYPE is a reserved key for type reference.

NAMESPACE is used for registering new apps on database.
TYPESPACE is used for registering terms, and formats.
TERMSPACE is a collection for ontological terms.
"""


class MongoClient(MongoClient):

    def initialize(self, app, table):
        '''
        Example, to ensure exists APP='hello', TABLE='world', do:
        client = MongoClient().initialize(app='hello', table='world')
        '''

        if not self.app_exists(app):
            self.create_app(app)

        if not self.table_exists(table):
            self.create_table(table)

        return self

    def __init__(self, lang=DEFAULT_LANGUAGE):
        self.lang = lang
        ''' Creates base databases and tables if they don't exist.  '''
        super().__init__()

        # Make sure collection db['types']['NAMESPACE'] exists.
        if NAMESPACE not in self['types'].collection_names():
            self['types'].create_collection(NAMESPACE, validator= {
                '$and': [
                  {
                    "name": {'$type': "string", '$exists': True}
                  }
                ]
              }
            )

        # Make sure db['types'][NAMESPACE] instances have unique "name".
        self['types'][NAMESPACE].create_index("name", unique=True)

        # Make sure db['types'][TYPESPACE] exists:
        if TYPESPACE not in self['types'].collection_names():
            self['types'].create_collection(TYPESPACE, validator= {
                '$and': [
                  {
                    "name": {'$type': "string", '$exists': True}
                  }
                ]
              }
            )
        # Make sure db['types'][TYPESPACE] instances have unique "name".
        self['types'][TYPESPACE].create_index("name", unique=True)

        # Make sure collection db['types']['NAMESPACE'] exists.
        if TERMSPACE not in self['types'].collection_names():
            self['types'].create_collection(TERMSPACE, validator= {
                '$and': [
                  {
                    "name": {'$type': "string", '$exists': True}
                  }
                ]
              }
            )
        # Make sure db['types'][TYPESPACE] instances have unique "name".
        self['types'][TERMSPACE].create_index("name", unique=True)

        self.items = self['items']
        self.types = self['types']
        self.index = self['index']

    def get_namespace_from_type_name(self, type_name):
        return type_name.split('-')[0]

    def record_exists(self, db, collection, query):
        return bool(list(self[db][collection].find(query).limit(1)))

    def app_exists(self, name):
        # TODO: Deprecate
        return self.record_exists('types', NAMESPACE, {'name': name})

    def apps(self):
        return DictList(self['types'][NAMESPACE].find())

    def table_exists(self, name):
        return self.record_exists('types', TYPESPACE, {'name': name})

    def tables(self):
        return DictList(self['types'][TYPESPACE].find())

    def type_exists(self, data, table):
        return bool(self['types'][table].find_one(data))

    # TODO: Make into property.setter
    def create_app(self, name):
        ''' Registers a new namespace in `types._names`. '''
        namespace = self.get_namespace_from_type_name(name)
        self['types'][NAMESPACE].insert({'name': namespace})

    # TODO: Make into property.setter
    def create_table(self, name, spec={}):
        ''' Registers a new schema in `types`.'''
        # Check if name of schema isn't overlapping with NAMESPACE collection.
        if name.startswith(NAMESPACE):
            print('Error. Table name cannot start with token "{}"'.format(NAMESPACE))
            return

        if name.startswith(TYPESPACE):
            print('Error. Table name cannot start with token "{}"'.format(TYPESPACE))
            return

        if name.startswith(TERMSPACE):
            print('Error. Table name cannot start with token "{}"'.format(TERMSPACE))
            return

        # Check if namespace exists for this new collection.
        # e.g., name="app-1.0/model_name"
        #       namespace = "app"
        namespace = self.get_namespace_from_type_name(name)
        if not self['types'][NAMESPACE].find({'name': namespace}).limit(1).count():
            print("Error. App name {} doesn't exist yet.".format(namespace))
            return

        # Register the table as collection db['types'][name]
        self['types'][TYPESPACE].insert({'name': name})

        # Create table in `types` database with initial schema.
        if not name in self['types'].collection_names():
            self['types'][name].insert(spec)

        # Create table in `items` database with requirement to reference schema.
        self['items'].create_collection(name, validator= {
            '$and': [
              {
                TYPE: {'$type': "objectId", '$exists': True}
              }
            ]
          }
        )

        # Create table in `index` database with same name.
        self['index'].create_collection(name)

    def drop_table(self, name):
        self['index'][name].drop()
        self['items'][name].drop()
        self['types'][name].drop()
        self['types'][TYPESPACE].remove({'name': name})

    def drop_app(self, name):

        # If name was registered, then remove it, and its all attributes.
        if self['types'][NAMESPACE].find(
                {'name': name}).limit(1).count():

            self['types'][NAMESPACE].remove({'name':name})

            tables_to_remove = []
            for type_obj in self['types'][TYPESPACE].find():
                table_name = type_obj['name']
                if table_name.startswith(name+'-'):
                    self['index'][table_name].drop()
                    self['items'][table_name].drop()
                    self['types'][table_name].drop()
                    tables_to_remove.append(table_name)

            self['types'][TYPESPACE].remove({'name': {'$in': tables_to_remove}})

    def create_type(self, data, table):
        ''' Inserts a new type for data table '''
        if isinstance(data, dict) and isinstance(table, str):
            self.types[table].insert(data)

    def create_item(self, data, table, upsert=False):
        ''' Inserts a new record to `items`.

        if upsert=True, then doesn't create duplicates.
        '''

        if not self['types'][TYPESPACE].find({'name': table}).limit(1).count():
            print('Table `{}` not defined. Create table.'.format(table))
            return

        if TYPE in data.keys():
            print('Data has reserved key {}, cannot create item.'.format(TYPE))
            return

        # Get latest type object schema from the db['types'][table].
        schema = self['types'][table].find().sort([('$natural', -1)]).limit(1).next()

        data[TYPE] = schema['_id']

        if upsert:
            # Insert data
            self['items'][table].update(data, data, upsert=True)
            # Insert normalized data
            ndata = normalize(data, schema, storage=self)
            self['index'][table].update(ndata, ndata, upsert=True)
            # Terminate
            return

        # Insert data
        self['items'][table].insert(data)
        # Insert normalized data
        self['index'][table].insert(normalize(data, schema, storage=self))


    def update_item(self, data, table, match=None, update=None):
        '''
        :match: list, that provides the key_path to match [('key1', 0), ('key2', 1, 'key3')]
        :update: dict, that provides the key_path to update [(0, 'some1'), (0, 'some2')]

        If we find the item in the database, that matches the given data by keys in match,
        then we overwrite the values that intersect with keys provided in the update.
        '''

        if '_id' in data.keys():

            _id = data['_id']
            del data['_id']

            if '_type' in data.keys():
                _type = data['_type']
                del data['_type']

            match = {'_id': _id}
            update = {'$set': data}

            self['items'][table].update_one(match, update)

            # As new schema for the data is not provided,
            # the best we can do is to write the new keys:
            # TODO: check, if key names are available in self['types'][table].find_one(match)
            self['index'][table].update_one(match, update)
        else:
            print('NOT UPDATED')


    def remove_item(self):
        raise NotImplemented()


    def fetch_concepts(self, refresh=False):

        if refresh:
            query = self.types['_terms'].find()
        else:
            query = self.types['_terms'].find({'aliases': {"$exists" : False}})

        from progress.bar import Bar
        bar = Bar('Processing', max=query.count())
        for term in query:
            if term.get('url'):
                wikidata_token = 'https://www.wikidata.org/wiki/Q'
                if term['url'].startswith(wikidata_token):
                    concept_id = term['url'].split(wikidata_token)[-1].split('#')[0]
                    concept = Concept('Q'+concept_id)()

                    # aliases
                    aliases = {
                        lang: [alias.get('value') for alias in concept.aliases[lang]]
                        for i, lang in enumerate(concept.aliases)
                    }

                    if aliases:
                        self.types['_terms'].update_one(
                            {'_id': term['_id']},
                            {'$set': {'aliases': aliases}}
                        )

                    # descriptions
                    descriptions = {
                        lang: concept.descriptions[lang].get('value')
                        for i, lang in enumerate(concept.descriptions)
                    }

                    if descriptions:
                        self.types['_terms'].update_one(
                            {'_id': term['_id']},
                            {'$set': {'descriptions': descriptions}}
                        )

            bar.next()
        bar.finish()

    def set_format(self, term_url, data={'default': {'patterns': []}}):
        term = self.types['_terms'].find_one({'url': term_url})
        if term:
            self.types[TERMSPACE].update_one(
                {'_id': term['_id']},
                {'$set': {'formats.{}'.format(list(data.keys())[0]): list(data.values())[0]}}
            )
        else:
            print('Term not found. Cannot set format.')

    def find_term(self, word, lang=None):

        if not lang:
            lang = self.lang

        if lang == 'cn':
            lang = 'zh-hans'

        return self.types['_terms'].find(
                {'aliases.{}'.format(lang):
                     {'$regex': u'{}'.format(word)}})

    def keys_to_lang(self, data, lang):
        """
        Given:
        >>> data = {'https-www-wikidata-org-wiki-q1347367': {'https-www-wikidata-org-wiki-q11573': 1234}}
        >>> lang = 'en'

        Returns:
        >>> {"ability": {"meter": 1234}}
        """

        def visit(path, key, value):
            key_term = self.types['_terms'].find_one({'name': key})
            if key_term:
                key_aliases = key_term.get('aliases')
                if key_aliases:
                    key_translation = key_aliases.get(lang)

                    if key_translation:
                        return key_translation[0], value
            return key, value

        remapped = remap(data, visit=visit)

        return remapped
