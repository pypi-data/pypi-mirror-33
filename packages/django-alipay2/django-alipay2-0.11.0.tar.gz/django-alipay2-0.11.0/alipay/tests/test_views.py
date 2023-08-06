from django.test import RequestFactory, TestCase, override_settings

from alipay.models import AlipayPayment
from alipay.views import AlipayRedirectView


class AlipayRedirectViewTest(TestCase):
    def redirect_payment(self, payment):
        view = AlipayRedirectView.as_view()
        factory = RequestFactory()
        req = factory.get('/')

        return view(req, out_no=payment.out_no)

    @override_settings(ALIPAY={'seller_email': 'a@a.aa',
                               'pid': 'real alipay pid',
                               'key': 'real alipay key',
                               'gateway': 'https://a.aa/?'})
    def test_single_seller(self):
        payment = AlipayPayment.objects.create(
            out_no='2',
            subject='充值',
            body='1年365元',
            amount_total=0.01,
        )
        resp = self.redirect_payment(payment)
        self.assertTrue('a.aa' in resp.url)
        payment.refresh_from_db()
        self.assertEqual(payment.seller_email, 'a@a.aa')
