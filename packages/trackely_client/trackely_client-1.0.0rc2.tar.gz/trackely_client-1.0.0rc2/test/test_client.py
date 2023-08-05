from __future__ import absolute_import
from trackely_client.api import APIClient
from binascii import unhexlify
from os.path import join
import httpretty
import unittest
import requests
import json


class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = APIClient('A', 'B')
        self.url = APIClient.BASE_URL

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    @httpretty.activate
    def test_create_campaign(self):
        httpretty.register_uri(httpretty.POST,
            join(self.url, 'campaigns'),
            body=json.dumps({
                'success': True,
                'campaign': {
                    'id': 'abc',
                }
            })
        )
        response = self.client.create_campaign(
            'This is a nice try'
        )
        self.assertTrue(response['success'])
        self.assertEqual(response['campaign']['id'], 'abc')

    @httpretty.activate
    def test_create_ad(self):
        httpretty.register_uri(httpretty.POST,
            join(self.url, 'ads'),
            body=json.dumps({
                'success': True,
                'ad': {
                    'id': 'abc',
                    'campaign_id': 'XYZ',
                    'pixel_id': 'FCK'
                }
            })
        )
        response = self.client.create_ad(
            'This is a nice try'
        )
        self.assertTrue(response['success'])
        self.assertEqual(response['ad']['id'], 'abc')
        self.assertEqual(response['ad']['campaign_id'], 'XYZ')
        self.assertEqual(response['ad']['pixel_id'], 'FCK')

    @httpretty.activate
    def test_create_pixel(self):
        httpretty.register_uri(httpretty.POST,
            join(self.url, 'pixels'),
            body=json.dumps({
                'success': True,
                'pixel': {
                    'id': 'abc',
                    'campaign_id': 'XYZ',
                    'url': join(self.url, 'pixel', 'XYZ.gif'),
                }
            })
        )

        res = self.client.create_pixel('Pixel')

        self.assertTrue(res['success'])
        self.assertEqual(res['pixel']['id'], 'abc')
        self.assertEqual(res['pixel']['campaign_id'], 'XYZ')
        self.assertEqual(res['pixel']['url'], join(self.url, 'pixel', 'XYZ.gif'))

    @httpretty.activate
    def test_get_campaigns(self):
        httpretty.register_uri(httpretty.GET,
            join(self.url, 'campaigns'),
            body=json.dumps({
                'success': True,
                'campaigns': [
                    {'id': 'abcd', 'description': 'One'},
                    {'id': 'dcba', 'description': 'Two'},
                ]
            })
        )

        res = self.client.get_campaigns()

        self.assertTrue(res['success'])
        self.assertEqual(len(res['campaigns']), 2)
        self.assertEqual(res['campaigns'][0]['id'], 'abcd')
        self.assertEqual(res['campaigns'][1]['id'], 'dcba')

    @httpretty.activate
    def test_get_ads(self):
        # ------------------- #
        # WITHOUT campaign ID #
        # ------------------- #
        httpretty.register_uri(httpretty.GET,
            join(self.url, 'ads'),
            body=json.dumps({
                'success': True,
                'ads': [
                    {'id': 'abcd', 'description': 'Three'},
                    {'id': 'dcba', 'description': 'Four'},
                ]
            })
        )

        res = self.client.get_ads()
        self.assertTrue(res['success'])
        self.assertIsInstance(res['ads'], list)
        self.assertEqual(len(res['ads']), 2)

        # ------------------- #
        # WITH campaign ID    #
        # ------------------- #
        httpretty.register_uri(httpretty.GET,
            join(self.url, 'ads'),
            body=json.dumps({
                'success': True,
                'ads': [
                    {
                        'id': 'abcd',
                        'description': 'Five',
                        'campaign_id': 'b' * 24,
                    },
                ]
            })
        )

        res = self.client.get_ads(campaign_id='b' * 24)
        self.assertTrue(res['success'])
        self.assertIsInstance(res['ads'], list)
        self.assertEqual(len(res['ads']), 1)
        self.assertEqual(res['ads'][0]['campaign_id'], 'b' * 24)

    @httpretty.activate
    def test_upload_ad_image(self):
        httpretty.register_uri(httpretty.PUT,
            join(self.url, 'ads'),
            body=json.dumps({
                'success': True,
                'ad': {
                    'image_url': 'http://algo',
                    'image_size': [1, 2]
                },
            })
        )

        res = self.client.upload_ad_image(
            ad_id='5b232a051df60ca01353ac90',
            image=unhexlify((
                "47494638396101000100800000ff"
                "ffff00000021f90401000000002c"
                "00000000010001000002024401003b"
            ))
        )

        self.assertTrue(res['success'])
        self.assertEqual(res['ad']['image_url'], 'http://algo')
        self.assertIsInstance(res['ad']['image_size'], list)
        self.assertEqual(len(res['ad']['image_size']), 2)

    @httpretty.activate
    def test_get_html_tag(self):
        httpretty.register_uri(httpretty.GET,
            join(self.url, 'ads'),
            body=json.dumps({
                'success': True,
                'html': '<div>something</div>',
            })
        )

        res = self.client.get_ad_html_tag(
            ad_id='5b232a051df60ca01353ac90'
        )

        self.assertTrue(res['success'])
        self.assertEqual(res['html'], '<div>something</div>')

    @httpretty.activate
    def test_modify_ad(self):
        httpretty.register_uri(httpretty.PUT,
            join(self.url, 'ads'),
            body=json.dumps({
                'success': True,
                'ad': {
                    'id': 'ABC',
                    'description': 'Mexico',
                    'target_url': 'http://mexico.com/HOLA'
                },
            })
        )

        res = self.client.modify_ad(ad_id='ABC',
            description='Mexico',
            target_url='http://mexico.com/HOLA'
        )

        self.assertTrue(res['success'])
        self.assertEqual(res['ad']['id'], 'ABC')
        self.assertEqual(res['ad']['target_url'], 'http://mexico.com/HOLA')

    @httpretty.activate
    def test_get_single_ad(self):
        httpretty.register_uri(httpretty.GET,
            join(self.url, 'ads'),
            body=json.dumps({
                'success': True,
                'ad': {
                    'id': 'ABC',
                    'description': 'Mexico',
                    'target_url': 'http://mexico.com/HOLA'
                },
            })
        )

        res = self.client.get_ad(ad_id='ABC')

        self.assertTrue(res['success'])
        self.assertIn('ad', res)
        self.assertEqual(res['ad']['id'], 'ABC')

    @httpretty.activate
    def test_get_history(self):
        httpretty.register_uri(httpretty.GET,
            join(self.url, 'history'),
            body=json.dumps({
                'success': True,
                'requests': [
                    {
                        'user_agent': 'A user agent; otro;',
                        'date': '2018-01-02 03:04:05-0700',
                    },
                    {
                        'user_agent': 'This is better',
                        'date': '2018-01-02 03:09:05-0700'
                    }
                ],
            })
        )

        res = self.client.get_history(ad_id='abcd', sorted_by='latest')

        self.assertTrue(res['success'])
        self.assertIn('requests', res)


if __name__ == '__main__':
    unittest.main()