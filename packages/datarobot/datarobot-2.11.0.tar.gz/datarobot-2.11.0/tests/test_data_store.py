from datetime import datetime
import responses

from datarobot import DataStore

from datarobot.utils import parse_time


@responses.activate
def test_list(data_stores_endpoint, data_stores_list_server_resp):
    responses.add(responses.GET, data_stores_endpoint, json=data_stores_list_server_resp)

    data_stores = DataStore.list()

    for data_store, server_payload in zip(data_stores, data_stores_list_server_resp['data']):
        assert data_store.id == server_payload['id']
        assert data_store.type == server_payload['type']
        assert data_store.canonical_name == server_payload['canonicalName']
        assert data_store.creator == server_payload['creator']
        assert data_store.updated == parse_time(server_payload['updated'])
        assert data_store.params.driver_id == server_payload['params']['driverId']
        assert data_store.params.jdbc_url == server_payload['params']['jdbcUrl']


@responses.activate
def test_get(data_stores_endpoint, postgresql_data_store_server_resp):
    data_store_id = postgresql_data_store_server_resp['id']
    responses.add(
        responses.GET,
        '{}{}/'.format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp
    )

    data_store = DataStore.get(data_store_id)

    assert data_store.id == postgresql_data_store_server_resp['id']
    assert data_store.type == postgresql_data_store_server_resp['type']
    assert data_store.canonical_name == postgresql_data_store_server_resp['canonicalName']
    assert data_store.creator == postgresql_data_store_server_resp['creator']
    assert data_store.updated == parse_time(postgresql_data_store_server_resp['updated'])
    assert data_store.params.driver_id == postgresql_data_store_server_resp['params']['driverId']
    assert data_store.params.jdbc_url == postgresql_data_store_server_resp['params']['jdbcUrl']


@responses.activate
def test_create(data_stores_endpoint, postgresql_data_store_server_resp):
    responses.add(responses.POST, data_stores_endpoint, json=postgresql_data_store_server_resp)

    data_store = DataStore.create(
        data_store_type=postgresql_data_store_server_resp['type'],
        canonical_name=postgresql_data_store_server_resp['canonicalName'],
        driver_id=postgresql_data_store_server_resp['params']['driverId'],
        jdbc_url=postgresql_data_store_server_resp['params']['jdbcUrl'],
    )

    assert data_store.id == postgresql_data_store_server_resp['id']
    assert data_store.type == postgresql_data_store_server_resp['type']
    assert data_store.canonical_name == postgresql_data_store_server_resp['canonicalName']
    assert data_store.creator == postgresql_data_store_server_resp['creator']
    assert data_store.updated == parse_time(postgresql_data_store_server_resp['updated'])
    assert data_store.params.driver_id == postgresql_data_store_server_resp['params']['driverId']
    assert data_store.params.jdbc_url == postgresql_data_store_server_resp['params']['jdbcUrl']


@responses.activate
def test_update(data_stores_endpoint, postgresql_data_store_server_resp):
    data_store_id = postgresql_data_store_server_resp['id']
    responses.add(
        responses.GET,
        '{}{}/'.format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp)
    updated_data_store_server_resp = dict(
        postgresql_data_store_server_resp,
        canonicalName='updated_canonical_name',
        params={
            'driverId': 'updated_driver_id',
            'jdbcUrl': 'updated_jdbc_url'
        }
    )
    responses.add(
        responses.PATCH,
        '{}{}/'.format(data_stores_endpoint, data_store_id),
        json=updated_data_store_server_resp)

    data_store = DataStore.get(data_store_id)

    data_store.update(
        canonical_name=updated_data_store_server_resp['canonicalName'],
        driver_id=updated_data_store_server_resp['params']['driverId'],
        jdbc_url=updated_data_store_server_resp['params']['jdbcUrl'],
    )

    assert data_store.id == updated_data_store_server_resp['id']
    assert data_store.type == updated_data_store_server_resp['type']
    assert data_store.canonical_name == updated_data_store_server_resp['canonicalName']
    assert data_store.creator == updated_data_store_server_resp['creator']
    assert data_store.updated == parse_time(postgresql_data_store_server_resp['updated'])
    assert data_store.params.driver_id == updated_data_store_server_resp['params']['driverId']
    assert data_store.params.jdbc_url == updated_data_store_server_resp['params']['jdbcUrl']


