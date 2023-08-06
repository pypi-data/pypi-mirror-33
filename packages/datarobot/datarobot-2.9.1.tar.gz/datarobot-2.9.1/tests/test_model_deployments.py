# -*- encoding: utf-8 -*-
import json

import pytest
import responses
from trafaret import DataError

from datarobot.enums import MODEL_DEPLOYMENT_STATUS
from datarobot.models import ModelDeployment


@pytest.fixture
def model_deployment_url(model_deployment_id):
    return 'https://host_name.com/modelDeployments/{}/'.format(
        model_deployment_id
    )


def test_from_data(model_deployment_data, model_deployment_id):
    model_deployment = ModelDeployment.from_data(model_deployment_data)
    assert model_deployment.id == model_deployment_id


def test_future_proof(model_deployment_data, model_deployment_id):
    model_deployment = ModelDeployment.from_data(dict(model_deployment_data, new_key='future'))
    assert model_deployment.id == model_deployment_id


@responses.activate
@pytest.mark.usefixtures('client')
def test_model_deployment_item_get(model_deployment_json, model_deployment_id,
                                   model_deployment_url):
    """
    Test ModelDeployment.get(model_deployment_id)
    """
    responses.add(responses.GET,
                  model_deployment_url,
                  body=model_deployment_json,
                  status=200,
                  content_type='application/json')
    model_deployment = ModelDeployment.get(model_deployment_id)

    assert isinstance(model_deployment, ModelDeployment)

    assert model_deployment.id == model_deployment_id
    assert model_deployment.description == 'test'
    assert model_deployment.recent_request_count == 10
    assert isinstance(model_deployment.user, dict)


@pytest.fixture
def model_deployment_service_statistic_url(model_deployment_id):
    return 'https://host_name.com/modelDeployments/{}/serviceStats/'.format(model_deployment_id)


@pytest.fixture
def model_deployment_action_log_url(model_deployment_id):
    return 'https://host_name.com/modelDeployments/{}/actionLog/'.format(model_deployment_id)


@responses.activate
@pytest.mark.usefixtures('client')
def test_model_deployment_get_service_statistics(one_model_deployment,
                                                 model_deployment_service_statistic_url):
    """
    Test get_service_statistics of ModelDeployment
    ModelDeployment(model_deployment_id).get_service_statistics()
    """
    body = json.dumps({
        'load': {
            'median': 4.0,
            'peak': 20.0},
        'userErrorRate': {
            'current': 1.0,
            'previous': 2.0
        },
        'consumers': 5,
        'totalRequests': 100,
        'serverErrorRate': {
            'current': 0.0,
            'previous': 1.0
        },
        'period': {
            'start': '2018-02-11 13:25:00.444356+00:00',
            'end': '2018-02-12 13:25:00.444356+00:00'
        },
        'medianExecutionTime': None
    })

    responses.add(
        responses.GET,
        model_deployment_service_statistic_url,
        body=body,
        status=200)

    result = one_model_deployment.get_service_statistics()
    assert responses.calls[0].request.method == 'GET'
    assert result['consumers'] == 5
    assert result['server_error_rate']['previous'] == 1.0


@responses.activate
@pytest.mark.usefixtures('client')
def test_model_deployment_action_log(one_model_deployment, model_deployment_action_log_url):
    """
    Test action_log of ModelDeployment
    ModelDeployment(model_deployment_id).action_log()
    """
    body = json.dumps({
        'data': [
            {
                'action': u'created',
                'performed_at': u'2018-02-14 20:56:44.843939',
                'performed_by': {
                    'id': u'5a84997a3e944d863bfa31be',
                    'username': u'admin@datarobot.com'
                }
            },
            {
                'action': u'deployed',
                'performed_at': u'2018-02-14 20:57:15.130000',
                'performed_by': {
                    'id': u'5a84997a3e944d863bfa31be',
                    'username': u'admin@datarobot.com'
                }
            }
        ]
    })

    responses.add(
        responses.GET,
        model_deployment_action_log_url,
        body=body,
        status=200)

    result = one_model_deployment.action_log()
    assert responses.calls[0].request.method == 'GET'
    assert len(result) == 2


@responses.activate
@pytest.mark.usefixtures('client')
def test_model_deployment_item_update(one_model_deployment,
                                      model_deployment_url):
    """
    Test ModelDeployment.update method
    """
    responses.add(responses.PATCH,
                  model_deployment_url,
                  body='',
                  status=204,
                  content_type='application/json')
    one_model_deployment.update(label='new_label', description='new_description',
                                status=MODEL_DEPLOYMENT_STATUS.INACTIVE)
    assert one_model_deployment.description == 'new_description'
    assert one_model_deployment.label == 'new_label'
    assert one_model_deployment.status == MODEL_DEPLOYMENT_STATUS.INACTIVE


def test_model_deployment_item_update_invalid_status_error(one_model_deployment):
    """
    Test ModelDeployment.update status validation
    """
    with pytest.raises(DataError):
        one_model_deployment.update(status='error_status')


@responses.activate
@pytest.mark.usefixtures('client')
def test_model_deployment_create(model_deployment_json, model_deployment_url):
    """
    Test ModelDeployment.crate method
    """
    responses.add(responses.POST,
                  'https://host_name.com/modelDeployments/',
                  body=model_deployment_json,
                  status=201,
                  content_type='application/json',
                  adding_headers={'Location': model_deployment_url})
    responses.add(responses.GET,
                  model_deployment_url,
                  body=model_deployment_json,
                  status=200,
                  content_type='application/json')
    model_deployment = ModelDeployment.create('pid', 'lid', 'label')

    assert isinstance(model_deployment, ModelDeployment)

    assert model_deployment.description == 'test'
    assert model_deployment.recent_request_count == 10
    assert isinstance(model_deployment.user, dict)


@responses.activate
@pytest.mark.usefixtures('client')
def test_model_deployment_list(model_deployment_json):
    """
    Test ModelDeployment.list method
    """
    list_json_data = '{{"data": [{}]}}'.format(model_deployment_json)
    responses.add(responses.GET,
                  'https://host_name.com/modelDeployments/',
                  body=list_json_data,
                  status=200,
                  content_type='application/json')
    model_deployments = ModelDeployment.list()
    assert isinstance(model_deployments, list)
    model_deployment = model_deployments[0]
    assert isinstance(model_deployment, ModelDeployment)
    assert model_deployment.description == 'test'
    assert model_deployment.recent_request_count == 10
    assert isinstance(model_deployment.user, dict)


def test_model_deployment_list_invalid_status_value():
    """
    Test invalid status param for filtering in ModelDeployment list
    """
    with pytest.raises(DataError):
        ModelDeployment.list(status='invalid_status')
