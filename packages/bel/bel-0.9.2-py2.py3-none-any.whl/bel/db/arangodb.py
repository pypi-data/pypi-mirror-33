import re
from arango import ArangoClient, ArangoError

import bel.utils as utils
from bel.Config import config

import logging
log = logging.getLogger(__name__)

edgestore_db_name = 'edgestore'
belns_db_name = 'belns'
belapi_db_name = 'belapi'

edgestore_nodes_name = 'nodes'  # edgestore node collection name
edgestore_edges_name = 'edges'  # edgestore edge collection name

equiv_nodes_name = 'equivalence_nodes'  # equivalence node collection name
equiv_edges_name = 'equivalence_edges'  # equivalence edge collection name
ortholog_nodes_name = 'ortholog_nodes'  # ortholog node collection name
ortholog_edges_name = 'ortholog_edges'  # ortholog edge collection name
belns_metadata_name = 'resources_metadata'  # BEL Resources metadata

belapi_settings_name = 'settings'  # BEL API settings and configuration
belapi_statemgmt_name = 'state_mgmt'  # BEL API state mgmt


def get_client(host=None, port=None, username=None, password=None, enable_logging=True):
    """Get arango client and edgestore db handle"""

    host = utils.first_true([host, config['bel_api']['servers']['arangodb_host'], 'localhost'])
    port = utils.first_true([port, config['bel_api']['servers']['arangodb_port'], 8529])
    username = utils.first_true([username, config['bel_api']['servers']['arangodb_username'], ''])
    password = utils.first_true([password, config.get('secrets', config['secrets']['bel_api']['servers'].get('arangodb_password')), ''])

    client = ArangoClient(
        protocol=config['bel_api']['servers']['arangodb_protocol'],
        host=host,
        port=port,
    )

    return client


def aql_query(db, query):
    """Run AQL query"""

    result = db.aql.execute(query)
    return result


def get_edgestore_handle(client, username=None, password=None):
    """Get Edgestore arangodb database handle"""

    username = utils.first_true([username, config['bel_api']['servers']['arangodb_username'], ''])
    password = utils.first_true([password, config.get('secrets', config['secrets']['bel_api']['servers'].get('arangodb_password', ''))])

    sys_db = client.db('_system', username=username, password=password)

    # Create a new database named "edgestore"
    if not sys_db.has_database(edgestore_db_name):
        if username and password:
            edgestore_db = client.create_database(
                name=edgestore_db_name,
                users=[{'username': username, 'password': password, 'active': True}],
            )
        else:
            edgestore_db = client.create_database(
                name=edgestore_db_name
            )

        nodes = edgestore_db.create_collection(edgestore_nodes_name, index_bucket_count=64)
        edges = edgestore_db.create_collection(edgestore_edges_name, edge=True, index_bucket_count=64)

        # Add a hash index to the collection
        nodes.add_hash_index(fields=['name'], unique=False)
        nodes.add_hash_index(fields=['components'], unique=False)  # add subject/object components as node properties

        edges.add_hash_index(fields=['name'], unique=False)
        edges.add_hash_index(fields=['metadata.nanopub_id'], unique=False)
        edges.add_hash_index(fields=['context[*].id'], unique=False)

        # TODO - add a skiplist index for _from? or _key? to be able to do paging?

        return edgestore_db

    if username and password:
        edgestore_db = client.db(edgestore_db_name, username=username, password=password)
    else:
        edgestore_db = client.db(edgestore_db_name)

    return edgestore_db


