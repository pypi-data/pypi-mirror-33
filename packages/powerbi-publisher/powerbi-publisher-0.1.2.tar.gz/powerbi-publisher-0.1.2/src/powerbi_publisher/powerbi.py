import requests
import time

from requests.auth import AuthBase


class PowerBiClient(object):

    def __init__(self, config):
        self.config = config
        self._token = None
        self.workspace_id = None

    @property
    def workspace_url_part(self):
        """
        Build the part of an endpoint URI concerning a workspace or group.
        As noted in
        https://docs.microsoft.com/en-us/power-bi/developer/overview-of-power-bi-rest-api
        (2018-06-21), "The Power BI APIs still refer to app workspaces as
        groups. Any references to groups mean that you are working with app
        workspaces."

        Returns
            str: A URI part concerning workspace (or group).
        """
        if self.workspace_id:
            return '/groups/{}/'.format(self.workspace_id)
        else:
            return '/'

    @property
    def auth(self):
        return BearerTokenAuth(self.token.access_token)

    @property
    def token(self):
        """
        Returns an existing valid token or gets a new one if it is not
        (i.e. expired).

        Returns:
            AzureToken: Object containing an authentication token information
        """
        if self._token is None or self._token.is_valid is False:
            self._token = get_access_token(
                self.config['client_id'],
                self.config['client_secret'],
                self.config['username'],
                self.config['password']
            )
            return self._token
        else:
            return self._token

    def upload_pbix(self, report_name, data, workspace_id=None):
        """
        Upload a Power BI file (PBIX) to Power BI web. If a report of the same
        name already exists, it will be deleted to be replaced.
        """
        self.workspace_id = workspace_id
        dataset_id = self.search_dataset_by_name(
            report_name)

        if dataset_id:
            self.delete_dataset(dataset_id)

        endpoint = 'https://api.powerbi.com/v1.0/myorg{0}imports?' \
                   'datasetDisplayName={1}'.format(
                    self.workspace_url_part, report_name)

        file = {'file': data}
        response = requests.post(endpoint, auth=self.auth, files=file)

        if not response.ok:
            raise RuntimeError("Expected status code 200, but got {}".format(
                response.status_code))

    def get_datasets(self):
        """
        Get datasets through the Power BI Web API (v1.0)

        Returns:
            dict: The part of the JSON response as a dictionary
        """
        endpoint = 'https://api.powerbi.com/v1.0/myorg{0}datasets'.format(
                    self.workspace_url_part)
        response = requests.get(endpoint, auth=self.auth)

        if not response.ok:
            raise RuntimeError("Expected status code 200, but got {}".format(
                response.status_code))

        return response.json()['value']

    def search_dataset_by_name(self, dataset_name):
        """
        Search a dataset by name.

        Args:
            dataset_name: A dataset name to search

        Returns:
            str: A dataset ID if found or None if no dataset has been found.
        """
        datasets = self.get_datasets()

        for dataset in datasets:
            if dataset['name'] == dataset_name:
                return dataset['id']

    def delete_dataset(self, dataset_id):
        """
        Delete a dataset through the Power BI Web API (v1.0)
        """
        endpoint = 'https://api.powerbi.com/v1.0/myorg{0}datasets/{1}' \
            .format(self.workspace_url_part, dataset_id)
        response = requests.delete(endpoint, auth=self.auth)

        if not response.ok:
            raise RuntimeError("Expected status code 200, but got {}".format(
                response.status_code))


class BearerTokenAuth(AuthBase):
    """
    Provide a thin abstraction layer on a token for compatibility with
    :mod:`requests`.
    """
    def __init__(self, token):
        self._token = token

    def __call__(self, r):
        """
        Modify and return a request object by adding to its headers an
         'Authorization' line with a OAuth2 Bearer token.

        See also:

            :meth:`requests.auth.AuthBase.__call__`

        Args:
            r: a request object of the requests module
        """
        r.headers['Authorization'] = self._as_authorization_header()
        return r

    def _as_authorization_header(self):
        return 'Bearer {!s}'.format(self._token)


def get_access_token(application_id, application_secret, user_id,
                     user_password):
    """
    Obtains an access token from Azure

    Args:
        application_id: The client/application ID
        application_secret: The client/application secret
        user_id: A Power BI username
        user_password: A Power BI user password

    Returns:
        AzureToken: An access token
    """
    data = {
        'grant_type': 'password',
        'scope': 'openid',
        'resource': "https://analysis.windows.net/powerbi/api",
        'client_id': application_id,
        'client_secret': application_secret,
        'username': user_id,
        'password': user_password
    }

    endpoint = "https://login.microsoftonline.com/common/oauth2/token"
    response = requests.post(endpoint, data=data)

    if not response.ok:
        raise requests.ConnectionError(
            "Expected status code 200, but got {}. "
            "Invalid authentication credentials?".format(
                response.status_code))

    token = response.json()
    azure_token = AzureToken(
        token['token_type'], token['access_token'], token['expires_on'])
    return azure_token


class AzureToken(object):
    def __init__(self, token_type, access_token, expires_on, time_margin=5):
        self.token_type = token_type
        self.access_token = access_token
        self.expires_on = int(expires_on)
        self.time_margin = time_margin

        if self.token_type != 'Bearer':
            raise ValueError('Invalid authentication token.')

    @property
    def is_valid(self):
        now = time.time()
        return now < (self.expires_on - self.time_margin)
