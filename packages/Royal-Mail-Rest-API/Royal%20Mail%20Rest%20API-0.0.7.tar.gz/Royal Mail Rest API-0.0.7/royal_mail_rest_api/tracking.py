import requests
from royal_mail_rest_api.api import RoyalMailBaseClass


class TrackingApi(RoyalMailBaseClass):
    """
    Start class for royal mail shipping api
    """
    summary_url = 'mailPieces/{}/summary'
    pod_url = 'mailPieces/{}/proofOfDelivery'
    history_url = 'mailPieces/{}/history'

    def __init__(self, client_id, client_secret):
        """
        Instantiate, store client_id and secret, build headers
        :param client_id:
        :param client_secret:
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self._create_headers()

    def _create_headers(self):
        """
        Create the required headers for interacting with the tracking api
        :return: Nothing
        """
        self.header = {'X-IBM-Client-Id': self.client_id,
                       'X-IBM-Client-Secret': self.client_secret,
                       'accept': 'application/json'}

    def summary(self, tracking_number):
        """
        takes 13 digit tracking number and requests summary data
        :param tracking_number:
        :return: tracking_summary
        """
        summary_url = self.summary_url.format(tracking_number)
        result = requests.get('{}/{}'.format(self.url, summary_url), headers=self.header)
        result.raise_for_status()
        return result.json()

    def proof_of_delivery(self, tracking_number):
        """
        recover proof of delivery
        :param tracking_number:
        :return:
        """
        pod_url = self.summary_url.format(tracking_number)
        result = requests.get('{}/{}'.format(self.url, pod_url), headers=self.header)
        result.raise_for_status()
        return result.json()

    def history(self, tracking_number):
        """
        Return history for a tracked item
        :param tracking_number:
        :return:
        """
        history_url = self.history_url.format(tracking_number)
        result = requests.get('{}/{}'.format(self.url, history_url), headers=self.header)
        result.raise_for_status()
        return result.json()