def get_belns_handle(client, username=None, password=None):
    """Get BEL namespace arango db handle"""

    username = utils.first_true([username, config['bel_api']['servers']['arangodb_username'], ''])
    password = utils.first_true([password, config.get('secrets', config['secrets']['bel_api']['servers'].get('arangodb_password')), ''])

    sys_db = client.db('_system', username=username, password=password)

    # Create a new database named "belns"
    if not sys_db.has_database(belns_db_name):
        if username and password:
            belns_db = client.create_database(
                name=belns_db_name,
                users=[{'username': username, 'password': password, 'active': True}],
            )
        else:
            belns_db = client.create_database(
                name=belns_db_name
            )

        resource_metadata = belns_db.create_collection(belns_metadata_name)
        equiv_nodes = belns_db.create_collection(equiv_nodes_name, index_bucket_count=64)
        ortholog_nodes = belns_db.create_collection(ortholog_nodes_name, index_bucket_count=64)
        equiv_edges = belns_db.create_collection(equiv_edges_name, edge=True, index_bucket_count=64)
        ortholog_edges = belns_db.create_collection(ortholog_edges_name, edge=True, index_bucket_count=64)

        # Add a hash index to the collection
        equiv_nodes.add_hash_index(fields=['name'], unique=True)
        ortholog_nodes.add_hash_index(fields=['name'], unique=True)

        return belns_db

    if username and password:
        belns_db = client.db(belns_db_name, username=username, password=password)
    else:
        belns_db = client.db(belns_db_name)

    return belns_db


def get_belapi_handle(client, username=None, password=None):
    """Get BEL API arango db handle"""

    username = utils.first_true([username, config['bel_api']['servers']['arangodb_username'], ''])
    password = utils.first_true([password, config.get('secrets', config['secrets']['bel_api']['servers'].get('arangodb_password')), ''])

    sys_db = client.db('_system', username=username, password=password)

    # Create a new database named "belapi"
    if not sys_db.has_database(belapi_db_name):
        if username and password:
            belapi_db = sys_db.create_database(
                name=belapi_db_name,
                users=[{'username': username, 'password': password, 'active': True}],
            )
        else:
            belapi_db = sys_db.create_database(
                name=belapi_db_name
            )

        belapi_db.create_collection(belapi_settings_name)
        belapi_db.create_collection(belapi_statemgmt_name)

        return belapi_db

    if username and password:
        belapi_db = client.db(belapi_db_name, username=username, password=password)
    else:
        belapi_db = client.db(belapi_db_name)

    return belapi_db


def delete_database(client, db_name, username=None, password=None):
    """Delete Arangodb database

    """

    username = utils.first_true([username, config['bel_api']['servers']['arangodb_username'], ''])
    password = utils.first_true([password, config.get('secrets', config['secrets']['bel_api']['servers'].get('arangodb_password')), ''])

    sys_db = client.db('_system', username=username, password=password)

    if sys_db.has_database(db_name):
        return sys_db.delete_database(db_name)
    else:
        log.warn('No arango database {db_name} to delete, does not exist')


# TODO  Convert ArangoDB loading to use bulk_import - this will be a significant refactor
#          since we can push any document via the generator but bulk_import only works with
#          a single collection at a time
# http://python-driver-for-arangodb.readthedocs.io/en/master/classes.html?highlight=bulk#arango.collections.Collection.import_bulk
def batch_load_docs(db, doc_iterator):
    """Batch load documents

    Args:
        db: ArangoDB client database handle
        doc_iterator:  function that yields (collection_name, doc_key, doc)
    """

    batch_size = 10000

    batch = db.batch(return_result=True)
    counter = 0
    results = []
    for (collection_name, doc) in doc_iterator:
        counter += 1

        # log.info(f'Cnt: {counter} Collection {collection_name} Doc {doc}')
        results.append(batch.collection(collection_name).insert(doc))
        if counter % batch_size == 0:
            log.debug(f'Commit batch  Count: {counter}')
            batch.commit()

            # TODO Add better error reporting

            # for result in results:
            #     if result:
            #         print(f'R: {result.result()}')

            results = []

            batch = db.batch(return_result=False)

    batch.commit()


def arango_id_to_key(_id):
    """Remove illegal chars from potential arangodb _key (id)

    Args:
        _id (str): id to be used as arangodb _key

    Returns:
        (str): _key value with illegal chars removed
    """

    key = re.sub("[^a-zA-Z0-9\_\-\:\.\@\(\)\+\,\=\;\$\!\*\'\%]+", '_', _id)
    if len(key) > 254:
        log.error(f'Arango _key cannot be longer than 254 chars: Len={len(key)}  Key: {key}')
    return key

