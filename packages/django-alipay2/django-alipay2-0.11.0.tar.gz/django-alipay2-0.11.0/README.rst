==============
django-alipay2
==============

提供django下alipay直接支付接口

Quick start
-----------
1. Install::

    pip install django_alipay2

2. Add "alipay" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'alipay',
    ]

3. [Optional] Include the alipay URLconf in your project urls.py like this::

    url(r'^alipay/', include('alipay.urls')),

4. Migrate::

    python manage.py migrate

5. Add config 'ALIPAY' to settings.py like this::

    # account below is for sandbox
    ALIPAY = {
        'pid': '2088101122136241',
        'key': '760bdzec6y9goq7ctyx96ezkz78287de',
        'seller_email': 'overseas_kgtest@163.com',
        'gateway': 'https://openapi.alipaydev.com/gateway.do?',
        'server_url': 'http://localhost:8000'
    }

    # you may add an 'api_provider' to support multiple seller
    ALIPAY = {
        'api_provider': 'some_package.sub_package.get_alipay_alipay'  # input:seller_email, output:AlipayAPI
    }

6. Create alipay redirect::

    import uuid
    payment = AlipayPayment.objects.create(
        out_no=uuid.uuid4(),
        subject='充值',
        body='1年365元',
        amount_total=0.01,
        user=None, # 可以指定user
        seller_email='your_seller_email@domain.com',
        # reference_id='1' # 可选
    )
    return redirect('alipay_redirect', out_no=payment.out_no)

