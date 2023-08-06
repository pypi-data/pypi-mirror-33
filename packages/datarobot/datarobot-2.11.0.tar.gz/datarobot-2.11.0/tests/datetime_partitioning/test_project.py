import json

import pytest
import responses


@responses.activate
@pytest.mark.usefixtures('client')
def test_set_target(datetime_partition_spec, holdout_start_date,
                    project_with_target_json, project_without_target,
                    unittest_endpoint, project_id):
    project_url = '{}/projects/{}/'.format(unittest_endpoint, project_id)
    aim_url = project_url + 'aim/'
    status_url = '{}/status/some-status/'.format(unittest_endpoint)

    responses.add(responses.PATCH,
                  aim_url,
                  body='',
                  status=202,
                  adding_headers={'Location': status_url},
                  content_type='application/json')

    responses.add(responses.GET,
                  status_url,
                  body='',
                  status=303,
                  adding_headers={'Location': project_url},
                  content_type='application/json')
    responses.add(responses.GET,
                  project_url,
                  body=project_with_target_json,
                  status=200,
                  content_type='application/json')

    expected_backtests = [{
        'index': bt.index, 'gapDuration': bt.gap_duration,
        'validationStartDate': bt.validation_start_date.isoformat(),
        'validationDuration': bt.validation_duration
        } for bt in datetime_partition_spec.backtests]
    expected_payload = {
        'datetimePartitionColumn': datetime_partition_spec.datetime_partition_column,
        'useTimeSeries': datetime_partition_spec.use_time_series,
        'defaultToKnownInAdvance': datetime_partition_spec.default_to_known_in_advance,
        'autopilotDataSelectionMethod': datetime_partition_spec.autopilot_data_selection_method,
        'validationDuration': datetime_partition_spec.validation_duration,
        'holdoutStartDate': holdout_start_date.isoformat(),
        'holdoutDuration': datetime_partition_spec.holdout_duration,
        'gapDuration': datetime_partition_spec.gap_duration,
        'numberOfBacktests': datetime_partition_spec.number_of_backtests,
        'backtests': expected_backtests,
        'cvMethod': 'datetime',
        'target': 'target',
        'mode': 'auto'
    }
    project_without_target.set_target('target', partitioning_method=datetime_partition_spec)

    assert responses.calls[0].request.method == 'PATCH'
    actual_request = json.loads(responses.calls[0].request.body)
    assert set(actual_request.keys()) == set(expected_payload.keys())
    assert actual_request == expected_payload


@responses.activate
@pytest.mark.usefixtures('client')
def test_time_series_set_target(time_series_partition_spec, holdout_start_date,
                                project_with_target_json, project_without_target,
                                unittest_endpoint, project_id):
    project_url = '{}/projects/{}/'.format(unittest_endpoint, project_id)
    aim_url = project_url + 'aim/'
    status_url = '{}/status/some-status/'.format(unittest_endpoint)

    responses.add(responses.PATCH,
                  aim_url,
                  body='',
                  status=202,
                  adding_headers={'Location': status_url},
                  content_type='application/json')

    responses.add(responses.GET,
                  status_url,
                  body='',
                  status=303,
                  adding_headers={'Location': project_url},
                  content_type='application/json')
    responses.add(responses.GET,
                  project_url,
                  body=project_with_target_json,
                  status=200,
                  content_type='application/json')

    expected_backtests = [{
        'index': bt.index, 'gapDuration': bt.gap_duration,
        'validationStartDate': bt.validation_start_date.isoformat(),
        'validationDuration': bt.validation_duration
        } for bt in time_series_partition_spec.backtests]
    expected_payload = {
        'datetimePartitionColumn': time_series_partition_spec.datetime_partition_column,
        'useTimeSeries': time_series_partition_spec.use_time_series,
        'defaultToKnownInAdvance': time_series_partition_spec.default_to_known_in_advance,
        'featureDerivationWindowStart': time_series_partition_spec.feature_derivation_window_start,
        'featureDerivationWindowEnd': time_series_partition_spec.feature_derivation_window_end,
        'forecastWindowStart': time_series_partition_spec.forecast_window_start,
        'forecastWindowEnd': time_series_partition_spec.forecast_window_end,
        'autopilotDataSelectionMethod': time_series_partition_spec.autopilot_data_selection_method,
        'validationDuration': time_series_partition_spec.validation_duration,
        'holdoutStartDate': holdout_start_date.isoformat(),
        'holdoutDuration': time_series_partition_spec.holdout_duration,
        'gapDuration': time_series_partition_spec.gap_duration,
        'numberOfBacktests': time_series_partition_spec.number_of_backtests,
        'backtests': expected_backtests,
        'cvMethod': 'datetime',
        'target': 'target',
        'mode': 'auto'
    }
    project_without_target.set_target('target', partitioning_method=time_series_partition_spec)

    assert responses.calls[0].request.method == 'PATCH'
    actual_request = json.loads(responses.calls[0].request.body)
    assert set(actual_request.keys()) == set(expected_payload.keys())
    assert actual_request == expected_payload


