# db
This is an experimental MongoClient wrapper to explore a database patterns. Requires local [MongoDB](https://www.mongodb.com/) to run.

```
pip install metadb
```

## Basics
```python
from metadb import MongoClient

cli = MongoClient()

# Create an app
cli.create_app('hello')
cli.apps()

# Create a table
cli.create_table('hello-world')
cli.tables()

# Define normalization type
cli.types['hello-world'].insert(
    {'test': {'*': 'http://corresponding-concept-definition-url|lambda _: _.title()'}})

# Create a record
cli.create_item({'test': 'hello, world'}, 'hello-world')

# Raw data:
cli.items['hello-world'].find_one()
>>> {'_id': ObjectId('5ae156142b93bc3c6f60aa11'),
 '_type': ObjectId('5ae156112b93bc3c6f60aa10'),
 'test': 'hello, world'}

# Normalized data:
cli.index['hello-world'].find_one()
>>> {'_id': ObjectId('5ae156142b93bc3c6f60aa11'),
 '_type': ObjectId('5ae156112b93bc3c6f60aa10'),
 'https-www-wikidata-org-wiki-q45594': 'Hello, World'}

cli.drop_app('hello')
```


# General ideas
1. Let's say we have MongoDB (or any kind of key-value store).

2. Let's say we have databases:

- `items`
- `types`
- `index`

3. Let's say we have a constraint for uniqueness of names in reserved collection `db["types"]["_names"]` representing global namespace for apps registry:
```
use types

db.createCollection("_names", {
  validator: {
    $and: [
      {
        "name": {$type: "string", $exists: true}
      }
    ]
  }
})

db.getCollection('_names').createIndex( {"name": 1}, { unique: true } )
```

4. Let's say we have a convention, that every time we create a new colletion in `items` database, each each record has to have `._type` attribute, which is an object ID from mongodb.

For example:
```
use items

db.createCollection("app-1.0/model_name", {
  validator: {
    $and: [
      {
        "_type": {$type: "objectId", $exists: true}
      }
    ]
  }
})
```

5. Assume that the `._type` is like a foreign key reference to the corresponding type, stored in the `types` database in the collection with corresponding name.

```
use types

types["app-1.0/model_name"]
```

**Corollary:** This way, each item refers to its type, and types can have histories, rather than migrations of models.

E.g., whenever we change the schema for model, we can simply insert new instancde into `types` database, corresponding to new schema.

5.1. Assume that `db['types']['_types']` stores unique registered type names.


6. Assume each instance in any of collections of the `types` database, follows a pattern corresponding to the pattern of the instance in the `items` database, one level up the instance tree hierarchy, as so:

```
example:

{'a': {'b': {'c': 1}}}

pattern:
{'*': 'obj', 'a': {'b': {'c': {'*': 'int'}}}}

(Here, the asterisk keys specify information about records at each level, e.g., 'c' are records of 'int'.)
```

Meaning that, based on the example record provided, data may have a "mask" that specifies the value types:

```python
from boltons.iterutils import remap

RESERVED_SCHEMA_KEY = '*'

def generate_pattern(instance):
    """
    Generates pattern based on first record in data.
    """

    def parse_type(value):
        return type(value).__name__

    if isinstance(instance, list):
        if not instance:
            print("If Instnace is a list, it has to be non-empty.")
            return
        elif not isinstance(instance[0], dict):
            print("If Instnace is a list, it's first element has to be a dict.")
            return
    else:
        if isinstance(instance, dict):
            instance = [instance]
        else:
            print("Instance must be a dict, or a list of dict.")
            return

    def visit(path, key, value):
        if not any([isinstance(value, t) for t in [dict, list, tuple]]):
            return key, {RESERVED_SCHEMA_KEY: parse_type(value)}
        else:
            return key, value

    remapped = remap(instance, visit=visit)
    remapped[0][RESERVED_SCHEMA_KEY] = 'obj'
    return remapped[0]

generate_pattern({'a': {'b': 'c'}})
```

Suppose we replace and enrich such mask under asterisks, with information about ontological types by providing references (e.g., URLs) to ontological vocabularies, and data type normalization rules in tuples separated by `|` like `ontological type|conversion rules`, like so:

```
{'*': 'http://www.omegawiki.org/DefinedMeaning:377726|lambda x: x', 'a': {'b': {'*': "https://www.wikidata.org/wiki/Q11573|lambda x.replace(',', '')"}}}
```

*Note: for lack of MongoDBs ability to store pure URLs as keys, will store correct urls in the database `db['types']['_terms']`, with required uniqueness for 'name', as so:

```
use types

db.createCollection("_terms", {
  validator: {
    $and: [
      {
        "name": {$type: "string", $exists: true}
      }
    ]
  }
})

db.getCollection('_names').createIndex( {"name": 1}, { unique: true } )
```


**Corollary:** Every time we create a new type, we can create corresponding corresponding conversion rules and ontological-metadata, and use it to normalize data instances (hereafter - *normalized instances*), when writing them to `index` database where key is replaced with the urls from the mask, and the values are replaced by the digests of the conversion rules.

7. Let's store the normalized instances in the `index` database.

**Corollary:** We have a generic way to query datasets by concepts, and present their keys in arbitrary human languages for understanding and analytics.

**Corollary:** We can define a generalized SQL, which works for querying knowledge-bases by concepts like:

`SELECT * FROM (concept_id)`

E.g.:

`SELECT * FROM <HUMANS>`, `SELECT * FROM <BEST SUPPLIERS OF..>`, `SELECT * FROM <BEST PEOPLE FOR..>`

*Note:* it seems like something similar to [SPARQL](https://en.wikipedia.org/wiki/SPARQL), but for generalized concepts from all possible vocabularies, rather than one.

**Corollary:** The database thus constructed has properties:

```
...
```

I guess, that this kind of database would be convenient for creating generic scalable backends for a generic application, with both structured and unstructured data accessible for analytics through a unified interface.


Examples:

```
names = ['infinity']

collections = [
    'infinity-0.1/comments'
    'infinity-0.1/topics'
]

...
```
