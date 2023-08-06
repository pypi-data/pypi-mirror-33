import pytest
import requests
import responses

from powerbi_publisher.powerbi import AzureToken, get_access_token, \
    PowerBiClient
from requests import Request
from unittest.mock import patch


@responses.activate
def test_upload_pbix(powerbiclient, pbix_file, get_datasets_response):
    """
    Test that a Power BI file (PBIX) is uploaded to Power BI web,
    replacing an existing one.
    """
    responses.add(
        responses.GET,
        'https://api.powerbi.com/v1.0/myorg/groups/some-workspace/datasets',
        json=get_datasets_response, status=200)

    responses.add(
        responses.DELETE,
        'https://api.powerbi.com/v1.0/myorg/groups/some-workspace/datasets/'
        'cf0eff42-c79d-44cf-9557-e30e18c63a68',
        status=200)

    responses.add(
        responses.POST,
        'https://api.powerbi.com/v1.0/myorg/groups/some-workspace/imports?'
        'datasetDisplayName=Some dataset name',
        status=200)

    powerbiclient.upload_pbix(
        'Some dataset name', pbix_file, 'some-workspace')

    assert len(responses.calls) == 3


@responses.activate
def test_get_datasets(powerbiclient, get_datasets_response):
    """
    Test that a list of datasets can be obtained from the Power BI web API.
    """
    responses.add(
        responses.GET,
        'https://api.powerbi.com/v1.0/myorg/datasets',
        json=get_datasets_response, status=200)

    datasets = powerbiclient.get_datasets()
    assert datasets[0]['id'] == 'cf0eff42-c79d-44cf-9557-e30e18c63a68'


@responses.activate
def test_search_dataset_by_name(powerbiclient, get_datasets_response):
    """
    Test that we can evaluate if a dataset exists, by its name.
    """
    responses.add(
        responses.GET,
        'https://api.powerbi.com/v1.0/myorg/datasets',
        json=get_datasets_response, status=200)

    dataset_name = 'Some dataset name'
    has_dataset = powerbiclient.search_dataset_by_name(dataset_name)
    assert has_dataset == 'cf0eff42-c79d-44cf-9557-e30e18c63a68'


@responses.activate
def test_has_not_dataset_by_name(
        powerbiclient, get_datasets_response):
    """
    Test that we can evaluate if a dataset does not exist, by its name.
    """
    responses.add(
        responses.GET,
        'https://api.powerbi.com/v1.0/myorg/datasets',
        json=get_datasets_response, status=200)

    dataset_name = 'NON EXISTING dataset name'
    has_dataset = powerbiclient.search_dataset_by_name(dataset_name)
    assert not has_dataset


@responses.activate
def test_delete_dataset(powerbiclient):
    """
    Test that a dataset can be deleted through the Power BI web API.
    """
    responses.add(
        responses.DELETE,
        'https://api.powerbi.com/v1.0/myorg/datasets/'
        'cf0eff42-c79d-44cf-9557-e30e18c63a68',
        status=200)

    powerbiclient.delete_dataset('cf0eff42-c79d-44cf-9557-e30e18c63a68')


@responses.activate
def test_get_access_token_connection_error(config):
    """
    Test that an exception is raised if there is a connection error with the
    Azure web API.
    """
    responses.add(responses.POST,
                  'https://login.microsoftonline.com/common/oauth2/token',
                  json={}, status=400)

    with pytest.raises(requests.exceptions.ConnectionError):
        PowerBiClient(config).auth()


@responses.activate
def test_get_access_token(config, azure_token_response_payload):
    """
    Test that an access token can be obtained from the Azure web API.
    """
    responses.add(responses.POST,
                  'https://login.microsoftonline.com/common/oauth2/token',
                  json=azure_token_response_payload, status=200)

    access_token = get_access_token(
        config['client_id'], config['client_secret'],
        config['username'], config['password'])

    assert isinstance(access_token, AzureToken)


@patch('powerbi_publisher.powerbi.get_access_token')
def test_request_auth_header(
        mock_get_token, config, azure_token):
    """
    Test that an 'Authorization' header for a Bearer token
    is added to an HTTP request.
    """
    mock_get_token.return_value = azure_token
    request = Request('POST',  'foo', data=None, headers=None)
    expected_authorization_token = "some_token"

    PowerBiClient(config).auth(request)
    assert request.headers.get('Authorization') == 'Bearer {!s}'\
        .format(expected_authorization_token)


@responses.activate
def test_auth_fails_with_invalid_token_type(
        config, azure_invalid_token_response_payload):
    """
    Test that the auth method raises a ValueError exception
    if Azure provides an invalid/unsupported token type (i.e. not 'Bearer').
    """
    responses.add(responses.POST,
                  'https://login.microsoftonline.com/common/oauth2/token',
                  json=azure_invalid_token_response_payload, status=200)

    with pytest.raises(ValueError):
        PowerBiClient(config).auth()


def test_token_is_valid(azure_token):
    """
    Test a token is valid if its expiration is one hour from now.
    """
    assert azure_token.is_valid


def test_invalid_token():
    """
    Test that an AzureToken object cannot be instantiated if the type
    is not supported.
    """
    with pytest.raises(ValueError):
        AzureToken('NOT Bearer', '', '')


@responses.activate
def test_access_token_is_reused(config, azure_token_response_payload):
    """
    Test that an access token is reused for many Power BI API calls if it is
    still valid.
    """
    responses.add(responses.POST,
                  'https://login.microsoftonline.com/common/oauth2/token',
                  json=azure_token_response_payload, status=200)

    powerbi_client = PowerBiClient(config)

    first_token = powerbi_client.token
    second_token = powerbi_client.token

    assert second_token == first_token


def test_build_endpoint_workspace_part(powerbiclient):
    """Test that the workspace part in a Power BI endpoint is built properly"""
    no_workspace_part = powerbiclient.workspace_url_part
    assert no_workspace_part == '/'

    powerbiclient.workspace_id = 'some-guid'
    workspace_part = powerbiclient.workspace_url_part
    assert workspace_part == '/groups/some-guid/'
