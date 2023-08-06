# -*- coding: utf-8 -*-
"""
    transaction.py

    :copyright: (c) 2015 by Fulfil.IO Inc.
    :license: see LICENSE for more details.
"""
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Bool, Not
from trytond.model import fields
from trytond.exceptions import UserError

import stripe
stripe.api_version = '2017-06-05'

__metaclass__ = PoolMeta
__all__ = [
    'PaymentGatewayStripe', 'PaymentTransactionStripe',
    'AddPaymentProfile'
]


class PaymentGatewayStripe:
    "Stripe Gateway Implementation"
    __name__ = 'payment_gateway.gateway'

    stripe_api_key = fields.Char(
        'Stripe API Key', states={
            'required': Eval('provider') == 'stripe',
            'invisible': Eval('provider') != 'stripe',
            'readonly': Not(Bool(Eval('active'))),
        }, depends=['provider', 'active']
    )

    stripe_publishable_key = fields.Char(
        'Stripe Publishable Key', states={
            'invisible': Eval('provider') != 'stripe',
            'readonly': Not(Bool(Eval('active'))),
        }, depends=['provider', 'active']
    )

    @classmethod
    def get_providers(cls, values=None):
        """
        Downstream modules can add to the list
        """
        rv = super(PaymentGatewayStripe, cls).get_providers()
        stripe_record = ('stripe', 'Stripe')
        if stripe_record not in rv:
            rv.append(stripe_record)
        return rv

    def get_methods(self):
        if self.provider == 'stripe':
            return [
                ('credit_card', 'Credit Card - Stripe'),
            ]
        return super(PaymentGatewayStripe, self).get_methods()

    @classmethod
    def view_attributes(cls):
        return super(PaymentGatewayStripe, cls).view_attributes() + [(
            '//notebook/page[@id="stripe"]', 'states', {
                'invisible': Eval('provider') != 'stripe'
            }
        )]


