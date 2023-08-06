"""
Example views for interactive testing of payment with netaxept.

You should restrict access (maybe with 'staff_member_required') if you choose to add this to your urlconf.
"""

from django.forms import forms, IntegerField, BooleanField, CharField, URLField
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from netaxept.gateway import get_payment_terminal_url
from ..actions import register


class PayForm(forms.Form):
    order_number = CharField(max_length=32)
    amount = IntegerField(min_value=1,
                          help_text='(In smallest currency unit, for instance write "100" for 1 nok)')
    currency_code = CharField(min_length=3, max_length=3, initial='NOK')
    redirect_url = URLField(initial="http://slashdot.org/")
    auto_auth = BooleanField(required=False, initial=False,
                             help_text='(Select this to automatically authorize the payment)')


def pay(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = PayForm(request.POST)
        if form.is_valid():
            registration = register(
                order_number=form.cleaned_data['order_number'],
                amount=form.cleaned_data['amount'],
                currency_code=form.cleaned_data['currency_code'],
                redirect_url=form.cleaned_data['redirect_url'],
                auto_auth=form.cleaned_data['auto_auth'],
            )
            return redirect(get_payment_terminal_url(registration.transaction_id))
    else:
        form = PayForm()

    return render(request, 'netaxept/example/form.html', {
        'title': 'Payment',
        'form': form
    })
