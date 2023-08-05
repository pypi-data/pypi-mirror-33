from metaform import normalize
from metadb import MongoClient, DictList

db = MongoClient()


def test_create_app():
    db.create_app('nanotech')
    assert db.app_exists('nanotech')

def test_create_table():
    db.create_table('nanotech-0.1/hello')
    assert db.table_exists('nanotech-0.1/hello')

def test_create_item():
    record = {'hello': 'world'}
    table = 'nanotech-0.1/hello'
    db.create_item(record, table)
    assert DictList([db.items[table].find_one()]).exists(record)

def test_drop_table():
    table = 'nanotech-0.1/hello'
    db.drop_table(table)
    assert db.items[table].find_one() is None

def test_drop_app():
    app = 'nanotech'
    db.drop_app(app)
    assert db.app_exists(app) == False

def test_normalization():
    item = {'a': {'b': '1,500.0'}}

    types = {
    'a':
         {'*': 'http://www.omegawiki.org/DefinedMeaning:377726',
               'b': {'*': "https://www.wikidata.org/wiki/Q11573|lambda x: float(x.replace(',', ''))"}
         }
    }

    assert normalize(item, None) == item

    assert normalize(item, types) == {
        'http-www-omegawiki-org-definedmeaning-377726':
            {'https-www-wikidata-org-wiki-q11573': 1500.0}
    }

def test_normalization_in_db():

    # Note: we need types database, which not only provides information about the ontological meaning,
    # but also provides information about the measure format, so that we know the datatype associated.

    db.drop_app('pets')
    db.create_app('pets')
    db.create_table('pets-dogs')

    # Let's say we have one dog item.
    item = {
        'name': 'Džetė',
        'color': 'black',
        'owner': 'Mindey',
        'skills': [
            {'name': 'catching mice', 'type': 'hunting'},
            {'name': 'catching cats', 'type': 'hunting'},

            {'name': 'identifying drunkards',
             'type': 'defense',
             'tests': [
                     {'date': '1989-05-12', 'level': 12},
                     {'date': '1993-01-02', 'level': 10}
                   ]
             }
        ]
    }

    # To keep data understandable, we identify the meaning of each item, and normalize it to some format.
    types = {
        'name':
            {'*': 'https://www.wikidata.org/wiki/Q82799|lambda _:_.title()'},
        'color':
            {'*': 'http://www.omegawiki.org/DefinedMeaning:661|lambda _:_.lower()'},
        'owner':
            {'*': 'https://www.wikidata.org/wiki/Q16869121|lambda _:_.lower()'},
        'skills': [
            {'*': 'https://www.wikidata.org/wiki/Q205961',
             'name': {'*': 'https://www.wikidata.org/wiki/Q82799|lambda _:_.lower()'},
             'type': {'*': 'https://www.wikidata.org/wiki/Q21146257|lambda _:_.lower()'},
             'tests': [
                  {'*': 'https://www.wikidata.org/wiki/Q27318',
                   'date': {'*': 'https://www.wikidata.org/wiki/Q205892|lambda _: converters.isoparse(_).isoformat()'},
                   'level': {'*': 'https://www.wikidata.org/wiki/Q1347367|lambda _: int(_)'}
                  },
             ]
        }]
    }

    db.types['pets-dogs'].insert(types)
    db.create_item(item, 'pets-dogs')
    assert DictList([db.index['pets-dogs'].find_one()]).exists(normalize(item, types))


