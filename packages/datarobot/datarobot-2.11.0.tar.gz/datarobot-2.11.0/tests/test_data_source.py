from datetime import datetime
import responses

from datarobot import DataSource, DataSourceParameters
from datarobot.utils import parse_time


@responses.activate
def test_list(data_sources_endpoint, data_sources_list_server_resp):
    responses.add(responses.GET, data_sources_endpoint, json=data_sources_list_server_resp)

    data_sources = DataSource.list()

    for data_source, server_payload in zip(data_sources, data_sources_list_server_resp['data']):
        assert data_source.id == server_payload['id']
        assert data_source.type == server_payload['type']
        assert data_source.canonical_name == server_payload['canonicalName']
        assert data_source.creator == server_payload['creator']
        assert data_source.updated == parse_time(server_payload['updated'])
        assert data_source.params.data_store_id == server_payload['params']['dataStoreId']
        # assert params are the same
        params = data_source.params
        srv_params = server_payload['params']
        assert params.table == (srv_params['table'] if 'table' in srv_params else None)
        assert params.schema == (srv_params['schema'] if 'schema' in srv_params else None)
        assert params.partition_column == \
            (srv_params['partitionColumn'] if 'partitionColumn' in srv_params else None)
        assert params.query == (srv_params['query'] if 'query' in srv_params else None)
        assert params.fetch_size == \
            (srv_params['fetchSize'] if 'fetchSize' in srv_params else None)


@responses.activate
def test_get(data_sources_endpoint, diagnostics_data_source_server_resp):
    data_source_id = diagnostics_data_source_server_resp['id']
    responses.add(
        responses.GET,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=diagnostics_data_source_server_resp
    )

    data_source = DataSource.get(data_source_id)

    assert data_source.id == diagnostics_data_source_server_resp['id']
    assert data_source.type == diagnostics_data_source_server_resp['type']
    assert data_source.canonical_name == diagnostics_data_source_server_resp['canonicalName']
    assert data_source.creator == diagnostics_data_source_server_resp['creator']
    assert data_source.updated == parse_time(diagnostics_data_source_server_resp['updated'])
    assert data_source.params.data_store_id ==\
        diagnostics_data_source_server_resp['params']['dataStoreId']
    # assert params are the same
    params = data_source.params
    srv_params = diagnostics_data_source_server_resp['params']
    assert params.data_store_id == srv_params['dataStoreId']
    assert params.query == srv_params['query']


@responses.activate
def test_create_from_query(data_sources_endpoint, diagnostics_data_source_server_resp):
    responses.add(responses.POST, data_sources_endpoint, json=diagnostics_data_source_server_resp)
    params = DataSourceParameters(
        data_store_id=diagnostics_data_source_server_resp['params']['dataStoreId'],
        query=diagnostics_data_source_server_resp['params']['query']
    )

    data_source = DataSource.create(
        data_source_type=diagnostics_data_source_server_resp['type'],
        canonical_name=diagnostics_data_source_server_resp['canonicalName'],
        params=params
    )

    assert data_source.id == diagnostics_data_source_server_resp['id']
    assert data_source.type == diagnostics_data_source_server_resp['type']
    assert data_source.canonical_name == diagnostics_data_source_server_resp['canonicalName']
    assert data_source.creator == diagnostics_data_source_server_resp['creator']
    assert data_source.updated == parse_time(diagnostics_data_source_server_resp['updated'])
    # assert params are the same
    params = data_source.params
    srv_params = diagnostics_data_source_server_resp['params']
    assert params.data_store_id == srv_params['dataStoreId']
    assert params.query == srv_params['query']
    assert params.partition_column is None
    assert params.table is None
    assert params.schema is None
    assert params.fetch_size is None


@responses.activate
def test_create_from_table(
    data_sources_endpoint, airlines10mb_1000_records_data_source_server_resp
):
    del airlines10mb_1000_records_data_source_server_resp['params']['fetchSize']
    responses.add(responses.POST, data_sources_endpoint,
                  json=airlines10mb_1000_records_data_source_server_resp)
    params = DataSourceParameters(
        data_store_id=airlines10mb_1000_records_data_source_server_resp['params']['dataStoreId'],
        table=airlines10mb_1000_records_data_source_server_resp['params']['table']
    )

    data_source = DataSource.create(
        data_source_type=airlines10mb_1000_records_data_source_server_resp['type'],
        canonical_name=airlines10mb_1000_records_data_source_server_resp['canonicalName'],
        params=params
    )

    assert data_source.id == airlines10mb_1000_records_data_source_server_resp['id']
    assert data_source.type == airlines10mb_1000_records_data_source_server_resp['type']
    assert data_source.canonical_name == \
        airlines10mb_1000_records_data_source_server_resp['canonicalName']
    assert data_source.creator == airlines10mb_1000_records_data_source_server_resp['creator']
    assert data_source.updated == \
        parse_time(airlines10mb_1000_records_data_source_server_resp['updated'])
    # assert params are the same
    params = data_source.params
    srv_params = airlines10mb_1000_records_data_source_server_resp['params']
    assert params.data_store_id == srv_params['dataStoreId']
    assert params.table == srv_params['table']
    assert params.partition_column is None
    assert params.query is None
    assert params.schema is None
    assert params.fetch_size is None


