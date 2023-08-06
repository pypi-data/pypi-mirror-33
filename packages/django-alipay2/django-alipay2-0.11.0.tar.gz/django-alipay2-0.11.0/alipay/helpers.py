from django.conf import settings
from django.utils.module_loading import import_string

from alipay.alipay import AlipayClient

DEFAULT_GATEWAY = 'https://mapi.alipay.com/gateway.do?'


def get_alipay_api(seller_email=None) -> 'AlipayAPI':
    api_provider_name = settings.ALIPAY.get('api_provider')
    if api_provider_name:
        api_provider = import_string(api_provider_name)
        return api_provider(seller_email)

    else:
        assert not seller_email or seller_email == settings.ALIPAY['seller_email'], 'seller_email和settings不匹配'

        return AlipayAPI(
            pid=settings.ALIPAY['pid'],
            key=settings.ALIPAY['key'],
            seller_email=settings.ALIPAY['seller_email'],
            gateway=settings.ALIPAY.get('gateway')
        )


class AlipayAPI:
    def __init__(self, pid, key, seller_email, gateway=None):
        self.seller_email = seller_email
        self.pid = pid
        self.key = key
        self.gateway = gateway or DEFAULT_GATEWAY

    @property
    def client(self):
        return AlipayClient(self.pid, self.key, self.seller_email, gateway=self.gateway)
