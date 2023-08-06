import requests
import sys

class Client:

    bearer_token_refresh_interval = 55 # this is in minutes, change it as necessary

    host = ''
    username = None
    password = None
    client_id = None
    client_secret = None
    entity_id = None
    headers = {}

    def __init__(self,
                 host,
                 username=None,
                 password=None,
                 client_id=None,
                 client_secret=None,
                 entity_id=None):
        self.host = host
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.entity_id = entity_id

    # def set_headers(self):
    #     self.headers = {}
    #
    #     if self.client_id is None and self.client_secret is None:
    #         self.headers["apiAccessKeyId"] = self.username
    #         self.headers["apiSecretAccessKey"] = self.password
    #     elif self.username is None and self.password is None:
    #         self.check_and_refresh_bearer_token()
    #
    #     # TODO: set content type to application/json
    #
    #     if self.entity_id is not None:
    #         self.headers["zuora-entity-ids"] = self.entity_id
    #
    # def check_and_refresh_bearer_token(self):
    #     print("hello world...")
    #     # TODO: 1. get the time difference between current time and bearer token retrieval time
    #     # TODO: 2. if time difference is greater than 55 minutes (or whatever the unit is
    #     # TODO:    call the get_bearer_token method
    #     # TODO: 3. add a new key value pair of key => "Authorization", value => "Bearer some-bearer-token"
    #
    # def get(self, endpoint, optional_headers=None):
    #     if optional_headers is not None:
    #         request_headers = self.merge_headers(optional_headers)
    #
    #     url = "%s/%s" % (self.host, endpoint)
    #
    #     return requests.get(url, headers=request_headers)
    #
    # def post(self, endpoint, payload=None, optional_headers=None):
    #     if optional_headers is not None:
    #         request_headers = self.merge_headers(optional_headers)
    #
    #     r = requests.post(url=endpoint, data=payload, headers=request_headers)
    #
    # def put(self, endpoint, payload=None, optional_headers=None):
    #     if optional_headers is not None:
    #         request_headers = self.merge_headers(optional_headers)
    #
    #     r = requests.put(url=endpoint, data=payload, headers=request_headers)
    #
    # def delete(self, endpoint, optional_headers=None):
    #     if optional_headers is not None:
    #         request_headers = self.merge_headers(optional_headers)
    #
    #     r = requests.delete(url=endpoint, headers=request_headers)
    #
    # def merge_headers(self, h):
    #     if sys.version_info >= (3,5):
    #         headers = {**self.headers, **h}
    #     else:
    #         headers = self.headers.copy()
    #         headers.update(h)
    #
    #     return headers

