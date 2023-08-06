from django.db import models
from django.db.models import CASCADE


class TransactionBase(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)
    success = models.BooleanField()
    response_source = models.CharField(max_length=20, null=True, blank=True)
    response_code = models.CharField(max_length=3, null=True, blank=True)
    response_text = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True


class Payment(TransactionBase):
    # Failed payments will sometimes have a null transaction id, we want to allow more
    # than one of those in the database, so we allow null in transaction_id
    transaction_id = models.CharField(max_length=32, unique=True, null=True, blank=True)
    order_number = models.CharField(max_length=32)
    amount = models.PositiveIntegerField()
    currency_code = models.CharField(max_length=3)
    description = models.CharField(max_length=255, null=True, blank=True)
    redirect_url = models.CharField(max_length=255)
    auto_auth = models.BooleanField()

    def __str__(self):
        return '{} {} - {}'.format(self.amount, self.currency_code, self.transaction_id)


class Operation(TransactionBase):
    AUTH = 'AUTH'
    SALE = 'SALE'
    CAPTURE = 'CAPTURE'
    CREDIT = 'CREDIT'
    ANNUL = 'ANNUL'

    OPERATION_CHOICES = (
        (AUTH, 'AUTH'),
        (SALE, 'SALE'),
        (CAPTURE, 'CAPTURE'),
        (CREDIT, 'CREDIT'),
        (ANNUL, 'ANNUL')
    )

    transaction_id = models.CharField(max_length=32)
    payment = models.ForeignKey(Payment, related_name='operations', on_delete=CASCADE)
    operation = models.CharField(max_length=7, choices=OPERATION_CHOICES)
    amount = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return '{} {} - {}'.format(self.operation, self.amount or '', self.transaction_id)
