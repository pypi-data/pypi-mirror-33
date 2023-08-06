import pytest
import requests
import responses

from powerbi_publisher.powerbi import AzureToken, get_access_token, \
    PowerBiClient
from requests import Request
from unittest.mock import patch


@responses.activate
def test_import_report(
        powerbiclient, pbix_file, post_import_response, get_import_response):
    """
    Test that a Power BI file (PBIX) is uploaded to Power BI web,
    and that a refresh is triggered for the created dataset.
    """
    responses.add(
        responses.POST,
        'https://api.powerbi.com/v1.0/myorg/groups/some-workspace/imports?'
        'datasetDisplayName=Some dataset name',
        json=post_import_response, status=200)

    responses.add(
        responses.GET,
        'https://api.powerbi.com/v1.0/myorg/groups/some-workspace/imports/'
        '37cd7597-bad6-472b-b788-18ae04fd573d',
        json=get_import_response, status=200)

    responses.add(
        responses.POST,
        'https://api.powerbi.com/v1.0/myorg/groups/some-workspace/datasets/'
        'd6c6e003-6ef7-418c-902f-fab1e114704c/refreshes',
        status=202)

    powerbiclient.import_report(
        'Some dataset name', pbix_file, 'some-workspace')

    assert len(responses.calls) == 3


@patch('time.sleep')
@responses.activate
def test_wait_for_import_succeeded(
        patched_time_sleep, powerbiclient, get_import_response_publishing, get_import_response):
    """
    Test that an import can be obtained.
    """
    patched_time_sleep.return_value = None

    responses.add(
        responses.GET,
        'https://api.powerbi.com/v1.0/myorg/imports/'
        '37cd7597-bad6-472b-b788-18ae04fd573d',
        json=get_import_response_publishing, status=200)

    responses.add(
        responses.GET,
        'https://api.powerbi.com/v1.0/myorg/imports/'
        '37cd7597-bad6-472b-b788-18ae04fd573d',
        json=get_import_response, status=200)

    powerbiclient._wait_for_import_succeeded(
        '37cd7597-bad6-472b-b788-18ae04fd573d')

    assert len(responses.calls) == 2


@responses.activate
def test_get_import(powerbiclient, get_import_response):
    """
    Test that an import can be obtained.
    """
    responses.add(
        responses.GET,
        'https://api.powerbi.com/v1.0/myorg/imports/'
        '37cd7597-bad6-472b-b788-18ae04fd573d',
        json=get_import_response, status=200)

    powerbiclient.get_import('37cd7597-bad6-472b-b788-18ae04fd573d')


@responses.activate
def test_refresh_dataset(powerbiclient):
    """
    Test a (data) refresh can be triggered for a dataset.
    """
    responses.add(
        responses.POST,
        'https://api.powerbi.com/v1.0/myorg/datasets/'
        'd6c6e003-6ef7-418c-902f-fab1e114704c/refreshes',
        status=202)

    powerbiclient.refresh_dataset('d6c6e003-6ef7-418c-902f-fab1e114704c')


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
