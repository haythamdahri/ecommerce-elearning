import datetime
from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED

from Ecommerce.models import *


def show_me_the_money(sender, **kwargs):
    ipn = sender
    print('notify')
    print('payment_status : {}'.format(ipn.txn_id))
    print('payment_status : {}'.format(ipn.payment_status))
    print('Receiver_email : {}'.format(ipn.receiver_email))
    print('custom : {}'.format(ipn.custom))
    print('mc gross : {}'.format(ipn.mc_gross))
    print('invoice : {}'.format(ipn.invoice))
    print('Mc Shipping : {}'.format(ipn.mc_shipping))
    print('Num Cart Items : {}'.format(ipn.num_cart_items))
    print('Payer Status : {}'.format(ipn.payer_status))
    print('Payment Date : {}'.format(ipn.payment_date))
    print('Pending Reason : {}'.format(ipn.pending_reason))
    print('Payment Type : {}'.format(ipn.payment_type))
    print('Address : {}'.format(ipn.address_city))
    print('Address validity : {}'.format(ipn.address_status))
    print('Address zip: {}'.format(ipn.address_zip))
    print('Frist name: {}'.format(ipn.first_name))
    print('Last name: {}'.format(ipn.last_name))
    print('Payer email: {}'.format(ipn.payer_email))
    order = Order.objects.get(pk=ipn.invoice)
    if ipn.payment_status == ST_PP_COMPLETED:
        if ipn.receiver_email == settings.PAYPAL_RECEIVER_EMAIL:
            if Decimal(ipn.mc_gross) == Decimal(order.amount / 10):
                if ipn.mc_currency == 'USD':
                    order_line = OrderLine.objects.filter(order=order)
                    for el in order_line:
                        stock_results = Stock.objects.filter(product=el.product, color=el.color)
                        if stock_results.exists():
                            stock = stock_results[0]
                            stock.quantity = stock.quantity - el.quantity
                            stock.save()
                    Cart.objects.filter(profile=order.profile).delete()
                    order.status = "Processing"
                    order.payment_method = "Paypal"
                    order.date_payment = datetime.date.today()
                    order.save()
                    message = "<p>Bonjour,</p><p>Votre Commande <b>#{}</b> :</p>" \
                              "<p>Montant : <b>{}</b></p>" \
                              "<p>Date : <b>{}</b></p>" \
                              "<p>Date de Paiement : <b>{}</b></p>" \
                              "<p>Méthode de Paiement : <b>Paypal</b></p>" \
                              "<p>Méthode de Livraison : <b>{}</b></p>" \
                              "<p>a été correctement payé, et elle sera traitée très prochainement." \
                              "<p>Merci.</p>".format(order.pk, order.amount, order.date, order.date_payment,
                                                     order.delivery_method)
                else:
                    order.status = ipn.payment_status
                    order.payment_method = "Paypal"
                    order.date_payment = datetime.date.today()
                    order.save()
                    message = "<p>Bonjour,</p><p>Votre paiement pour la Commande <b>#{}</b> :</p>" \
                              "<p>a été refusé car vous avais utilisé le devis <b>{}</b> au lieu de MAD" \
                              "<p>Merci.</p>".format(order.pk, ipn.mc_currency)
            else:
                order.status = ipn.payment_status
                order.payment_method = "Paypal"
                order.date_payment = datetime.date.today()
                order.save()
                message = "<p>Bonjour,</p><p>Votre paiement pour la Commande <b>#{}</b> :</p>" \
                          "<p>a été refusé car vous n'avais pas payé toute la somme <b>{}</b> Dh." \
                          "<p>Merci.</p>".format(order.pk, order.amount)
        else:
            order.status = ipn.payment_status
            order.payment_method = "Paypal"
            order.date_payment = datetime.date.today()
            order.save()
            message = "<p>Bonjour,</p><p>Votre paiement pour la Commande <b>#{}</b> :</p>" \
                      "<p>a été refusé car vous n'avais pas payé le vrai compte." \
                      "<p>Merci.</p>".format(order.pk, order.amount)
    elif ipn.payment_status == "Pending":
        order.status = ipn.payment_status
        order.payment_method = "Paypal"
        order.date_payment = datetime.date.today()
        order.save()
        message = "<p>Bonjour,</p><p>Votre paiement pour la Commande <b>#{}</b> :</p>" \
                  "<p>Votre Transaction est en cours de vérification par Paypal, raison : <b>{}</b>." \
                  "<p>Merci.</p>".format(order.pk, ipn.pending_reason)
    else:
        order.status = ipn.payment_status
        order.payment_method = "Paypal"
        order.date_payment = datetime.date.today()
        order.save()
        message = "<p>Bonjour,</p><p>Votre paiement pour la Commande <b>#{}</b> a été refusé</p>".format(order.pk)

    mail_context = {
        'title': 'INFORMATIONS COMMANDE',
        'subject': 'Paiement procedé',
        'description': message
    }
    message = render_to_string('ecommerce/mail/payment_email.html', mail_context)
    send_mail(
        'NCR-TECH NOTIFICATION : INFORAMTIONS COMMANDE #{}'.format(order.pk),
        message,
        settings.EMAIL_HOST_USER,
        [order.profile.user.email],
        fail_silently=False,
        html_message=message,
    )

valid_ipn_received.connect(show_me_the_money)
invalid_ipn_received.connect(show_me_the_money)