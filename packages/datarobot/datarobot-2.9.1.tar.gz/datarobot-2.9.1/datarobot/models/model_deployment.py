import trafaret as t

from ..enums import MODEL_DEPLOYMENT_STATUS
from ..utils import from_api, parse_time
from .api_object import APIObject


class ModelDeployment(APIObject):
    """ ModelDeployments provide an interface for tracking the health and activity of predictions
    made against a deployment model. The `get_service_statistics` method can be used to see current
    and historical trends in requests made and in user and server error rates

    Attributes
    ----------
    id : str
        id of the model deployment
    model : dict
        model associated with the model deployment
    project : dict
        project associated with the model deployment
    type : str
        type of the model deployment. Can be one of [`sse`, `dedicated`, `legacy_dedicated`]
    status : str
        status of the model deployment. Can be one of [`active`, `inactive`, `archived`]
    user : dict
        user who created the model deployment
    organization_id : str
        id of the organization associated with the model deployment
    instance : dict
        instance associated with the model deployment
    label : str
        label of the model deployment
    description : str
        description of the model deployment
    prediction_endpoint : str
        URL where the model is deployed and available for serving predictions
    deployed : bool
        has the model deployment deployed process finished or not.
    created_at : datetime
        timestamp when the model deployment was created
    updated_at : datetime
        timestamp when the model deployment was updated
    service_health : str
        display model health status. Can be one of [`passing`, `warning` or `failing`]
    service_health_messages : list
        list of `HealthMessage` objects for service health state
    recent_request_count : int
        the number of recent requests, within the recent time window
        specified in `trend_time_window`
    prev_request_count : int
        the number of requests, within the previous time window specified in `trend_time_window`
    relative_requests_trend : float
        relative difference (as a percentage) between the number of prediction requests performed
        within the current time window and one time window before that. The size of the time window
        is specified by `trend_time_window`
    trend_time_window : str
        time window (in full days from "now") trend is calculated for
    request_rates : list
        history of request rates per day sorted in chronological order
        (last entry being the most recent, i.e. today).

    Notes
    -----
    ``HealthMessage`` dict contains:

        * `level` : error level, one of [`passing`, `warning`, `failing`]
        * `msg_id` : identifier for message, like `USER_ERRORS`, `SERVER_ERRORS`, `NO_GOOD_REQUESTS`
        * `message` : human-readable message

    ``Instance`` dict contains:

        * `id` : id of the dedicated prediction instance the model is deployed to
        * `host_name` : host name of the dedicated prediction instance
        * `private_ip` : IP address of the dedicated prediction instance
        * `orm_version` : On-demand Resource Manager version of the dedicated prediction instance

    ``Model`` dict contains:

        * `id` : id of the deployed model
        * `model_type` : identifies the model, e.g. `Nystroem Kernel SVM Regressor`
        * `uid` : id of the user who created this model

    ``User`` dict contains:

        * `username` : the user's username
        * `first_name` : the user's first name
        * `last_name` : the user's last name
    """
    _path = 'modelDeployments/'

    _status_converter = t.Enum(
        MODEL_DEPLOYMENT_STATUS.ACTIVE,
        MODEL_DEPLOYMENT_STATUS.INACTIVE,
        MODEL_DEPLOYMENT_STATUS.ARCHIVED
    )
    _converter = t.Dict({
        t.Key('id'): t.String,
        t.Key('model'): t.Dict({
            t.Key('id'): t.String,
            t.Key('model_type'): t.String,
            t.Key('uid'): t.String
        }).ignore_extra('*'),
        t.Key('project'): t.Dict().ignore_extra('*'),
        t.Key('type'): t.String,
        t.Key('status'): _status_converter,
        t.Key('user'): t.Dict({
            t.Key('id'): t.String,
            t.Key('username'): t.String,
            t.Key('first_name', optional=True): t.String,
            t.Key('last_name', optional=True): t.String
        }).ignore_extra('*'),
        t.Key('organization_id', optional=True): t.String,
        t.Key('instance', optional=True): t.Dict({
            t.Key('id'): t.String,
            t.Key('host_name'): t.String,
            t.Key('private_ip'): t.String,
            t.Key('orm_version'): t.String
        }).ignore_extra('*'),
        t.Key('label'): t.String,
        t.Key('description', optional=True): t.String(allow_blank=True),
        t.Key('prediction_endpoint'): t.String,
        t.Key('deployed', optional=True): t.Bool,
        t.Key('created_at'): parse_time,
        t.Key('updated_at'): parse_time,
        t.Key('service_health'): t.String,
        t.Key('service_health_messages'): t.List(t.Dict({
            t.Key('level'): t.String,
            t.Key('msg_id'): t.String,
            t.Key('message'): t.String
        })),
        t.Key('recent_request_count'): t.Int,
        t.Key('prev_request_count'): t.Int,
        t.Key('relative_requests_trend'): t.Float,
        t.Key('trend_time_window'): t.Or(t.String, t.Int),
        t.Key('request_rates'): t.List(t.Any)
    }).ignore_extra('*')
    _service_health_converter = t.Dict({
        t.Key('total_requests'): t.Int,
        t.Key('consumers'): t.Int,
        t.Key('period'): t.Dict({
            t.Key('start'): parse_time,
            t.Key('end'): parse_time
        }),
        t.Key('user_error_rate'): t.Dict({
            t.Key('current'): t.Float,
            t.Key('previous'): t.Float
        }),
        t.Key('server_error_rate'): t.Dict({
            t.Key('current'): t.Float,
            t.Key('previous'): t.Float
        }),
        t.Key('load'): t.Dict({
            t.Key('peak'):  t.Float,
            t.Key('median'): t.Float
        }),
        t.Key('median_execution_time', optional=True): t.Or(t.Float, t.Null)
    }).ignore_extra('*')
    _action_log_action_choices = ['deployed', 'created']
    _action_log_action_converter = t.Enum(*_action_log_action_choices)
    _action_log_converter = t.Dict({
        t.Key('action'): _action_log_action_converter,
        t.Key('performed_by'): t.Dict({
            t.Key('id'): t.String,
            t.Key('username'): t.String,
            t.Key('first_name', optional=True): t.String,
            t.Key('last_name', optional=True): t.String
        }).ignore_extra('*'),
        t.Key('performed_at'): parse_time
    }).ignore_extra('*')

    def __init__(self, id, model=None, project=None, type=None, status=None, user=None,
                 organization_id=None, instance=None, label=None, description=None,
                 prediction_endpoint=None, deployed=None, created_at=None, updated_at=None,
                 service_health=None, service_health_messages=None, recent_request_count=None,
                 prev_request_count=None, relative_requests_trend=None, trend_time_window=None,
                 request_rates=None):
            self.id = id
            self.model = model
            self.project = project
            self.type = type
            self.status = status
            self.user = user
            self.organization_id = organization_id
            self.instance = instance
            self.label = label
            self.description = description
            self.prediction_endpoint = prediction_endpoint
            self.deployed = deployed
            self.created_at = created_at
            self.updated_at = updated_at
            self.service_health = service_health
            self.service_health_messages = service_health_messages
            self.recent_request_count = recent_request_count
            self.prev_request_count = prev_request_count
            self.relative_requests_trend = relative_requests_trend
            self.trend_time_window = trend_time_window
            self.request_rates = request_rates

    @classmethod
    def create(cls, project_id, model_id, label, instance_id=None, description=None, status=None):
        """ Create model deployment.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        model_id : str
            id of the model for deployment
        label : str
            human-readable name for the model deployment
        instance_id : str, optional
            id of the instance in DataRobot cloud being deployed to
        description : str, optional
            description for the model deployment
        status : str, optional
            status for the model deployment. Can be [`active`, `inactive`, `archived`].

        Returns
        -------
        job : Job
            an instance of created async job
        """
        payload = {
            'projectId': project_id,
            'modelId': model_id,
            'label': label
        }
        if instance_id:
            payload['instanceId'] = instance_id
        if description:
            payload['description'] = description
        if status:
            payload['status'] = status
        response = cls._client.post(cls._path, data=payload)
        return cls.from_location(response.headers['Location'])

    @classmethod
    def list(cls, limit=None, offset=None, query=None, order_by=None, status=None):
        """ List of model_deployments

        Parameters
        ----------
        limit : int or None
            at most this many results are returned, default: no limit
        offset : int or None
            this many results will be skipped, default: 0
        query : str, optional
            Filter the model deployments by matching labels and descriptions
            with the specified string. Partial matches are included, too.
            Matches are case insensitive
        order_by : str, optional
            the model deployments. Supported attributes for ordering: label, exportTarget,
            status, type. Prefix attribute name with dash to sort in descending order, e.g.
            orderBy=-label. Only one field can be selected
        status : str, optional
            Filter the list of deployments by status.
            Must be one of: [`active`, `inactive`, `archived`]

        Returns
        -------
        model_deployments : list[ModelDeployment]
        """
        if status:
            status = cls._status_converter.check(status)
        response = cls._client.get(cls._path,
                                   params={'limit': limit,
                                           'offset': offset,
                                           'query': query,
                                           'orderBy': order_by,
                                           'status': status})
        r_data = response.json()
        return [cls.from_server_data(item) for item in r_data['data']]

    @classmethod
    def get(cls, model_deployment_id):
        """ Retrieve sa single model_deployment

        Parameters
        ----------
        model_deployment_id:
            the id of the model_deployment to query

        Returns
        -------
        model_deployment : ModelDeployment
            The queried instance
        """
        path = '{}{}/'.format(cls._path, model_deployment_id)
        return cls.from_location(path)

    def update(self, label=None, description=None, status=None):
        """ Update model_deployment object

        Parameters
        ----------
        label : str, optional
            The new value for label to be set
        description : str, optional
            The new value for description to be set
        status : str, optional
            The new value for status to be set, Can be one of [`active`, `inactive`, `archived`]
        """
        payload = {}
        if label:
            payload['label'] = label
        if description is not None:
            payload['description'] = description
        if status:
            status = self._status_converter.check(status)
            payload['status'] = status
        path = '{}{}/'.format(self._path, self.id)
        self._client.patch(path, data=payload)
        if label:
            self.label = label
        if description is not None:
            self.description = description
        if status:
            self.status = status

    def get_service_statistics(self, start_date=None, end_date=None):
        """ Retrieve health overview of current model_deployment

        Parameters
        ----------
        start_date : str, optional
            datetime string that filter statistic from this timestamp
        end_date: str, optional
            datetime string that filter statistic till this timestamp

        Returns
        -------
        service_health : dict
            dict that represent `ServiceHealth` object

        Notes
        -----
        `ServiceHealth` dict contains:

            * `total_requests`: total number of requests performed. 0, if there were no requests
            * `consumers` : total number of unique users performing requests. 0,
              if there were no requests
            * `period` : dict with two fields - `start` and `end`, that denote the boundaries
              of the time period the stats are reported for. Note,
              that a half-open time interval is used: [start: end)
            * `user_error_rate` : dict with two fields - `current` and `previous`,
              that denote the ratio of user errors to the total number of requests performed
              for the given period and one time period before that.
              0.0, if there were no errors (or requests)
            * `server_error_rate` : dict with two fields - `current` and `previous`,
              that denote the ratio of server errors to the total number of requests
              performed for the given period and one time period before that.
              0.0, if there were no errors (or requests)
            * `load` : dict with two fields - `peak` and `median`, that denote the max and the
              median
              of the request rate (in requests *per minute*) across all requests for the duration
              of the given time period. Both will be equal to 0.0, if there were no requests.
            * `median_execution_time` : the median of the execution time across all
              performed requests (in seconds). `null`, if there were no requests
        """

        path = '{}{}/serviceStats/'.format(self._path, self.id)
        query_params = {'start': start_date, 'end': end_date}
        response_data = from_api(self._client.get(path, params=query_params).json())
        safe_data = self._service_health_converter.check(response_data)
        return safe_data

    def action_log(self, limit=None, offset=None):
        """ List of actions taken affecting this deployment

        Allows insight into when the `ModelDeployment` was created or deployed.

        Parameters
        ----------
        limit : int or None
            at most this many results are returned, default: no limit
        offset : int or None
            this many results will be skipped, default: 0

        Returns
        -------
        action_log : list of dict [`ActionLog`]

        Notes
        -----
        ``ActionLog`` dict contains:

            * `action` : identifies the action. Can be one of [`deployed`, `created`]
            * `performed_by` : dict with id, username, first_name and last_name of the user who
              performed the action.
            * `performed_at` : date/time when the action was performed in ISO-8601 format.
        """

        path = '{}{}/actionLog/'.format(self._path, self.id)
        query_params = {'limit': limit, 'offset': offset}
        response = self._client.get(path, params=query_params)
        r_data = response.json()
        return [self._action_log_converter.check(item) for item in from_api(r_data['data'])]
