import trafaret as t

from datarobot.client import get_client, staticproperty
from datarobot.models.api_object import APIObject

from ..utils import encode_utf8_if_py2, from_api, parse_time


_data_source_params_converter = t.Dict({
    t.Key('data_store_id'): t.String() | t.Null,
    t.Key('table', optional=True): t.String() | t.Null,
    t.Key('schema', optional=True): t.String() | t.Null,
    t.Key('partition_column', optional=True): t.String() | t.Null,
    t.Key('query', optional=True): t.String() | t.Null,
    t.Key('fetch_size', optional=True): t.Int() | t.Null
}).ignore_extra('*')


class DataSourceParameters(object):
    """ Data request configuration

    Attributes
    ----------
    data_store_id : str
        the id of the DataStore.
    table : str
        optional, the name of specified database table.
    schema : str
        optional, the name of the schema associated with the table.
    partition_column : str
        optional, the name of the partition column.
    query : str
        optional, the user specified SQL query.
    fetch_size : int
        optional, a user specified fetch size in the range [1, 20000].
        By default a fetchSize will be assigned to balance throughput and memory usage
    """
    def __init__(self, data_store_id=None, table=None, schema=None, partition_column=None,
                 query=None, fetch_size=None):
        _data_source_params_converter.check({
            'data_store_id': data_store_id,
            'table': table,
            'schema': schema,
            'partition_column': partition_column,
            'query': query,
            'fetch_size': fetch_size
        })
        self.data_store_id = data_store_id
        self.table = table
        self.schema = schema
        self.partition_column = partition_column
        self.query = query
        self.fetch_size = fetch_size

    def collect_payload(self):
        return {
            'data_store_id': self.data_store_id,
            'table': self.table,
            'schema': self.schema,
            'partition_column': self.partition_column,
            'query': self.query,
            'fetch_size': self.fetch_size
        }

    @classmethod
    def from_server_data(cls, data):
        converted_data = _data_source_params_converter.check(from_api(data))
        return cls(**converted_data)

    def __eq__(self, other):
        self_payload = self.collect_payload()
        other_payload = other.collect_payload()
        del self_payload['data_store_id']
        del other_payload['data_store_id']
        return self_payload == other_payload


class DataSource(APIObject):
    """ A data source. Represents data request

    Attributes
    ----------
    data_source_id : str
        the id of the data source.
    data_source_type : str
        the type of data source.
    canonical_name : str
        the user-friendly name of the data source.
    creator : str
        the id of the user who created the data source.
    updated : datetime.datetime
        the time of the last update.
    params : DataSourceParameters
        a list specifying data source parameters.
    """
    _path = 'externalDataSources/'
    _client = staticproperty(get_client)
    _converter = t.Dict({
        t.Key('id', optional=True) >> 'data_source_id': t.String(),
        t.Key('type') >> 'data_source_type': t.String(),
        t.Key('canonical_name'): t.String(),
        t.Key('creator'): t.String(),
        t.Key('params'): _data_source_params_converter
    }).allow_extra('*')

    def __init__(self, data_source_id=None, data_source_type=None, canonical_name=None,
                 creator=None, updated=None, params=None):
        self._id = data_source_id
        self._type = data_source_type
        self.canonical_name = canonical_name
        self._creator = creator
        self._updated = updated
        self.params = params

    @classmethod
    def list(cls):
        """
        Returns list of available data sources.

        Returns
        -------
        data_sources : list of DataSource instances
            contains a list of available data sources.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> data_sources = dr.DataSource.list()
            >>> data_sources
            [DataSource('Diagnostics'), DataSource('Airlines 100mb'), DataSource('Airlines 10mb')]
        """
        r_data = cls._client.get(cls._path).json()
        return [cls.from_server_data(item) for item in r_data['data']]

    @classmethod
    def get(cls, data_source_id):
        """
        Gets the data source.

        Parameters
        ----------
        data_source_id : str
            the identifier of the data source.

        Returns
        -------
        data_source : DataSource
            the requested data source.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> data_source = dr.DataSource.get('5a8ac9ab07a57a0001be501f')
            >>> data_source
            DataSource('Diagnostics')
        """
        return cls.from_location('{}{}/'.format(cls._path, data_source_id))

    @classmethod
    def create(cls, data_source_type, canonical_name, params):
        """
        Creates the data source.

        Parameters
        ----------
        data_source_type : str
            the type of data source.
        canonical_name : str
            the user-friendly name of the data source.
        params : DataSourceParameters
            a list specifying data source parameters.

        Returns
        -------
        data_source : DataSource
            the created data source.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> params = dr.DataSourceParameters(
            ...     data_store_id='5a8ac90b07a57a0001be501e',
            ...     query='SELECT * FROM airlines10mb WHERE "Year" >= 1995;'
            ... )
            >>> data_source = dr.DataSource.create(
            ...     data_source_type='jdbc',
            ...     canonical_name='airlines stats after 1995',
            ...     params=params
            ... )
            >>> data_source
            DataSource('airlines stats after 1995')
        """
        payload = {
            'type': data_source_type,
            'canonicalName': canonical_name,
            'params': params.collect_payload()
        }
        return cls.from_server_data(
            cls._client.post(cls._path, data=payload).json()
        )

    def update(self, canonical_name=None, params=None):
        """
        Creates the data source.

        Parameters
        ----------
        canonical_name : str
            optional, the user-friendly name of the data source.
        params : DataSourceParameters
            optional, the identifier of the DataDriver.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> data_source = dr.DataSource.get('5ad840cc613b480001570953')
            >>> data_source
            DataSource('airlines stats after 1995')
            >>> params = dr.DataSourceParameters(
            ...     query='SELECT * FROM airlines10mb WHERE "Year" >= 1990;'
            ... )
            >>> data_source.update(
            ...     canonical_name='airlines stats after 1990',
            ...     params=params
            ... )
            >>> data_source
            DataSource('airlines stats after 1990')
        """
        payload = {
            'canonicalName': canonical_name or self.canonical_name,
            'params': params.collect_payload() if params else self.params.collect_payload()
        }
        r_data = self._client.patch('{}{}/'.format(self._path, self.id), data=payload).json()
        self.canonical_name = r_data['canonicalName']
        self.params = DataSourceParameters.from_server_data(r_data.pop('params'))

    def delete(self):
        """ Removes the DataSource """
        self._client.delete('{}{}/'.format(self._path, self.id))

    @classmethod
    def from_server_data(cls, data, keep_attrs=None):
        converted_data = cls._converter.check(from_api(data))
        params = converted_data.pop('params')
        data_store_id = params.pop('data_store_id')
        converted_data['params'] = DataSourceParameters(data_store_id, **params)
        converted_data['updated'] = parse_time(converted_data['updated'])
        return cls(**converted_data)

    def __repr__(self):
        return encode_utf8_if_py2(u'{}(\'{}\')'.format(self.__class__.__name__,
                                                       self.canonical_name or self.id))

    @property
    def id(self):
        return self._id

    @property
    def creator(self):
        return self._creator

    @property
    def type(self):
        return self._type

    @property
    def updated(self):
        return self._updated
