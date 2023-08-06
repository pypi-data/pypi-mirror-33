from django.test import TestCase, override_settings

from alipay.helpers import get_alipay_api


def dummy_api_provider(seller_email=None):
    return 'some_api'


class HelpersTest(TestCase):
    @override_settings(ALIPAY={
        'pid': 'hello',
        'key': 'world',
        'seller_email': 'default@seller',
    })
    def test_get_alipay_api_default(self):
        api = get_alipay_api('default@seller')
        self.assertEqual(api.pid, 'hello')

        api = get_alipay_api(None)
        self.assertEqual(api.pid, 'hello')
        self.assertEqual(api.seller_email, 'default@seller')

        with self.assertRaises(AssertionError) as cm:
            api = get_alipay_api('other@seller')
        self.assertIsNotNone(cm.exception)

    @override_settings(ALIPAY={
        'pid': 'hello',
        'key': 'world',
        'seller_email': 'default@seller',
        'api_provider': __name__ + '.dummy_api_provider'
    })
    def test_get_alipay_api_with_provider(self):
        api = get_alipay_api('defualt@seller')
        self.assertEqual(api, 'some_api')