class PaymentTransactionStripe:
    """
    Payment Transaction implementation for Stripe
    """
    __name__ = 'payment_gateway.transaction'

    @property
    def stripe_amount(self):
        """
        Stripe requires amounts in currencies that support decimals to be
        multiplied by 100 while the other ones sent as such.

        https://stripe.com/docs/currencies#zero-decimal
        """
        if self.currency.code in (
                'BIF', 'XAF', 'XPF', 'CLP',
                'KMF', 'DJF', 'GNF', 'JPY',
                'MGA', 'PYG', 'RWF', 'KRW',
                'VUV', 'VND', 'XOF'):
            return int(self.amount)
        return int(self.amount * 100)

    def authorize_stripe(self, card_info=None):
        """
        Authorize using stripe.
        """
        TransactionLog = Pool().get('payment_gateway.transaction.log')

        stripe.api_key = self.gateway.stripe_api_key

        charge_data = self.get_stripe_charge_data(card_info=card_info)
        charge_data['idempotency_key'] = 'auth_%s' % self.uuid
        charge_data['capture'] = False

        try:
            charge = stripe.Charge.create(**charge_data)
        except (
            stripe.error.CardError, stripe.error.InvalidRequestError,
            stripe.error.AuthenticationError, stripe.error.APIConnectionError,
            stripe.error.StripeError
        ), exc:
            self.state = 'failed'
            self.save()
            TransactionLog.serialize_and_create(self, exc.json_body)
        else:
            if charge.status == 'succeeded':
                self.state = 'authorized'
            else:
                self.state = 'failed'
            self.provider_reference = charge.id
            self.save()
            TransactionLog.create([{
                'transaction': self,
                'log': unicode(charge),
            }])

    def settle_stripe(self):
        """
        Settle an authorized charge
        """
        TransactionLog = Pool().get('payment_gateway.transaction.log')

        assert self.state == 'authorized'

        stripe.api_key = self.gateway.stripe_api_key

        try:
            charge = stripe.Charge.retrieve(self.provider_reference)
            charge = charge.capture(amount=self.stripe_amount)
        except (
            stripe.error.InvalidRequestError,
            stripe.error.AuthenticationError, stripe.error.APIConnectionError,
            stripe.error.StripeError
        ), exc:
            self.state = 'failed'
            self.save()
            TransactionLog.serialize_and_create(self, exc.json_body)
        else:
            if charge.status == 'succeeded':
                self.state = 'completed'
            else:
                self.state = 'failed'
            self.provider_reference = charge.id
            self.save()
            TransactionLog.create([{
                'transaction': self,
                'log': unicode(charge),
            }])
            self.safe_post()

    def capture_stripe(self, card_info=None):
        """
        Capture using stripe.
        """
        TransactionLog = Pool().get('payment_gateway.transaction.log')

        stripe.api_key = self.gateway.stripe_api_key

        charge_data = self.get_stripe_charge_data(card_info=card_info)
        charge_data['idempotency_key'] = 'capture_%s' % self.uuid
        charge_data['capture'] = True

        try:
            charge = stripe.Charge.create(**charge_data)
        except (
            stripe.error.CardError, stripe.error.InvalidRequestError,
            stripe.error.AuthenticationError, stripe.error.APIConnectionError,
            stripe.error.StripeError
        ), exc:
            self.state = 'failed'
            self.save()
            TransactionLog.serialize_and_create(self, exc.json_body)
        else:
            if charge.status == 'succeeded':
                self.state = 'completed'
            else:
                self.state = 'failed'
            self.provider_reference = charge.id
            self.save()
            TransactionLog.create([{
                'transaction': self,
                'log': unicode(charge),
            }])
            self.safe_post()

    def get_stripe_charge_data(self, card_info=None):
        """
        Downstream modules can modify this method to send extra data to
        stripe
        """
        charge_data = {
            'amount': self.stripe_amount,
            'currency': self.currency.code.lower(),
        }

        if card_info:
            charge_data['source'] = {
                'object': 'card',
                'number': card_info.number,
                'exp_month': card_info.expiry_month,
                'exp_year': card_info.expiry_year,
                'cvc': card_info.csc,
                'name': card_info.owner or self.address.name or self.party.name
            }
            charge_data['source'].update(self.address.get_address_for_stripe())

        elif self.payment_profile:
            charge_data.update({
                'customer': self.payment_profile.stripe_customer_id,
                'card': self.payment_profile.provider_reference,
            })

        else:
            self.raise_user_error('no_card_or_profile')

        return charge_data

    def retry_stripe(self, credit_card=None):
        """
        Retry charge

        :param credit_card: An instance of CreditCardView
        """
        raise self.raise_user_error('feature_not_available')

    def update_stripe(self):
        """
        Update the status of the transaction from Stripe
        """
        raise self.raise_user_error('feature_not_available')

    def cancel_stripe(self):
        """
        Cancel this authorization or request
        """
        TransactionLog = Pool().get('payment_gateway.transaction.log')

        if self.state != 'authorized':
            self.raise_user_error('cancel_only_authorized')

        stripe.api_key = self.gateway.stripe_api_key

        try:
            charge = stripe.Charge.retrieve(
                self.provider_reference
            ).refund(idempotency_key=('refund_%s' % self.uuid))
        except (
            stripe.error.InvalidRequestError,
            stripe.error.AuthenticationError, stripe.error.APIConnectionError,
            stripe.error.StripeError
        ), exc:
            TransactionLog.serialize_and_create(self, exc.json_body)
        else:
            self.state = 'cancel'
            self.save()
            TransactionLog.create([{
                'transaction': self,
                'log': unicode(charge),
            }])

    def refund_stripe(self):
        TransactionLog = Pool().get('payment_gateway.transaction.log')

        stripe.api_key = self.gateway.stripe_api_key

        try:
            refund = stripe.Refund.create(
                charge=self.origin.provider_reference,
                amount=self.stripe_amount
            )
        except (
            stripe.error.InvalidRequestError,
            stripe.error.AuthenticationError, stripe.error.APIConnectionError,
            stripe.error.StripeError
        ), exc:
            self.state = 'failed'
            self.save()
            TransactionLog.serialize_and_create(self, exc.json_body)
        else:
            self.provider_reference = refund.id
            self.state = 'completed'
            self.save()
            TransactionLog.create([{
                'transaction': self,
                'log': unicode(refund),
            }])
            self.safe_post()


class AddPaymentProfile:
    """
    Add a payment profile
    """
    __name__ = 'party.party.payment_profile.add'

    def transition_add_stripe(self):
        """
        Handle the case if the profile should be added for Stripe
        """
        card_info = self.card_info

        stripe.api_key = card_info.gateway.stripe_api_key

        profile_data = {
            'source': {
                'object': 'card',
                'number': card_info.number,
                'exp_month': card_info.expiry_month,
                'exp_year': card_info.expiry_year,
                'cvc': card_info.csc,
                'name': (
                    card_info.owner or self.address.name or self.party.name
                ),
            },
        }
        profile_data['source'].update(
            card_info.address.get_address_for_stripe())

        customer_id = card_info.party._get_stripe_customer_id(
            card_info.gateway
        )

        try:
            if customer_id:
                customer = stripe.Customer.retrieve(customer_id)
                card = customer.sources.create(**profile_data)
            else:
                profile_data.update({
                    'description': card_info.party.name,
                    'email': card_info.party.email,
                })
                customer = stripe.Customer.create(**profile_data)
                card = customer.sources.data[0]
        except (
            stripe.error.CardError, stripe.error.InvalidRequestError,
            stripe.error.AuthenticationError, stripe.error.APIConnectionError,
            stripe.error.StripeError
        ), exc:
            raise UserError(exc.json_body['error']['message'])

        return self.create_profile(
            card.id,
            stripe_customer_id=customer.id
        )
