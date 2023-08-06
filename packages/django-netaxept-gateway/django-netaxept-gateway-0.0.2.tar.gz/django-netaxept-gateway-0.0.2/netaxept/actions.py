import suds
from structlog import get_logger

from .gateway import do_register, do_process
from .models import Payment, Operation

logger = get_logger()


class NetaxeptException(Exception):
    def __str__(self):
        return repr(self.msg)


class PaymentNotAuthorized(NetaxeptException):
    msg = 'Payment not authorized'


class AmountAlreadyCaptured(NetaxeptException):
    msg = 'Amount already captured'


class NoAmountCaptured(NetaxeptException):
    msg = 'No amount capture'


class PaymentRegistrationNotCompleted(NetaxeptException):
    msg = 'Payment registration not completed'


def register(order_number, amount, currency_code, redirect_url, description=None, auto_auth=False):
    """
    Registering a payment is the first step for netaxept, before taking the user to the netaxept
    terminal hosted page.

    See: https://shop.nets.eu/web/partners/register

    :param order_number: An alphanumerical string identifying the payment (max 32 characters)
    :param amount: The amount in smallest currency unit
    :param currency_code: The 3 letter currency code
    :param redirect_url: We decide during registration where we want the user to be redirected after the end of
            the next phase (after the user adds his CC information on the terminal pages)
    :param description: A text (MaxLength: 4000)
    :param auto_auth: If set to True, authorization will be automatically run at after the end of the next phase
            (after the user adds his CC information on the terminal pages).
    :return: The payment registration (either successful or unsuccesful)
    :raises SOAP exceptions
    """
    logger.info('netaxept-register', order_number=order_number, amount=amount,
                currency_code=currency_code, redirect_url=redirect_url, description=description, auto_auth=auto_auth)
    payment = Payment(
        amount=amount,
        currency_code=currency_code,
        order_number=order_number,
        description=description,
        redirect_url=redirect_url,
        auto_auth=auto_auth
    )
    try:
        response = do_register(
            order_number=payment.order_number,
            amount=payment.amount,
            currency_code=payment.currency_code,
            description=payment.description,
            redirect_url=payment.redirect_url,
            auto_auth=payment.auto_auth)
        payment.transaction_id = response.TransactionId
        payment.success = True
    except suds.WebFault as e:
        logger.error('netaxept-register', exc_info=e)
        _handle_response_exception(e, payment)
    finally:
        payment.save()
    return payment


def sale(payment_id):
    logger.info('netaxept-sale', payment_id=payment_id)
    payment = Payment.objects.get(id=payment_id)
    if not payment.success:
        logger.error('netaxept-sale-payment-registration-not-complete')
        raise PaymentRegistrationNotCompleted()
    operation = Operation(
        payment_id=payment_id,
        transaction_id=payment.transaction_id,
        operation=Operation.SALE,
    )
    _handle_operation(operation)
    return operation


def auth(payment_id):
    logger.info('netaxept-auth', payment_id=payment_id)
    payment = Payment.objects.get(id=payment_id)
    if not payment.success:
        logger.error('netaxept-auth-payment-registration-not-complete')
        raise PaymentRegistrationNotCompleted()
    operation = Operation(
        payment_id=payment_id,
        transaction_id=payment.transaction_id,
        operation=Operation.AUTH,
    )
    _handle_operation(operation)
    return operation


def capture(payment_id, amount=None):
    """
    Capture the amount for an already authorized Payment.

    Assumes authorization occured previously (we cannot check in the database because sometimes pre-auth was used
    and only nets knows the status of that).

    :param payment_id: The id of a payment where registration and authorization were succesfully completed.
    :param amount: An optional positive number, must not be larger than what remains on this payment.
                   If parameter is absent, then the amount remaining on this payment will be captured.
    :return: the operation
    :raises SOAP exceptions
    """
    logger.info('netaxept-capture', payment_id=payment_id, amount=amount)
    payment = Payment.objects.get(id=payment_id)
    if not payment.success:
        logger.error('netaxept-capture-payment-registration-not-complete')
        raise PaymentRegistrationNotCompleted()
    operation = Operation(
        payment_id=payment_id,
        transaction_id=payment.transaction_id,
        operation=Operation.CAPTURE,
        amount=amount,
    )
    _handle_operation(operation)
    return operation


def credit(payment_id, amount=None):
    """
    Credit the amount for a payment that was either authd and captured, or sale'd.

    Assumes capture or sale occured previously.
    XXX: It is in fact possible to see those operations in the db, analyse if it's a good idea to pre-check.

    :param payment_id: The id of a payment where money was already taken.
    :param amount: An optional positive number, must not be larger than what remains on this payment.
                   If parameter is absent, then the amount remaining on this payment will be credited.
    :return: the operation
    :raises SOAP exceptions
    """
    logger.info('netaxept-credit', payment_id=payment_id, amount=amount)
    payment = Payment.objects.get(id=payment_id)
    if not payment.success:
        logger.error('netaxept-credit-payment-registration-not-complete')
        raise PaymentRegistrationNotCompleted()
    operation = Operation(
        payment_id=payment_id,
        transaction_id=payment.transaction_id,
        operation=Operation.CREDIT,
        amount=amount,
    )
    _handle_operation(operation)
    return operation


def _handle_operation(operation):
    try:
        # XXX: Should read the response and not only rely on the REST exception.
        do_process(
            transaction_id=operation.transaction_id,
            operation=operation.operation,
            amount=getattr(operation, 'amount', None),
        )
        operation.success = True
    except suds.WebFault as e:
        _handle_response_exception(e, operation)
    finally:
        operation.save()


def _handle_response_exception(exception, obj):
    logger.error('netaxept-gateway-invocation-error', exc_info=exception)
    obj.success = False
    bbsexception = getattr(exception.fault.detail, 'BBSException', None)
    if bbsexception:
        result = bbsexception.Result
        obj.response_code = str(result.ResponseCode)
        obj.response_source = result.ResponseSource
        obj.response_text = result.ResponseText
        obj.message = bbsexception.Message  # XXX: I think we're currently not saving this to the db.
    else:
        obj.response_text = exception.fault.detail[0].Message
    raise exception