@responses.activate
def test_create_from_table_limited_with_fetch_size(
    data_sources_endpoint, airlines10mb_1000_records_data_source_server_resp
):
    responses.add(responses.POST, data_sources_endpoint,
                  json=airlines10mb_1000_records_data_source_server_resp)
    params = DataSourceParameters(
        data_store_id=airlines10mb_1000_records_data_source_server_resp['params']['dataStoreId'],
        table=airlines10mb_1000_records_data_source_server_resp['params']['table'],
        fetch_size=airlines10mb_1000_records_data_source_server_resp['params']['fetchSize']
    )

    data_source = DataSource.create(
        data_source_type=airlines10mb_1000_records_data_source_server_resp['type'],
        canonical_name=airlines10mb_1000_records_data_source_server_resp['canonicalName'],
        params=params
    )

    assert data_source.id == airlines10mb_1000_records_data_source_server_resp['id']
    assert data_source.type == airlines10mb_1000_records_data_source_server_resp['type']
    assert data_source.canonical_name == \
        airlines10mb_1000_records_data_source_server_resp['canonicalName']
    assert data_source.creator == airlines10mb_1000_records_data_source_server_resp['creator']
    assert data_source.updated == \
        parse_time(airlines10mb_1000_records_data_source_server_resp['updated'])
    # assert params are the same
    params = data_source.params
    srv_params = airlines10mb_1000_records_data_source_server_resp['params']
    assert params.data_store_id == srv_params['dataStoreId']
    assert params.table == srv_params['table']
    assert params.fetch_size == srv_params['fetchSize']
    assert params.partition_column is None
    assert params.query is None
    assert params.schema is None


@responses.activate
def test_create_from_table_specific_schema(
    data_sources_endpoint, airlines10mb_data_source_server_resp
):
    responses.add(responses.POST, data_sources_endpoint,
                  json=airlines10mb_data_source_server_resp)
    params = DataSourceParameters(
        data_store_id=airlines10mb_data_source_server_resp['params']['dataStoreId'],
        table=airlines10mb_data_source_server_resp['params']['table'],
        schema=airlines10mb_data_source_server_resp['params']['schema'],
    )

    data_source = DataSource.create(
        data_source_type=airlines10mb_data_source_server_resp['type'],
        canonical_name=airlines10mb_data_source_server_resp['canonicalName'],
        params=params
    )

    assert data_source.id == airlines10mb_data_source_server_resp['id']
    assert data_source.type == airlines10mb_data_source_server_resp['type']
    assert data_source.canonical_name == \
        airlines10mb_data_source_server_resp['canonicalName']
    assert data_source.creator == airlines10mb_data_source_server_resp['creator']
    assert data_source.updated == \
        parse_time(airlines10mb_data_source_server_resp['updated'])
    # assert params are the same
    params = data_source.params
    srv_params = airlines10mb_data_source_server_resp['params']
    assert params.data_store_id == srv_params['dataStoreId']
    assert params.table == srv_params['table']
    assert params.schema == srv_params['schema']
    assert params.partition_column is None
    assert params.query is None
    assert params.fetch_size is None


