import pytest
import time

from powerbi_publisher.powerbi import AzureToken, PowerBiClient
from unittest.mock import patch, PropertyMock


@pytest.fixture
def config():
    """Return a config fixture"""
    return {
        'resource': 'https://analysis.windows.net/powerbi/api',
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
def pbix_file():
    """Return a (fake) Power BI report (PBIX) file"""
    return b'\x68\x65\x6c\x6c\x6f\x77\x6f\x72\x6c\x64'  # helloworld


@pytest.fixture
def post_import_response():
    """Return a fixture of a Post Import response from the Power BI web API"""
    return {
        "id": "37cd7597-bad6-472b-b788-18ae04fd573d"
    }


@pytest.fixture
def get_import_response_publishing():
    """
    Return a fixture of a Get Import response from the Power BI web API
    where the import is still being published (i.e. not ready/succeeded).
    """
    return {
        "@odata.context": "http://api.powerbi.com/v1.0/myorg/$metadata#imports/$entity",
        "id": "37cd7597-bad6-472b-b788-18ae04fd573d",
        "importState": "Publishing",
        "createdDateTime": "2018-07-06T17:51:17.223Z",
        "updatedDateTime": "2018-07-06T18:33:41.483Z",
        "name": "IT Dashboard",
        "connectionType": "import",
        "source": "Upload",
        "datasets": [],
        "reports": []
    }


@pytest.fixture
def get_import_response():
    """Return a fixture of a Get Import response from the Power BI web API"""
    return {
        "@odata.context": "http://api.powerbi.com/v1.0/myorg/$metadata#imports/$entity",
        "id": "37cd7597-bad6-472b-b788-18ae04fd573d",
        "importState": "Succeeded",
        "createdDateTime": "2018-07-06T17:51:17.223Z",
        "updatedDateTime": "2018-07-06T18:33:41.483Z",
        "name": "IT Dashboard",
        "connectionType": "import",
        "source": "Upload",
        "datasets": [
            {
                "id": "d6c6e003-6ef7-418c-902f-fab1e114704c",
                "name": "IT Dashboard",
                "webUrl": "https://app.powerbi.com/datasets/d6c6e003-6ef7-418c-902f-fab1e114704c",
                "addRowsAPIEnabled": False,
                "isRefreshable": False,
                "isEffectiveIdentityRequired": False,
                "isEffectiveIdentityRolesRequired": False
            }
        ],
        "reports": [
            {
                "id": "2fdc6fc9-5bb3-43b8-9ff9-8e2afd4f3c64",
                "modelId": 0,
                "name": "IT Dashboard",
                "webUrl": "https://app.powerbi.com/reports/2fdc6fc9-5bb3-43b8-9ff9-8e2afd4f3c64",
                "embedUrl": "https://app.powerbi.com/reportEmbed?reportId=2fdc6fc9-5bb3-43b8-9ff9-8e2afd4f3c64",
                "isOwnedByMe": False,
                "isOriginalPbixReport": False
            }
        ]
    }