@responses.activate
def test_unable_to_change_type(data_stores_endpoint, postgresql_data_store_server_resp):
    data_store_id = postgresql_data_store_server_resp['id']
    responses.add(
        responses.GET,
        '{}{}/'.format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp)
    responses.add(
        responses.PATCH,
        '{}{}/'.format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp)

    data_store = DataStore.get(data_store_id)
    data_store._type = 'new_type'
    data_store.update()
    new_data_store = DataStore.get(data_store_id)

    assert new_data_store.type == postgresql_data_store_server_resp['type']


@responses.activate
def test_unable_to_change_creator(data_stores_endpoint, postgresql_data_store_server_resp):
    data_store_id = postgresql_data_store_server_resp['id']
    responses.add(
        responses.GET,
        '{}{}/'.format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp)
    responses.add(
        responses.PATCH,
        '{}{}/'.format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp)

    data_store = DataStore.get(data_store_id)
    data_store._creator = 'new_creator'
    data_store.update()
    new_data_store = DataStore.get(data_store_id)

    assert new_data_store.creator == postgresql_data_store_server_resp['creator']


@responses.activate
def test_unable_to_change_updated_time(data_stores_endpoint, postgresql_data_store_server_resp):
    data_store_id = postgresql_data_store_server_resp['id']
    responses.add(
        responses.GET,
        '{}{}/'.format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp)
    responses.add(
        responses.PATCH,
        '{}{}/'.format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp)

    data_store = DataStore.get(data_store_id)
    data_store._updated = datetime.now()
    data_store.update()
    new_data_store = DataStore.get(data_store_id)

    assert new_data_store.updated == parse_time(postgresql_data_store_server_resp['updated'])


@responses.activate
def test_delete(data_stores_endpoint, postgresql_data_store_server_resp):
    data_store_id = postgresql_data_store_server_resp['id']
    responses.add(
        responses.GET,
        '{}{}/'.format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp
    )
    delete_url = '{}{}/'.format(data_stores_endpoint, data_store_id)
    responses.add(responses.DELETE, delete_url)

    data_store = DataStore.get(data_store_id)
    data_store.delete()

    assert responses.calls[1].request.method == responses.DELETE
    assert responses.calls[1].request.url == delete_url


@responses.activate
def test_connection_test(data_stores_endpoint, postgresql_data_store_server_resp):
    data_store_id = postgresql_data_store_server_resp['id']
    responses.add(
        responses.GET,
        '{}{}/'.format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp
    )
    responses.add(
        responses.POST,
        '{}{}/test/'.format(data_stores_endpoint, data_store_id),
        json={'message': 'Connection successful'})

    data_store = DataStore.get(data_store_id)
    resp = data_store.test(username='my_username', password='my_password')

    assert resp['message'] == 'Connection successful'


@responses.activate
def test_schemas_list(data_stores_endpoint, postgresql_data_store_server_resp,
                      postgresql_schemas_list_server_resp):
    data_store_id = postgresql_data_store_server_resp['id']
    responses.add(
        responses.GET,
        '{}{}/'.format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp
    )
    responses.add(
        responses.POST,
        '{}{}/schemas/'.format(data_stores_endpoint, data_store_id),
        json=postgresql_schemas_list_server_resp
    )

    data_store = DataStore.get(data_store_id)
    resp = data_store.schemas(username='my_username', password='my_password')

    assert resp == postgresql_schemas_list_server_resp


@responses.activate
def test_tables_list(
        data_stores_endpoint, postgresql_data_store_server_resp, postgresql_tables_list_server_resp
):
    data_store_id = postgresql_data_store_server_resp['id']
    responses.add(
        responses.GET,
        '{}{}/'.format(data_stores_endpoint, data_store_id),
        json=postgresql_data_store_server_resp
    )
    responses.add(
        responses.POST,
        '{}{}/tables/'.format(data_stores_endpoint, data_store_id),
        json=postgresql_tables_list_server_resp
    )

    data_store = DataStore.get(data_store_id)
    resp = data_store.tables(username='my_username', password='my_password', schema='demo')

    assert resp == postgresql_tables_list_server_resp
