import requests
import datetime
from royal_mail_rest_api.api import RoyalMailBaseClass
from royal_mail_rest_api.errors import RoyalMailError


class ShippingApi(RoyalMailBaseClass):
    """
    Royal Mail Shipping Class, used to communicate with the Royal Mail Rest API to create labels
    """
    token_url = '/shipping/v2/token'
    post_domestic_url = '/shipping/v2/domestic'
    delete_shipment_url = '/shipping/v2/'
    put_shipment_label_url = '/shipping/v2/'
    put_shipment_update_url = '/shipping/v2/'
    post_manifest_url = '/shipping/v2/manifest'

    def __init__(self, client_id, client_secret, username, password):
        """
        authenticate with the Shipping service.
        Password is an SHA1 hashed password. The royal mail develop tools have an html file to do this for you
        https://developer.royalmail.net/node/18564
        https://developer.royalmail.net/sites/developer.royalmail.net/files/rmg_shipping_api_v2_rest_password_generator_0.zip
        :param client_id:
        :param client_secret:
        :param username:
        :param password:
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password

        # make a date 30 days in the past so the token is expired.
        self.token_created = datetime.datetime.now() - datetime.timedelta(days=30)
        self._create_authentication_header()

    def _create_authentication_header(self):
        self.header = {'X-IBM-Client-Id': self.client_id,
                       'X-IBM-Client-Secret': self.client_secret,
                       'x-rmg-user-name': self.username,
                       'x-rmg-password': self.password,
                       'accept': 'application/json',
                       'content-type': 'application/json'}

    def _create_token_header(self):
            self.tokenheader = {'X-IBM-Client-Id': self.client_id,
                                'X-IBM-Client-Secret': self.client_secret,
                                'x-rmg-auth-token': self.token,
                                'accept': 'application/json'}

    def get_token(self):
        """

        Summary
        =======

        Method to get a JWT token

        Description
        -----------

        This method will accept a DMO/NEOPOST user name and password.
        On successful validation of the user credential it will issue a JWT token to the user which will be
        valid for 4 hours. On subsequent requests, user will pass the JWT token in the request header.

        :return:
        """
        # Token expires after 4 hours, lets give it 3.45 hours to be safe
        if self.token_created < (datetime.datetime.now() - datetime.timedelta(hours=3, minutes=45)):
            result = requests.get('{}{}'.format(self.url, self.token_url), headers=self.header)
            result.raise_for_status()
            result = result.json()
            self.token = result['token']
            self.token_created = datetime.datetime.now()
            self._create_token_header()

    def _error_handler(self, result):
        """
        Deal with returning a useful error up the chain, not just an http response error for the client app to deal with.
        :param result:
        :return:
        """
        try:
            result.raise_for_status()
        except Exception:
            raise RoyalMailError(result.json())


    def post_domestic(self, data):
        """

        Summary
        =======

        Operation to create a shipment

        Description
        -----------
        This method will take a domestic shipment request in the body and on successful response,
        it will return the shipment numbers and item details.
        :return:
        """
        self.get_token()
        data = data
        result = requests.post('{}{}'.format(self.url, self.post_domestic_url), json=data, headers=self.tokenheader)
        self._error_handler(result)
        return result.json()

    def put_shipment(self, shipment_number, data):
        """
        Summary
        =======

        updateShipment

        Description
        -----------

        Update a shipment. Send a shipment request in body. On successful response,
        it will return shipment number and warnings. Service related information can not be updated,
        and if passed as part of request, it will be ignored.

        :return:
        """
        self.get_token()
        result = requests.put('{}{}{}'.format(self.url, self.put_shipment_update_url, shipment_number), json=data,
                              headers=self.tokenheader)
        self._error_handler(result)
        return result.json()

    def delete_shipment(self, shipment_number):
        """
        Description

        Delete a shipment. Send a shipment identifier in Url. Successful response will be 200 with no content.

        :return:
        """
        self.get_token()
        result = requests.delete('{}{}{}'.format(self.url, self.delete_shipment_url, shipment_number),
                                 headers=self.tokenheader)
        self._error_handler(result)
        return result.json()

    def put_shipment_label(self, shipment_number):
        """

        Description
        -----------
        This method returns a label for the shipment identifier passed in the url.

        :return:
        """
        self.get_token()
        result = requests.put('{}{}{}/label'.format(self.url, self.put_shipment_label_url, shipment_number),
                              headers=self.tokenheader)
        self._error_handler(result)
        return result.json()

    def post_manifest(self, manifest_options=None):
        """

        Description
        -----------
        This method creates a shipping manifest

        :return:
        """
        self.get_token()
        result = requests.post('{}{}'.format(self.url, self.post_manifest_url), json=manifest_options,
                               headers=self.tokenheader)
        self._error_handler(result)
        return result.json()

    def put_manifest(self, sales_order_number=None, manifest_batch_number=None):
        """

        Description
        -----------

        This method return a manifest label for a previously manifested shipment.

        :return:
        """
        self.get_token()
        items = {'salesOrderNumber': sales_order_number, 'manifestBatchNumber': manifest_batch_number}
        params = ['{}={}'.format(k, str(v)) for k, v in items.items() if v is not None]

        query_params = '&'.join(params)

        result = requests.put('{}{}?{}'.format(self.url, self.post_manifest_url, query_params),
                              headers=self.tokenheader)
        self._error_handler(result)
        return result.json()
