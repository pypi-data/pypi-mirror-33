import requests
from django.conf import settings
from suds.client import Client

MERCHANTID = getattr(settings, 'NETAXEPT_MERCHANTID', '')
TOKEN = getattr(settings, 'NETAXEPT_TOKEN', '')

WSDL = getattr(settings, 'NETAXEPT_WSDL', 'https://epayment-test.bbs.no/netaxept.svc?wsdl')
TERMINAL = getattr(settings, 'NETAXEPT_TERMINAL', 'https://epayment-test.bbs.no/Terminal/default.aspx')


def do_register(order_number, amount, currency_code, description, redirect_url, auto_auth):
    client = _get_client()
    request = _get_basic_register_request(client, redirect_url, language=None, auto_auth=auto_auth)

    order = _get_netaxept_object(client, 'Order')
    order.OrderNumber = order_number
    order.Amount = amount
    order.CurrencyCode = currency_code
    order.UpdateStoredPaymentInfo = None

    request.Order = order
    request.Description = description
    return client.service.Register(MERCHANTID, TOKEN, request)


def do_process(transaction_id, operation, amount=None):
    client = _get_client()
    request = _get_netaxept_object(client, 'ProcessRequest')
    request.Operation = operation
    request.TransactionId = transaction_id
    if amount:
        request.TransactionAmount = amount
    return client.service.Process(MERCHANTID, TOKEN, request)


def get_payment_terminal_url(transaction_id):
    request = requests.get(
        TERMINAL,
        params={'merchantId': MERCHANTID, 'transactionId': transaction_id})
    return request.url


def _get_client():
    return Client(WSDL, faults=True)


def _get_netaxept_object(client, obj):
    return client.factory.create('ns1:%s' % obj)


def _get_basic_register_request(client, redirecturl, language, auto_auth):
    """
    Return a basic register request without order
    """
    environment = _get_netaxept_object(client, 'Environment')
    environment.Language = None
    environment.OS = None
    environment.WebServicePlatform = 'SUDS'

    terminal = _get_netaxept_object(client, 'Terminal')
    terminal.AutoAuth = auto_auth
    terminal.Language = language
    terminal.OrderDescription = None
    terminal.RedirectOnError = None
    terminal.RedirectUrl = redirecturl

    request = _get_netaxept_object(client, 'RegisterRequest')
    request.AvtaleGiro = None
    request.CardInfo = None
    request.Customer = None
    request.DnBNorDirectPayment = None
    request.Environment = environment
    request.ServiceType = None
    request.Terminal = terminal
    request.Recurring = None

    return request