@responses.activate
def test_create_from_table_with_partition_column(
    data_sources_endpoint, airlines10mb_data_source_server_resp
):
    del airlines10mb_data_source_server_resp['params']['schema']
    airlines10mb_data_source_server_resp['params']['partitionColumn'] = 'part_column'
    responses.add(responses.POST, data_sources_endpoint,
                  json=airlines10mb_data_source_server_resp)
    params = DataSourceParameters(
        data_store_id=airlines10mb_data_source_server_resp['params']['dataStoreId'],
        table=airlines10mb_data_source_server_resp['params']['table'],
        partition_column=airlines10mb_data_source_server_resp['params']['partitionColumn'],
    )

    data_source = DataSource.create(
        data_source_type=airlines10mb_data_source_server_resp['type'],
        canonical_name=airlines10mb_data_source_server_resp['canonicalName'],
        params=params
    )

    assert data_source.id == airlines10mb_data_source_server_resp['id']
    assert data_source.type == airlines10mb_data_source_server_resp['type']
    assert data_source.canonical_name == \
        airlines10mb_data_source_server_resp['canonicalName']
    assert data_source.creator == airlines10mb_data_source_server_resp['creator']
    assert data_source.updated == \
        parse_time(airlines10mb_data_source_server_resp['updated'])
    # assert params are the same
    params = data_source.params
    srv_params = airlines10mb_data_source_server_resp['params']
    assert params.data_store_id == srv_params['dataStoreId']
    assert params.table == srv_params['table']
    assert params.partition_column == srv_params['partitionColumn']
    assert params.schema is None
    assert params.query is None
    assert params.fetch_size is None


@responses.activate
def test_update_to_table(
    data_sources_endpoint,
    diagnostics_data_source_server_resp,
    airlines10mb_1000_records_data_source_server_resp
):
    data_source_id = diagnostics_data_source_server_resp['id']
    responses.add(
        responses.GET,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=diagnostics_data_source_server_resp)
    updated_params = DataSourceParameters(
        table=airlines10mb_1000_records_data_source_server_resp['params']['table'],
        fetch_size=airlines10mb_1000_records_data_source_server_resp['params']['fetchSize']
    )
    updated_data_source_server_resp = dict(
        diagnostics_data_source_server_resp,
        canonicalName='updated_canonical_name',
        params=updated_params.collect_payload()
    )
    updated_data_source_server_resp['params']['dataStoreId'] = \
        diagnostics_data_source_server_resp['params']['dataStoreId']
    responses.add(
        responses.PATCH,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=updated_data_source_server_resp)
    data_source = DataSource.get(data_source_id)

    data_source.update(
        canonical_name=updated_data_source_server_resp['canonicalName'],
        params=updated_params
    )

    assert data_source.id == updated_data_source_server_resp['id']
    assert data_source.type == updated_data_source_server_resp['type']
    assert data_source.canonical_name == updated_data_source_server_resp['canonicalName']
    assert data_source.creator == updated_data_source_server_resp['creator']
    assert data_source.updated == parse_time(updated_data_source_server_resp['updated'])
    assert data_source.params == updated_params


@responses.activate
def test_update_fetch_size(data_sources_endpoint, airlines10mb_data_source_server_resp):
    data_source_id = airlines10mb_data_source_server_resp['id']
    fetch_size = 12345
    responses.add(
        responses.GET,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=airlines10mb_data_source_server_resp)
    airlines10mb_data_source_server_resp['params']['fetchSize'] = fetch_size
    responses.add(
        responses.GET,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=airlines10mb_data_source_server_resp)
    responses.add(
        responses.PATCH,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=airlines10mb_data_source_server_resp)

    data_source = DataSource.get(data_source_id)
    assert data_source.params.fetch_size is None

    new_perams_kwargs = data_source.params.collect_payload()
    new_perams_kwargs['fetch_size'] = fetch_size
    data_source.update(
        params=DataSourceParameters(**new_perams_kwargs)
    )
    new_data_source = DataSource.get(data_source_id)

    assert new_data_source.params.fetch_size == fetch_size


@responses.activate
def test_update_schema(data_sources_endpoint, airlines10mb_data_source_server_resp):
    data_source_id = airlines10mb_data_source_server_resp['id']
    updated_schema = 'other_schema'
    responses.add(
        responses.GET,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=airlines10mb_data_source_server_resp)
    airlines10mb_data_source_server_resp['params']['schema'] = updated_schema
    responses.add(
        responses.GET,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=airlines10mb_data_source_server_resp)
    responses.add(
        responses.PATCH,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=airlines10mb_data_source_server_resp)

    data_source = DataSource.get(data_source_id)
    new_perams_kwargs = data_source.params.collect_payload()
    new_perams_kwargs['schema'] = updated_schema
    data_source.update(
        params=DataSourceParameters(**new_perams_kwargs)
    )
    new_data_source = DataSource.get(data_source_id)
    assert new_data_source.params.schema == updated_schema