@responses.activate
@pytest.mark.usefixtures('client')
def test_multiseries_set_target(time_series_partition_spec, holdout_start_date,
                                project_with_target_json, project_without_target,
                                unittest_endpoint, project_id):
    time_series_partition_spec.multiseries_id_columns = ['series_id']
    project_url = '{}/projects/{}/'.format(unittest_endpoint, project_id)
    aim_url = project_url + 'aim/'
    status_url = '{}/status/some-status/'.format(unittest_endpoint)
    multi_prop_url = '{}features/{}/multiseriesProperties/'.format(
        project_url, time_series_partition_spec.datetime_partition_column)
    multi_prop_json = {
        'datetimePartitionColumn': time_series_partition_spec.datetime_partition_column,
        'detectedMultiseriesIdColumns': [
            {'multiseriesIdColumns': ['series_id'], 'timeStep': 1, 'timeUnit': 'DAY'}
        ]
    }
    responses.add(responses.GET, multi_prop_url,
                  json=multi_prop_json)
    date_feat_json = {
        'projectId': project_id, 'name': time_series_partition_spec.datetime_partition_column,
        'id': 2, 'timeSeriesEligible': False, 'featureType': 'date',
        'timeSeriesEligibilityReason': 'notUnique', 'lowInformation': False, 'uniqueCount': 500
    }
    responses.add(responses.GET,
                  '{}features/{}/'.format(project_url,
                                          time_series_partition_spec.datetime_partition_column),
                  json=date_feat_json)

    responses.add(responses.PATCH,
                  aim_url,
                  body='',
                  status=202,
                  adding_headers={'Location': status_url},
                  content_type='application/json')

    responses.add(responses.GET,
                  status_url,
                  body='',
                  status=303,
                  adding_headers={'Location': project_url},
                  content_type='application/json')
    responses.add(responses.GET,
                  project_url,
                  body=project_with_target_json,
                  status=200,
                  content_type='application/json')

    expected_backtests = [{
        'index': bt.index, 'gapDuration': bt.gap_duration,
        'validationStartDate': bt.validation_start_date.isoformat(),
        'validationDuration': bt.validation_duration
        } for bt in time_series_partition_spec.backtests]
    expected_payload = {
        'datetimePartitionColumn': time_series_partition_spec.datetime_partition_column,
        'multiseriesIdColumns': time_series_partition_spec.multiseries_id_columns,
        'useTimeSeries': time_series_partition_spec.use_time_series,
        'defaultToKnownInAdvance': time_series_partition_spec.default_to_known_in_advance,
        'featureDerivationWindowStart': time_series_partition_spec.feature_derivation_window_start,
        'featureDerivationWindowEnd': time_series_partition_spec.feature_derivation_window_end,
        'forecastWindowStart': time_series_partition_spec.forecast_window_start,
        'forecastWindowEnd': time_series_partition_spec.forecast_window_end,
        'autopilotDataSelectionMethod': time_series_partition_spec.autopilot_data_selection_method,
        'validationDuration': time_series_partition_spec.validation_duration,
        'holdoutStartDate': holdout_start_date.isoformat(),
        'holdoutDuration': time_series_partition_spec.holdout_duration,
        'gapDuration': time_series_partition_spec.gap_duration,
        'numberOfBacktests': time_series_partition_spec.number_of_backtests,
        'backtests': expected_backtests,
        'cvMethod': 'datetime',
        'target': 'target',
        'mode': 'auto'
    }
    project_without_target.set_target('target', partitioning_method=time_series_partition_spec)

    assert responses.calls[2].request.method == 'PATCH'
    actual_request = json.loads(responses.calls[2].request.body)
    assert set(actual_request.keys()) == set(expected_payload.keys())
    assert actual_request == expected_payload
