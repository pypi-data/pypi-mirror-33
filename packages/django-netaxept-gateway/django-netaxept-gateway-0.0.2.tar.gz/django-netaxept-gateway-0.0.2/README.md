django-netaxept-gateway
======================= 

Tested on python 3.5 and django 2.0.7


Installation
------------

    pip install django-netaxept-gateway


Configuration
-------------

Add ``netaxept.apps.NetaxeptConfig`` to ``settings.INSTALLED_APPS`` and run:

    ./manage.py migrate


Configure `NETAXEPT_MERCHANTID` and `NETAXEPT_TOKEN`

By default this library connects to the test netaxept endpoints,
to use the production environment you must set:

`NETAXEPT_TERMINAL` to  `https://epayment.nets.eu/Terminal/default.aspx`

`NETAXEPT_WSDL` to `https://epayment.nets.eu/netaxept.svc?wsdl`


IMPORTANT
---------

- Amounts are in smallest currenty unit. For instance one NOK is represented in netaxept as "100 NOK".

- Payment objects have a `success` field that indicate whether the payment was _registered_ without error, it says nothing about whether we got the money or not
(To receive money the payment needs to go thru `auth` then `capture` , or thru `sale`).


Netaxept Reference
------------------

https://shop.nets.eu/web/partners/home

Read this first: https://shop.nets.eu/web/partners/flow-outline

API details: https://shop.nets.eu/web/partners/appi

Test card numbers: https://shop.nets.eu/web/partners/test-cards


Design
------

We don't allow payment registration with `autoSale` because it becomes very difficult to determine the status of the operation when it is carried-out automatically.


TODO
----

- Unit tests
- On prod (where debug is turned off), errors in the admin after invoking the gateway are shown as a useless grey page.


To work on this code
--------------------

    pip install -e .

