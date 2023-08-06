import pytest
import time

from powerbi_publisher.powerbi import AzureToken, PowerBiClient
from unittest.mock import patch, PropertyMock


@pytest.fixture
def config():
    """Return a config fixture"""
    return {
        'resource': 'https://analysis.windows.net/powerbi/api',
        'tenant': 'some_tenant_guid',
        'authority_host_url': 'https://login.microsoftonline.com',
        'client_id': 'some_client_id',
        'client_secret': 'some_client_secret',
        'username': 'some_username',
        'password': 'some_password'
    }


@pytest.fixture
def azure_token_response_payload():
    """Return an Azure access token response payload"""
    now = time.time()
    now_plus_one_hour = now + 3600

    return {
      'token_type': 'Bearer',
      'expires_in': '3599',
      'expires_on': now_plus_one_hour,
      'access_token': 'some_long_token'
    }


@pytest.fixture
def azure_invalid_token_response_payload(azure_token_response_payload):
    """Return an invalid Azure access token response payload"""
    valid_token = azure_token_response_payload
    invalid_token = valid_token.update({'token_type': 'NOT Bearer'})
    return invalid_token


@pytest.fixture
def powerbiclient_token(azure_token):
    """Return a Power BI access token"""
    with patch('powerbi_publisher.powerbi.PowerBiClient.token',
               new_callable=PropertyMock) as mock:
        mock.return_value = azure_token
        yield mock


@pytest.fixture
def powerbiclient(config, powerbiclient_token):
    """Return a PowerBiClient fixture"""
    powerbi_client = PowerBiClient(config)
    return powerbi_client


@pytest.fixture
def azure_token():
    """Return an AzureToken fixture"""
    now = time.time()
    now_plus_one_hour = now + 3600
    return AzureToken('Bearer', 'some_token', now_plus_one_hour)


@pytest.fixture
def get_datasets_response():
    """Return a fixture of a Get Datasets response from the Power BI web API"""
    return {
        "@odata.context":
            "http://api.powerbi.com/v1.0/myorg/$metadata#datasets",
        "value": [
            {
                "id": "cf0eff42-c79d-44cf-9557-e30e18c63a68",
                "name": "Some dataset name",
                "addRowsAPIEnabled": False,
                "configuredBy": "email@example.com",
                "isRefreshable": True,
                "isEffectiveIdentityRequired": False,
                "isEffectiveIdentityRolesRequired": False,
                "isOnPremGatewayRequired": False
            }
        ]
    }


@pytest.fixture
def pbix_file():
    """Return a (fake) Power BI report (PBIX) file"""
    return b'\x68\x65\x6c\x6c\x6f\x77\x6f\x72\x6c\x64'  # helloworld
