import requests
import json
import os
import sys

is_3 = sys.version_info >= (3, 0)

class Error(Exception): pass
class APIError(Error): pass


class APIClient(object):
    BASE_URL = 'https://apps.edws.co/trackely/api'

    def __init__(self, key, secret, base_url=BASE_URL):
        self.key = key
        self.secret = secret
        self.base_url = base_url

    @property
    def headers(self):
        return {
            'Authorization': '{} {}'.format(self.key, self.secret)
        }

    def create_campaign(self, description=None):
        url = os.path.join(self.base_url, 'campaigns')
        response = requests.post(url,
            headers=self.headers,
            data={'description': description}
        )
        return response.json()

    def create_ad(self, description=None, campaign_id=None):
        url = os.path.join(self.base_url, 'ads')

        response = requests.post(url,
            headers=self.headers,
            data={
                'description': description,
                'campaign_id': campaign_id,
            }
        )

        return response.json()

    def upload_ad_image(self, ad_id=None, image=None):
        url = os.path.join(self.base_url, 'ads')
        response = requests.put(url,
            headers=self.headers,
            params={
                'action': 'upload_image',
                'ad_id': ad_id
            },
            files={
                'file': image
            }
        )

        return response.json()

    def get_ad_html_tag(self, ad_id=None):
        url = os.path.join(self.base_url, 'ads')
        response = requests.get(url,
            headers=self.headers,
            params={
                'action': 'tag',
                'ad_id': ad_id,
            },
        )

        return response.json()

    def create_pixel(self, description=None, campaign_id=None):
        url = os.path.join(self.base_url, 'pixels')
        response = requests.post(url,
            headers=self.headers,
            data={
                'description': description,
                'campaign_id': campaign_id,
            }
        )

        return response.json()

    def get_campaigns(self):
        url = os.path.join(self.base_url, 'campaigns')
        response = requests.get(url,
            headers=self.headers,
        )

        return response.json()

    def get_ads(self, **params):
        """ Supported parameters by API: campaign_id
        """

        url = os.path.join(self.base_url, 'ads')
        response = requests.get(url,
            headers=self.headers,
            params=params,
        )

        return response.json()

    def get_ad(self, ad_id):
        url = os.path.join(self.base_url, 'ads')
        response = requests.get(url,
            headers=self.headers,
            params={'ad_id': ad_id}
        )

        return response.json()

    def modify_ad(self, ad_id, **params):
        """ Modify basic values from an ad
        Supported parameters by API:
            - target_url
            - description
        """

        url = os.path.join(self.base_url, 'ads')
        response = requests.put(url,
            headers=self.headers,
            params={'ad_id': ad_id},
            data=params
        )

        return response.json()

    def get_history(self, ad_id=None, sorted_by=None):
        """
         * sorted_by: latest
         * ad_id: Ad ID
        """

        url = os.path.join(self.base_url, 'history')
        params = {}

        ad_id and params.update({'ad_id': ad_id})
        sorted_by and params.update({'sorted': sorted_by})

        response = requests.get(url,
            headers=self.headers,
            params=params,
        )

        return response.json()

if __name__ == '__main__':
    client = APIClient('5afb53881df60c27f1721333',
        'ea8d90148485fb6d10c4f3e677b65ef8922cf88893cc678c0b6a5bfe579e0ced',
        base_url='http://localhost:8080/api')
    response = client.create_campaign('Hola mundo')
    campaign = response['campaign']
    response = client.create_pixel('Un pixel',
        campaign_id=campaign['id'],
        )
    pixel = response['pixel']
    response = client.create_ad()

    print(campaign)
    print(pixel)