@responses.activate
def test_update_partition_column(data_sources_endpoint, airlines10mb_data_source_server_resp):
    data_source_id = airlines10mb_data_source_server_resp['id']
    partition_column = 'my_partition_column'
    responses.add(
        responses.GET,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=airlines10mb_data_source_server_resp)
    airlines10mb_data_source_server_resp['params']['partition_column'] = partition_column
    responses.add(
        responses.GET,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=airlines10mb_data_source_server_resp)
    responses.add(
        responses.PATCH,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=airlines10mb_data_source_server_resp)

    data_source = DataSource.get(data_source_id)
    new_perams_kwargs = data_source.params.collect_payload()
    new_perams_kwargs['partition_column'] = partition_column
    data_source.update(
        params=DataSourceParameters(**new_perams_kwargs)
    )
    new_data_source = DataSource.get(data_source_id)
    assert new_data_source.params.partition_column == partition_column


@responses.activate
def test_update_to_query(
    data_sources_endpoint,
    diagnostics_data_source_server_resp,
    airlines10mb_1000_records_data_source_server_resp
):
    data_source_id = airlines10mb_1000_records_data_source_server_resp['id']
    responses.add(
        responses.GET,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=airlines10mb_1000_records_data_source_server_resp)
    updated_params = DataSourceParameters(
        query=diagnostics_data_source_server_resp['params']['query'],
    )
    updated_data_source_server_resp = dict(
        airlines10mb_1000_records_data_source_server_resp,
        canonicalName='updated_canonical_name',
        params=updated_params.collect_payload()
    )
    updated_data_source_server_resp['params']['dataStoreId'] = \
        airlines10mb_1000_records_data_source_server_resp['params']['dataStoreId']
    responses.add(
        responses.GET,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=updated_data_source_server_resp)
    responses.add(
        responses.PATCH,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=updated_data_source_server_resp)
    data_source = DataSource.get(data_source_id)

    data_source.update(
        canonical_name=updated_data_source_server_resp['canonicalName'],
        params=updated_params
    )

    assert data_source.id == airlines10mb_1000_records_data_source_server_resp['id']
    assert data_source.type == updated_data_source_server_resp['type']
    assert data_source.canonical_name == updated_data_source_server_resp['canonicalName']
    assert data_source.creator == updated_data_source_server_resp['creator']
    assert data_source.updated == parse_time(updated_data_source_server_resp['updated'])
    assert data_source.params == updated_params


@responses.activate
def test_update_unable_to_change_type(data_sources_endpoint, diagnostics_data_source_server_resp):
    data_source_id = diagnostics_data_source_server_resp['id']
    responses.add(
        responses.GET,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=diagnostics_data_source_server_resp)
    responses.add(
        responses.PATCH,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=diagnostics_data_source_server_resp)

    data_source = DataSource.get(data_source_id)
    data_source._type = 'new_type'
    data_source.update()
    new_data_source = DataSource.get(data_source_id)

    assert new_data_source.type == diagnostics_data_source_server_resp['type']


@responses.activate
def test_update_unable_to_change_creator(
    data_sources_endpoint, diagnostics_data_source_server_resp
):
    data_source_id = diagnostics_data_source_server_resp['id']
    responses.add(
        responses.GET,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=diagnostics_data_source_server_resp)
    responses.add(
        responses.PATCH,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=diagnostics_data_source_server_resp)

    data_source = DataSource.get(data_source_id)
    data_source._created = 'other_user'
    data_source.update()
    new_data_source = DataSource.get(data_source_id)

    assert new_data_source.creator == diagnostics_data_source_server_resp['creator']


@responses.activate
def test_update_unable_to_change_updated(
    data_sources_endpoint, diagnostics_data_source_server_resp
):
    data_source_id = diagnostics_data_source_server_resp['id']
    responses.add(
        responses.GET,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=diagnostics_data_source_server_resp)
    responses.add(
        responses.PATCH,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=diagnostics_data_source_server_resp)

    data_source = DataSource.get(data_source_id)
    data_source._updated = datetime.now()
    data_source.update()
    new_data_source = DataSource.get(data_source_id)

    assert new_data_source.updated == parse_time(diagnostics_data_source_server_resp['updated'])


@responses.activate
def test_delete(data_sources_endpoint, diagnostics_data_source_server_resp):
    data_source_id = diagnostics_data_source_server_resp['id']
    responses.add(
        responses.GET,
        '{}{}/'.format(data_sources_endpoint, data_source_id),
        json=diagnostics_data_source_server_resp
    )
    delete_url = '{}{}/'.format(data_sources_endpoint, data_source_id)
    responses.add(responses.DELETE, delete_url)

    data_source = DataSource.get(data_source_id)
    data_source.delete()

    assert responses.calls[1].request.method == responses.DELETE
    assert responses.calls[1].request.url == delete_url