def test_query_normalized_index():
    db.drop_app('pets')
    db.create_app('pets')
    db.create_table('pets-dogs')

    data = [
        {
            'name': 'Džetė',
            'color': 'black',
            'owner': 'Mindey',
            'skills': [
                {'name': 'catching cats', 'type': 'hunting'},

                {'name': 'identifying drunkards',
                 'type': 'defense',
                 'tests': [
                         {'date': '1993-01-02', 'level': 10}
                       ]
                 }
            ]
        },
        {
            'name': '小小',
            'color': '棕色',
            'owner': '思思',
            'skills': [
                {'name': '', 'type': 'hunting'},

                {'name': 'identifying drunkards',
                 'type': 'defense'
                 }
            ]
        },
        {
            'name': 'Nice',
            'color': 'balta',
            'owner': 'Meia',
            'skills': [
                {'name': 'catching mice', 'type': 'hunting'}
            ]
        }
    ]

    types = {
        'name':
            {'*': 'https://www.wikidata.org/wiki/Q82799|lambda _:_.title()'},
        'color':
            {'*': 'http://www.omegawiki.org/DefinedMeaning:661|lambda _:_.lower()'},
        'owner':
            {'*': 'https://www.wikidata.org/wiki/Q16869121|lambda _:_.lower()'},
        'skills': [
            {'*': 'https://www.wikidata.org/wiki/Q205961',
             'name': {'*': 'https://www.wikidata.org/wiki/Q82799|lambda _:_.lower()'},
             'type': {'*': 'https://www.wikidata.org/wiki/Q21146257|lambda _:_.lower()'},
             'tests': [
                  {'*': 'https://www.wikidata.org/wiki/Q27318',
                   'date': {'*': 'https://www.wikidata.org/wiki/Q205892|lambda _: converters.isoparse(_).isoformat()'},
                   'level': {'*': 'https://www.wikidata.org/wiki/Q1347367|lambda _: int(_)'}
                  },
             ]
        }]
    }

    db.types['pets-dogs'].insert(types)

    for item in data:
        db.create_item(item, 'pets-dogs')

    db.fetch_concepts()

    term = db.find_term('名称', 'cn').next()
    search_results = list(db.index['pets-dogs'].find({term['name']: {'$exists': True}}))
    assert len(search_results) == 3

    results = db.keys_to_lang(search_results, 'zh')

    expect_to_contain = [{
       '名稱': 'Džetė',
       'http-www-omegawiki-org-definedmeaning-661': 'black',
       '所有者': 'mindey',
       '技巧': [{'名稱': 'catching cats',
         'https-www-wikidata-org-wiki-q21146257': 'hunting'},
        {'名稱': 'identifying drunkards',
         'https-www-wikidata-org-wiki-q21146257': 'defense',
         '考試': [{'https-www-wikidata-org-wiki-q205892': '1993-01-02T00:00:00',
           'https-www-wikidata-org-wiki-q1347367': 10}]}],
       },
      {
       '名稱': '小小',
       'http-www-omegawiki-org-definedmeaning-661': '棕色',
       '所有者': '思思',
       '技巧': [{'名稱': '', 'https-www-wikidata-org-wiki-q21146257': 'hunting'},
        {'名稱': 'identifying drunkards',
         'https-www-wikidata-org-wiki-q21146257': 'defense'}]
       },
      {
       '名稱': 'Nice',
       'http-www-omegawiki-org-definedmeaning-661': 'balta',
       '所有者': 'meia',
       '技巧': [{'名稱': 'catching mice',
         'https-www-wikidata-org-wiki-q21146257': 'hunting'}]
     }]

    # This might actually fail, when wikidata is updated and contains these fields.
    assert all([DictList(results).exists(item) for item in expect_to_contain])


def test_create_format():
    db.drop_app('test')
    db.create_app('test')
    db.create_table('test-test')
    types = {
    'a':
         {'*': 'http://www.omegawiki.org/DefinedMeaning:377726',
               'b': {'*': "https://www.wikidata.org/wiki/Q11573|lambda x: float(x.replace(',', ''))"}
         }
    }
    if not db.type_exists(types, 'test-test'):
        db.create_type(types, 'test-test')
        item = {'a': {'b': '1,500.0'}}
        # create dummy item (that pulls the concept definitions)
        db.create_item(item, 'test-test')
        # but we should probably import all concepts on the moment when we define type...

    db.set_format(
        'https://www.wikidata.org/wiki/Q11573',
        {'numeric':
            {'rules': [
                {'max_digits': 5}
            ]}})

    db.set_format(
        'https://www.wikidata.org/wiki/Q11573',
        {'other':
            {'rules': [
                {'max_digits': 3}
            ]}})

    result = db.types['_terms'].find_one({'url': 'https://www.wikidata.org/wiki/Q11573'})

    assert result.get('formats') == {'numeric': {'rules': [{'max_digits': 5}]},
                                       'other': {'rules': [{'max_digits': 3}]}}
    # db.create_type(types, 'test-test')

def test_one_way_synchronization():
    db.drop_app('testing')
    db.create_app('testing')
    db.create_table('testing-items')

    source_state_1 = [ {'hello': 'world'} ]

    for record in source_state_1:
        db.create_item( record, 'testing-items', upsert=True )


    source_state_2 = [ {'hello': 'world'}, {'makes': 'sense'} ]

    for record in source_state_2:
        db.create_item( record, 'testing-items', upsert=True )


    source_state_3 = [ {'makes': 'cool'}, {'aligns': 'data'} ]

    for record in source_state_3:
        db.create_item( record, 'testing-items', upsert=True )

    # The result should be all non-duplicates.
    expected_result = [
        {'hello': 'world'},
        {'makes': 'sense'},
        {'makes': 'cool'},
        {'aligns': 'data'}
    ]

    assert list(db.items['testing-items'].find({}, {'_id': 0, '_type': 0})) == expected_result
