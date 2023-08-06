from django.conf.urls import url
from django.contrib import admin
from django.db.models import Prefetch
from django.forms import forms, IntegerField
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.html import format_html

from . import actions
from .models import Payment, Operation


def link_to_payment(obj):
    payment = obj.payment
    text = '{} - {}'.format(payment.amount, payment.currency_code)
    return format_html(
        '<a href="{}">{}</a>',
        reverse('admin:netaxept_payment_change', args=(payment.pk,)),
        text)


link_to_payment.short_description = 'Payment'


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ['created', 'success', 'operation', 'amount', 'response_code', 'response_source', 'response_text',
                    link_to_payment]
    search_fields = ['transaction_id', 'amount']
    list_filter = ['success', 'operation']

    readonly_fields = ['created', 'modified', link_to_payment]


class OperationInline(admin.TabularInline):
    model = Operation
    ordering = ['-created']
    fields = readonly_fields = ['created', 'success', 'operation', 'amount', 'response_code', 'response_source',
                                'response_text']
    show_change_link = True
    can_delete = False
    extra = 0


def operation_count(payment):
    return payment.operations.count()


class AuthPaymentForm(forms.Form):
    pass


def auth_payment_form(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    if request.method == 'POST':
        form = AuthPaymentForm(request.POST)
        if form.is_valid():
            result = actions.auth(
                payment_id=payment_id)
            # As confirmation we take the user to the edit page of the auth operation.
            return HttpResponseRedirect(reverse('admin:netaxept_operation_change', args=[result.id]))
    else:
        form = AuthPaymentForm()

    return render(
        request,
        'admin/netaxept/form.html',
        {
            'title': 'Auth registered payment of {} {}'.format(payment.amount, payment.currency_code),
            'form': form,
            'opts': Payment._meta,  # Used to setup the navigation / breadcrumbs of the page
        }
    )


class CapturePaymentForm(forms.Form):
    amount = IntegerField(min_value=0, required=False,
                          help_text='If left empty, then the amount remaining on this payment will be captured.')


def capture_payment_form(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    if request.method == 'POST':
        form = CapturePaymentForm(request.POST)
        if form.is_valid():
            result = actions.capture(
                payment_id=payment_id,
                amount=form.cleaned_data['amount'])
            # As confirmation we take the user to the edit page of the capture operation.
            return HttpResponseRedirect(reverse('admin:netaxept_operation_change', args=[result.id]))
    else:
        form = CapturePaymentForm()

    return render(
        request,
        'admin/netaxept/form.html',
        {
            'title': 'Capture money from registered payment of {} {}'.format(payment.amount, payment.currency_code),
            'form': form,
            'opts': Payment._meta,  # Used to setup the navigation / breadcrumbs of the page
        }
    )


class CreditPaymentForm(forms.Form):
    amount = IntegerField(min_value=0, required=False,
                          help_text='If left empty, then the amount remaining on this payment will be credited.')


def credit_payment_form(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    if request.method == 'POST':
        form = CreditPaymentForm(request.POST)
        if form.is_valid():
            result = actions.credit(
                payment_id=payment_id,
                amount=form.cleaned_data['amount'])
            # As confirmation we take the user to the edit page of the credit operation.
            return HttpResponseRedirect(reverse('admin:netaxept_operation_change', args=[result.id]))
    else:
        form = CreditPaymentForm()

    return render(
        request,
        'admin/netaxept/form.html',
        {
            'title': 'Credit money from registered payment of {} {}'.format(payment.amount, payment.currency_code),
            'form': form,
            'opts': Payment._meta,  # Used to setup the navigation / breadcrumbs of the page
        }
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ['created', 'success', 'amount', 'currency_code', 'order_number', 'description', 'redirect_url',
                    'transaction_id', operation_count]
    search_fields = ['transaction_id', 'order_number', 'amount', 'description']
    list_filter = ['success', 'currency_code']

    readonly_fields = ['created', 'modified', 'auth_button', 'capture_button', 'credit_button']
    inlines = [OperationInline]

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .prefetch_related(Prefetch('operations'))

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(
                r'^(?P<payment_id>[0-9a-f-]+)/auth/$',
                self.admin_site.admin_view(auth_payment_form),
                name='netaxept_payment_auth',
            ),
            url(
                r'^(?P<payment_id>[0-9a-f-]+)/capture/$',
                self.admin_site.admin_view(capture_payment_form),
                name='netaxept_payment_capture',
            ),
            url(
                r'^(?P<payment_id>[0-9a-f-]+)/credit/$',
                self.admin_site.admin_view(credit_payment_form),
                name='netaxept_payment_credit',
            ),
        ]
        return my_urls + urls

    def auth_button(self, obj):
        if obj.success:
            return format_html('<a class="button" href="{}">Auth</a>',
                               reverse('admin:netaxept_payment_auth', args=[obj.pk]))
        else:
            return '-'

    auth_button.short_description = 'Auth'

    def capture_button(self, obj):
        if obj.success:
            return format_html('<a class="button" href="{}">Capture</a>',
                               reverse('admin:netaxept_payment_capture', args=[obj.pk]))
        else:
            return '-'

    capture_button.short_description = 'Capture'

    def credit_button(self, obj):
        if obj.success:
            return format_html('<a class="button" href="{}">Credit</a>',
                               reverse('admin:netaxept_payment_credit', args=[obj.pk]))
        else:
            return '-'

    credit_button.short_description = 'Credit'
