import decimal
from datetime import timedelta
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from django.db.models import Sum, Min, F, Count, Max, Q
from django.http import JsonResponse, HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.template.loader import render_to_string, get_template
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from Ecommerce.forms import LoginForm, SignUpForm, ContactForm, UserForm, UserPasswordForm, GoPageForm, PriceFilterForm, \
    CheckOutForm, TrackOrderForm, ConfirmEmailForm
from Ecommerce.models import Banner, NewsLetter, Profile, Image, WishList, Compare, Order, OrderLine
from .context_processors import *


# ---------------- HOME ----------------
class home(View):
    def get(self, request):
        context = dict()
        # ----------------SEND REQUEST THROUGH VIEW ----------------
        """
        request_url = "{0}://{1}{2}".format(request.scheme, request.get_host(), reverse('ecommerce:subscribe_email'))
        response = requests.get(request_url, params={'email': 'haytham.dahri@gmail.com'})
        print(response.json())
        """
        # ---------------- Trending Products With Min Price From ----------------
        trending_stock, trending_stock_products_ids = list(), list()
        for stock in list(Stock.objects.filter(product__is_active=True).order_by('-product__number_views')):
            if stock.product.pk not in trending_stock_products_ids:
                stock.product_min_price_from = \
                    Product.objects.filter(id=stock.product_id).annotate(Min('price_from')).values(
                        'price_from').first()[
                        'price_from']
                trending_stock.append(stock)
                trending_stock_products_ids.append(stock.product.pk)
        trending_products_stock = len(trending_stock) > 1 and trending_stock[:10]
        for stock in trending_products_stock:
            calculate_new_prices(stock.product)
        # ---------------- Banners deals ----------------
        top_banners = Banner.objects.filter(is_active=True)[:2]
        # ---------------- Last Products ----------------
        last_products_ids = Stock.objects.filter(product__is_active=True).values('product').distinct().order_by('product__add_date').values('product')
        last_products = list()
        for p_id in last_products_ids:
            last_products.append(Product.objects.get(id=p_id['product']))
        calculate_new_prices(last_products)
        # ---------------- Featured Products (Produits Spéciales) featured=0..10  featured_products=10..20 ----------------
        featured_stock, featured_stock_products_ids = list(), list()
        for stock in Stock.objects.filter(product__is_featured=True, product__is_active=True).order_by(
                '-product__number_views'):
            if stock.product.pk not in featured_stock_products_ids:
                featured_stock.append(stock)
                featured_stock_products_ids.append(stock.product.pk)
        featured = featured_stock[:10] if len(featured_stock) > 0 else trending_stock
        featured_products = list()
        for stock in featured_stock:
            featured_products.append(stock.product)
        if len(featured_products) == 0:
            featured_products = featured - trending_stock if len(trending_stock) > 0 else Product.objects.filter(
                quantity__gt=0).distinct()
        calculate_new_prices(featured_products)
        # ---------------- Deals Of The Week 0..10 => 10..20 ----------------
        deals_of_week = sorted(
            Sale.objects.filter(is_daily=False, product__is_active=True, product__stock__isnull=False,
                                date_end__gt=now()), key=lambda deal: deal.saved_amount())
        deals_of_week.reverse()
        deals_of_week = list(deals_of_week)
        sales_deals_products_ids = list()
        final_deals_of_week = list()
        for deal in deals_of_week:
            if deal.product_id not in sales_deals_products_ids:
                stock = deal.product.stock_set.all()
                if stock.exists():
                    deal.product.price += stock.all().order_by('price_sup').first().price_sup
                deal.quantity = deal.product.stock_set.aggregate(Sum('quantity'))["quantity__sum"]
                deal.first_quantity = deal.product.stock_set.aggregate(Sum('first_quantity'))["first_quantity__sum"]
                deal.percent = (deal.quantity * 100) / deal.first_quantity
                deal.sold = deal.first_quantity - deal.quantity
                deal.consumed_percentage = str(((100 * deal.sold) / deal.first_quantity)).replace(',', '.')
                sales_deals_products_ids.append(deal.product_id)
                final_deals_of_week.append(deal)
        # ---------------- Random Categories ----------------
        bc = dict()
        categories = Category.objects.all()
        for category in categories:
            bc[category] = category.product_set.count()
        best_categories = [l[0] for l in sorted(list(bc.items()), key=lambda x: x[1])]
        best_categories.reverse()
        best_categories = best_categories[:3]
        # ---------------- Top 20 Products ----------------
        stock_best_products_ids = Stock.objects.filter(product__is_active=True).values('product').distinct().annotate(
            sold_percentage=(100 - (Sum(F('quantity')) * 100) / Sum(F('first_quantity')))).order_by(
            '-sold_percentage').values('product')
        best_products = list()
        for p_id in stock_best_products_ids:
            best_products.append(Product.objects.get(id=p_id['product']))
        calculate_new_prices(best_products)
        # ---------------- More Products Category ----------------
        more_products_category = Category.objects.annotate(Sum('product')).values('product__sum', 'id').order_by(
            '-product__sum').first()
        more_products_category['id'] = Category.objects.get(id=more_products_category['id'])
        more_products = more_products_category['id'].product_set.all()
        for product in more_products:
            calculate_new_prices(product)
            print(f'PRICE: {product.price}')

        context = {
            'trending_products_stock': trending_products_stock[:10],
            'last_products': last_products,
            'featured': featured,
            'deals_of_week': final_deals_of_week,
            'featured_products': featured_products,
            'best_categories': best_categories,
            'best_products': best_products[:4],
            'more_products': more_products,
            'more_products_category': more_products_category,
            'banners': top_banners,
        }
        return render(request, 'ecommerce/home.html', context)


def category(request, id):
    context = dict()
    return render(request, 'ecommerce/home.html')

# ---------------- Calculating Product Price Depending On Stock Sup Price And Sales ----------------
def calculate_new_prices(products, color=None):
    try:
        product_iterator = iter(products)
        for product in products:
            stock = product.stock_set.all()
            if stock.exists():
                if color is None:
                    product.price += stock.all().order_by('price_sup').first().price_sup
                else:
                    product.price += stock.filter(color=color).first().price_sup
            sale = product.sale_set.filter(date_end__gte=datetime.date.today())
            if sale.exists():
                product.is_sale = True
                product.old_price = product.price
                product.price -= sale.all().order_by('-percentage').first().saved_amount()
    except TypeError as te:
        product = products
        stock = product.stock_set.all()
        if stock.exists():
            if color is None:
                product.price += stock.all().order_by('price_sup').first().price_sup
            else:
                product.price += stock.filter(color=color).first().price_sup
        sale = product.sale_set.filter(date_end__gte=datetime.date.today())
        if sale.exists():
            product.is_sale = True
            product.old_price = product.price
            product.price -= sale.all().order_by('-percentage').first().saved_amount()


# ---------------- NEWSLETTER SUBSCRIBE ----------------
def subscribe_email(request):
    if request.method == "POST":
        email = request.POST.get('email')
        status = False
        msg = ""
        try:
            if request.user.email == email:
                NewsLetter.objects.create(email=email)
                message = render_to_string('ecommerce/mail/subscription.html', {'email': email})
                send_mail("NewsLetter Subscription", message, "haytham.dahri@ecommerce.ma", [email], fail_silently=False,  html_message=message)
                status = True
                msg = "Vous êtes inscrit au Newsletter, vous allez recevoir des notifications, Merci."
            else:
                msg = "L'adresse email saisie ne correspond pas à votre email!"

            context = {'status': status,
                       'message': msg}
            return JsonResponse(context, safe=False)
        except:
            context = {'status': status, 'message': 'Vous êtes deja inscrit. Merci'}
            return JsonResponse(context, safe=False)
    else:
        context = {'status': False, 'message': 'Une erreur est survenue, veuillez ressayer!'}
        return JsonResponse(context, safe=False)


# ---------------- ACCOUNT ----------------
def account(request):
    context = dict()
    user = request.user
    # ---------------- GET REQUEST ----------------
    if request.method == "GET":
        if user.is_authenticated:
            initial = {
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }
            userForm = UserForm(initial=initial)
            initial = {
                'password': user.password
            }
            userPasswordForm = UserPasswordForm(initial=initial)
            context = {
                'UserForm': userForm,
                'userPasswordForm': userPasswordForm
            }
            return render(request, 'ecommerce/accounts/account.html', context)
        else:
            loginForm, signUpForm = LoginForm(), SignUpForm()
            context = {'LoginForm': loginForm, 'SignUpForm': signUpForm}
            return render(request, 'ecommerce/accounts/sign_in_sign_up.html', context)
    # ---------------- POST REQUEST ----------------
    else:
        if user.is_authenticated:
            # ---------------- FOR INFO EDIT ----------------
            if request.POST.get('is_password_change') == "0":
                old_email = user.email
                us = User.objects.get(id=request.user.id)
                userForm = UserForm(request.POST or None, instance=us)
                if userForm.is_valid():
                    if userForm.cleaned_data['email'] != old_email:
                        if not User.objects.filter(email=userForm.cleaned_data['email']).exists():
                            user = userForm.save(commit=False)
                            user.is_active = False
                            user.save()
                            send_confirmation_signup_mail(request, user, 'Confirmer votre nouvelle adresse email')
                            logout(request)
                        else:
                            messages.error(request, "L'adresse email est déja utilisé.")
                    else:
                        userForm.save()
                        messages.success(request, 'Les informations de votre profil sont modifiées avec succé')

                    return redirect('ecommerce:account')
                else:
                    initial = {
                        'password': user.password
                    }
                    userPasswordForm = UserPasswordForm(initial=initial)
                    context = {
                        'UserForm': userForm,
                        'userPasswordForm': userPasswordForm
                    }
                    messages.error(request, 'Veuillez verifier les informations!')
                    return render(request, 'ecommerce/accounts/account.html', context)
            # ---------------- FOR PASSWORD EDIT ----------------
            else:
                us = User.objects.get(id=request.user.id)
                userPasswordForm = UserPasswordForm(request.POST or None, instance=us)
                if userPasswordForm.is_valid():
                    # ---------------- GET DATA ----------------
                    #  ----------------initialisation
                    password = userPasswordForm.cleaned_data['password']
                    user_password = user.password
                    print(user_password)
                    matchcheck = check_password(password, user_password)
                    if matchcheck:
                        user = userPasswordForm.save(commit=False)
                        user.set_password(userPasswordForm.cleaned_data['new_password'])
                        user.save()
                        messages.success(request, 'Votre mot de passe à été modifié avec succé')
                        login(request, user)
                        return redirect('ecommerce:account')
                    else:
                        messages.error(request, 'Ancien mot de passe invalide!')
                else:
                    messages.error(request, 'Mot de passe invalide!')

                initial = {
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email
                }
                userForm = UserForm(initial=initial)
                context = {
                    'UserForm': userForm,
                    'userPasswordForm': userPasswordForm
                }
                return render(request, 'ecommerce/accounts/account.html', context)
        else:
            signUpForm = SignUpForm(request.POST)
            if signUpForm.is_valid():
                user = signUpForm.save(commit=False)
                password = signUpForm.cleaned_data['password']
                print(password)
                user.set_password(password)
                user.is_active = False
                user.save()
                profile_image = get_object_or_404(Image, name="default_profile_picture")
                print(profile_image)
                Profile.objects.create(user=user, picture=profile_image)
                send_confirmation_signup_mail(request, user)
                messages.success(request, f'Bienvenue {user.profile.full_name()} au sein de note plateforme E-commerce HAYTHAM DAHRI')
                return redirect('ecommerce:login')
            else:
                messages.error(request,  'Les informations saisies sont invalides, veuillez corriger les erreurs puis ressayer!')
                loginForm = LoginForm()
                context = {'LoginForm': loginForm, 'SignUpForm': signUpForm}
                return render(request, 'ecommerce/accounts/sign_in_sign_up.html', context)


def confirm_email_signup(request, id_user, token_email):
    user = get_object_or_404(User, id=id_user)

    if user.is_active:
        messages.warning(request, "Votre email est déjà confirmé.")
        return redirect('ecommerce:login')

    if user.profile.token_email_expiration <= timezone.now():
        messages.warning(request, "Votre lien a expiré. <strong><a href='/ecommerce/confirm_mail/resend'>Renvoyer l'email</a></strong> ")
        return redirect('ecommerce:login')
    else:
        if user.profile.token_email == token_email:
            user.is_active = True
            user.save()
            messages.success(request, "Votre email a été confirmé.")
            return redirect('ecommerce:login')
        else:
            raise Http404("Une erreur s'est produite.")

    return redirect('ecommerce:login')

def send_confirmation_signup_mail(request,  user=None, title='HAYTHAM DAHRI : Finalisez votre inscription'):

    if user is None:
        messages.error(request, 'Une erreur s\'est produite. Peut être que l\'email indiqué n\'est pas enregistrée. Veuillez Réssayer')
    elif user.is_active:
        messages.warning(request, 'Votre compte est déjà activé')

    else:
        generated_token = get_random_string(length=32)
        user.profile.token_email = generated_token
        user.profile.token_email_expiration = timezone.now() + timedelta(days=2)
        user.profile.save()
        message = render_to_string("ecommerce/mail/signup_confirm_email.html",{'user': user,'request':request}, request)

        send_mail(
            title,
            message,
            'haytham.dahri@ecommerce.ma',
            [user.email],
            fail_silently=False,
            html_message=message
        )

        messages.success(request, 'Un e-mail de vérification a été envoyé à l\'adresse ' + user.email + '. Cliquez sur le lien inclu dans l\'e-mail pour activer votre compte.')

def confirm_email_signup(request, id_user, token_email):
    user = get_object_or_404(User, id=id_user)

    if user.is_active:
        messages.warning(request, "Votre email est déjà confirmé.")
        return redirect('ecommerce:login')

    if user.profile.token_email_expiration <= timezone.now():
        messages.warning(request, "Votre lien a expiré. <a href='/main/confirm_mail/resend'>Renvoyer l'email</a>")
        return redirect('ecommerce:login')
    else:
        if user.profile.token_email == token_email:
            user.is_active = True
            user.save()
            messages.success(request, "Votre email a été confirmé.")
            return redirect('ecommerce:login')
        else:
            raise Http404("Une erreur s'est produite.")

    return redirect('ecommerce:login')


def signup_complete(request):
    return render(request, 'ecommerce/accounts/singup_thanks.html')

class ConfirmMailResendView(View):

    def get(self, request):
        confirm_email_form = ConfirmEmailForm()
        context = {
            'confirmForm': confirm_email_form
        }
        return render(request, 'ecommerce/mail/confirm_mail_form.html', context)

    def post(self, request):
        confirm_email_form = ConfirmEmailForm(request.POST or None)
        if confirm_email_form.is_valid():
            try:
                user = User.objects.get(email=confirm_email_form.cleaned_data['email'])
            except:
                user = None
            send_confirmation_signup_mail(request, user)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous puis ressayer!")

        context = {
            'confirmForm': confirm_email_form
        }
        return render(request, 'ecommerce/mail/confirm_mail_form.html', context)

# ---------------- User login controller ----------------
def login_user(request):
    if request.method == "POST":
        loginForm = LoginForm(request.POST)
        if loginForm.is_valid():
            email = loginForm.cleaned_data['email']
            password = loginForm.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('ecommerce:account')
                else:
                    messages.warning(request, "Votre compte n'est pas encore activé, Veuillez l'activer à travers le lien vous a été envoyé via mail. <a href='"+reverse('ecommerce:confirm_mail_resend')+"'>Renvoyer l'email</a>")
                    return redirect('ecommerce:login')
            else:
                messages.error(request, 'Email ou mot de passe incorrect, veuillez ressayer!')
                return redirect('ecommerce:account')
        else:
            messages.error(request, 'Email ou mot de passe incorrect, veuillez ressayer!')
            return redirect('ecommerce:account')
    else:
        return redirect('ecommerce:account')


# ---------------- LOGOUT USER ----------------
def log_out_user(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        return redirect('ecommerce:account')
    else:
        return redirect('ecommerce:account')


# ---------------- Delete product from cart ----------------
@login_required
def delete_cart(request):
    context = dict()
    if request.method == "POST":
        cart_id = request.POST.get('cart_id')
        cart = Cart.objects.get(pk=cart_id)
        if cart.delete() is not None:
            mycart_context = my_cart(request.user)
            context['status'] = True
            context['message'] = cart.product.name + " à été supprimé"
            if float(mycart_context['total_price_in_cart']).is_integer():
                context['total_price_in_cart'] = int(mycart_context['total_price_in_cart'])
            else:
                context['total_price_in_cart'] = Decimal(mycart_context['total_price_in_cart']).normalize()
            context['number_products_in_cart'] = request.user.profile.cart_set.all().count()
        else:
            mycart_context = my_cart(request.user)
            context['status'] = True
            context['message'] = "Une erreur est survenue, veuillez ressayer!"
            if float(mycart_context['total_price_in_cart']).is_integer():
                context['total_price_in_cart'] = int(mycart_context['total_price_in_cart'])
            else:
                context['total_price_in_cart'] = Decimal(mycart_context['total_price_in_cart']).normalize()
            print(f"TOTAL IN CART: {context['total_price_in_cart']}")
        return JsonResponse(context, safe=False)
    else:
        mycart_context = my_cart(request.user)
        context['status'] = True
        context['message'] = "Une erreur est survenue, veuillez ressayer!"
        return JsonResponse(context, safe=False)

# ---------------- Delete product from cart ----------------
@login_required
def delete_product_compare(request):
    product_id = request.GET.get('product', "None")
    message_error = message_success = ""
    is_success = False
    profile = request.user.profile
    product = Product.objects.filter(id=product_id).first()
    compare = product.compare_set.filter(profile=profile).first()
    compare.products.remove(product)

    if product not in compare.products.all():
        is_success = True
        message_success = product.name + " à été supprimé de votre liste de comparaison"
    else:
        is_success = False
        message_error = "Une erreur est survenue, veuillez ressayer!"
    data = {
        'is_success': is_success,
        'message_success': message_success,
        'message_error': message_error,
        'number_products_in_carts': compare.products.all().count()
    }
    return JsonResponse(data, safe=False)


# ---------------- 404 HANDLER ----------------
def handler404(request):
    return render(request, 'ecommerce/404.html')

# ---------------- 500 HANDLER ----------------
def handler500(request):
    return render(request, 'ecommerce/500.html')

# ---------------- Add product to wish list ----------------
def add_wish(request):
    product_id = request.GET.get('product', "None")
    message_error = ""
    number_products_in_wish_list = ""
    if request.user.is_authenticated:
        if product_id != "None":
            user = request.user
            products_wish = Product.objects.filter(pk=product_id)
            if products_wish.exists():
                if not WishList.objects.filter(profile=user.profile, product=products_wish[0]).exists():
                    WishList.objects.create(profile=user.profile, product=products_wish[0])
                    wish_list_result = WishList.objects.filter(profile=user.profile)
                    number_products_in_wish_list = wish_list_result.count()
                else:
                    message_error = "Produit existe déjà dans votre liste des souhaits"
            else:
                message_error = "Produit n'existe pas"
        else:
            message_error = "Erreur"
    else:
        message_error = "Vous devez se connecter!"
    data = {
        'message_error': message_error,
        'number_products_in_wish_list': number_products_in_wish_list
    }
    return JsonResponse(data)

# ---------------- Add product to cart ----------------
@csrf_exempt
def add_cart(request):
    product_id = request.GET.get('product', "None")
    message_error = ""
    stock_id = request.GET.get('stock', "None")
    quantity = request.GET.get('quantity', 1)
    print(f"Quantity: {quantity}")
    price = total_price_in_cart = number_products_in_cart = message_warning = ""
    html_element = ""
    if request.user.is_authenticated:
        if product_id != "None":
            user = request.user
            products_wish = Product.objects.filter(pk=product_id)
            if products_wish.exists():
                if int(quantity) < int(products_wish[0].quantity_min):
                    quantity = products_wish[0].quantity_min
                    message_warning = "Quantité est {}".format(products_wish[0].quantity_min)
                if stock_id == "None" or stock_id == "":
                    stock = Stock.objects.filter(product=products_wish[0])
                else:
                    stock = Stock.objects.filter(product=products_wish[0], id=stock_id, quantity__gte=int(quantity))
                if stock.exists():
                    cart_objects = Cart.objects.filter(profile=user.profile, product=products_wish[0],
                                                       color=stock[0].color)
                    if not cart_objects.exists():
                        cart = Cart.objects.create(profile=user.profile, product=products_wish[0], color=stock[0].color,
                                                   quantity=quantity)
                        context = {'cart': cart}
                        html_element = render_to_string("ecommerce/parts/single_product_cart.html", context, request)
                        cart.save()
                        color_id = stock[0].color.pk
                        cart_result = Cart.objects.filter(profile=user.profile)
                        number_products_in_cart = cart_result.count()
                        total_price_in_cart = 0
                        for el in cart_result:
                            stock = el.product.stock_set.filter(color=el.color)
                            if stock.exists():
                                el.product.price = el.product.price + stock.all()[0].price_sup
                            sale = el.product.sale_set.filter(date_end__gte=datetime.date.today())
                            if sale.exists():
                                el.product.price = el.product.price - (
                                        (el.product.price * sale.all()[0].percentage) / 100)
                            if el.product == products_wish[0]:
                                price = Decimal(el.product.price) * Decimal(quantity)
                            total_price_in_cart += Decimal(el.product.price * el.quantity)
                            if float(total_price_in_cart).is_integer():
                                total_price_in_cart = int(total_price_in_cart)
                            else:
                                total_price_in_cart = total_price_in_cart.normalize()
                            print('hello')
                    else:
                        message_error = "Produit existe déja dans votre panier"
                else:
                    message_error = "Produit en rupture stock"
            else:
                message_error = "Produit n'existe pas"
    else:
        message_error = "Vous devez se connecter!"

    data = {
        'message_error': message_error,
        'message_warning': message_warning,
        'total_price_in_cart': total_price_in_cart,
        'number_products_in_cart': number_products_in_cart,
        'price': price,
        'stock_id': stock_id,
        'quantity': quantity,
        'html_element': html_element,
    }
    return JsonResponse(data)

# ---------------- Load carts ----------------
def load_carts(request):
    user = request.user
    has_more_carts = False
    nb_elements_more = 0
    cart_list = Cart.objects.filter(profile=user.profile).order_by('id')
    html_elements = render_to_string("ecommerce/parts/cart_products.html", {'cart': cart_list}, request)
    if cart_list.count() - 3 > 0:
        nb_elements_more = cart_list.count() - 3
        has_more_carts = True
    return JsonResponse(
        {'has_more_carts': has_more_carts, 'nb_elements_more': nb_elements_more, 'nb_elements_in_cart': cart_list.count(), 'html_elements': html_elements})

# ---------------- Add product to compare list----------------
def add_compare(request):
    product_id = request.GET.get('product', "None")
    message_error = message_success = ""
    is_success = False
    number_products_in_compare = ""
    print('1')
    if request.user.is_authenticated:
        print('2')
        if product_id != "None":
            print('3')
            user = request.user
            products_compare = Product.objects.filter(pk=product_id)
            my_compares = Compare.objects.filter(profile=user.profile).values()
            if products_compare.exists():
                print('4')
                if not my_compares.exists():
                    print('5')
                    my_compare = Compare.objects.create(profile=user.profile)
                    my_compare.products.add(products_compare[0])
                    my_compare.save()
                    compare_result = Compare.objects.filter(profile=user.profile)
                    number_products_in_compare = compare_result.count()
                    message_success = f"{products_compare[0].name} à été ajouté dans votre liste de comparaison"
                    is_success = True
                else:
                    print('6')
                    comp = my_compares[0]
                    compare = Compare.objects.get(id=comp.get('id'))
                    my_compares_products = compare.products.all()
                    p = [True for p in my_compares_products if p.id == products_compare[0].id]
                    if len(p) == 0:
                        compare.products.add(products_compare[0])
                        compare.save()
                        compare_result = Compare.objects.get(profile=user.profile)
                        number_products_in_compare = compare_result.products.all().count()
                        message_success = f"{products_compare[0].name} à été ajouté dans votre liste de comparaison"
                        is_success = True
                    else:
                        message_error = "Produit existe déjà dans votre liste de comparaison"
            else:
                message_error = "Produit n'existe pas"
        else:
            message_error = "Erreur"
    else:
        message_error = "Vous devez se connecter!"
    data = {
        'message_error': message_error,
        'message_success': message_success,
        'number_products_in_compare': number_products_in_compare,
        'is_success': is_success
    }
    return JsonResponse(data, safe=False)

# ---------------- Contact Us ----------------
def contact_us(request):
    context = dict()
    if request.method == "POST":
        contact_form = ContactForm(data=request.POST or None)
        if contact_form.is_valid():
            contact_form.save()
            email = contact_form.cleaned_data['email']
            full_name = f"{contact_form.cleaned_data['first_name']} {contact_form.cleaned_data['last_name']}"
            messages.success(request, f"Merci {full_name} pour votre message, on va vous contacter sur {email}")
            return redirect('ecommerce:contact_us')

    contact_form = ContactForm()
    context = {
        'contact_from': contact_form
    }
    return render(request, 'ecommerce/contact.html', context)


# ---------------- Products ----------------
def products(request, category_id=None, brand_id=None):
    # ---------------- All Products ----------------
    products = Product.objects.filter(id__lte=-1)
    category = Category.objects.filter(id=category_id)
    brand = Brand.objects.filter(id=brand_id)
    sort_type = request.GET.get('sort_type', None)
    category_error = brand_error = False
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)
    search = request.GET.get('search', None)
    category_of_search_id = request.GET.get('category', None)
    category_from_search = False
    gopageform = GoPageForm()
    pricefilterform = PriceFilterForm()

    # ---------------- No Category ----------------
    if category_id == None:
        #---------------- No brand ----------------
        if brand_id == None:
            if sort_type == 'popularity':
                products = Product.objects.filter(is_active=True).annotate(
                    sold=F('stock__first_quantity') - F('stock__quantity')).distinct().order_by('-sold')
                distinced_products = list()
                for p in products:
                    print(distinced_products)
                    if p not in distinced_products:
                        distinced_products.append(p)
                products = distinced_products
            elif sort_type == 'rating':
                products = Product.objects.filter(is_active=True).distinct().order_by('-rate')
            elif sort_type == 'date':
                products = Product.objects.filter(is_active=True).distinct().order_by('-add_date')
            else:
                products = Product.objects.filter(is_active=True).distinct()
            brand = None
        #---------------- Brand selected ----------------
        else:
            if brand.exists():
                brand = brand[0]
                if sort_type == 'popularity':
                    products = Product.objects.filter(is_active=True, brand=brand).annotate(
                        sold=F('stock__first_quantity') - F('stock__quantity')).distinct().order_by('-sold')
                    distinced_products = list()
                    for p in products:
                        print(distinced_products)
                        if p not in distinced_products:
                            distinced_products.append(p)
                    products = distinced_products
                elif sort_type == 'rating':
                    products = Product.objects.filter(is_active=True, brand=brand).distinct().order_by('-rate')
                elif sort_type == 'date':
                    products = Product.objects.filter(is_active=True, brand=brand).distinct().order_by('-add_date')
                else:
                    products = Product.objects.filter(is_active=True, brand=brand).distinct()
            else:
                brand_error = True
                brand = None
        category = None
    # ---------------- Category selected ----------------
    else:
        if category.exists():
            #---------------- No brand ----------------
            if brand_id == None:
                category = category[0]
                if sort_type == 'popularity':
                    products = category.product_set.filter(is_active=True).annotate(
                        sold=F('stock__first_quantity') - F('stock__quantity')).distinct().order_by('-sold')
                    distinced_products = list()
                    for p in products:
                        print(distinced_products)
                        if p not in distinced_products:
                            distinced_products.append(p)
                    products = distinced_products
                elif sort_type == 'rating':
                    products = category.product_set.filter(is_active=True).distinct().order_by('-rate')
                elif sort_type == 'date':
                    products = category.product_set.filter(is_active=True).distinct().order_by(
                        '-add_date')
                else:
                    products = category.product_set.filter(is_active=True).distinct()
                brand = None
            else:
                if brand.exists():
                    category = category[0]
                    brand = brand[0]
                    if sort_type == 'popularity':
                        products = category.product_set.filter(is_active=True, brand=brand).annotate(
                            sold=F('stock__first_quantity') - F('stock__quantity')).distinct().order_by('-sold')
                        distinced_products = list()
                        for p in products:
                            print(distinced_products)
                            if p not in distinced_products:
                                distinced_products.append(p)
                        products = distinced_products
                    elif sort_type == 'rating':
                        products = category.product_set.filter(is_active=True, brand=brand).distinct().order_by('-rate')
                    elif sort_type == 'date':
                        products = category.product_set.filter(is_active=True, brand=brand).distinct().order_by(
                            '-add_date')
                    else:
                        products = category.product_set.filter(is_active=True, brand=brand).distinct()
                else:
                    brand_error = True
                    brand = None
        else:
            category_error = True
            category = None

    # ---------------- Calculating Quantity Sum in Store ----------------
    for p in products:
        p.quantity_in_stock = p.stock_set.aggregate(quantity=Sum('quantity'))["quantity"]
    # ---------------- Price Sorting ----------------
    if sort_type == 'price-desc':
        products = products.order_by('price')
    elif sort_type == 'price':
        products = products.order_by('-price')
    # ---------------- Calculating Product Price Depending On Stock Sup Price And Sales ----------------
    calculate_new_prices(products)
    """
    for product in products:
        stock = product.stock_set.all()
        if stock.exists():
            product.price += stock.all().order_by('price_sup').first().price_sup
        sale = product.sale_set.filter(date_end__gte=datetime.date.today())
        if sale.exists():
            product.is_sale = True
            product.old_price = product.price
            product.price -= sale.all().order_by('-percentage').first().saved_amount()"""
    # ---------------- Search Filtering ----------------
    if search is not None and search != "":
        print("SEARCH IS NOT NONE")
        products = products.filter(name__contains=search)
        if category_of_search_id is not None and category_of_search_id != "all" and category_of_search_id != "":
            category = Category.objects.filter(id=category_of_search_id)
            if category.exists():
                category_from_search = True
                category = category[0]
                products = [p for p in products if p.categories.filter(id=category.id).exists()]
            else:
                category = None
                category_error = True
    else:
        search = None
        if category_of_search_id is not None and category_of_search_id != "all" and category_of_search_id != "all" and max_price is None and min_price is None:
            return redirect("ecommerce:category_products", category_id=category_of_search_id)
    # ---------------- Price Filtering ----------------
    if min_price is not None or max_price is not None:
        try:
            if min_price is None or min_price == "":
                min_price = 0
            if max_price is None or max_price == "":
                max_price = products.values('price').aggregate(Max('price'))['price__max']
            min_price = Decimal(min_price)
            max_price = Decimal(max_price)
            products = [p for p in products if p.price >= min_price and p.price <= max_price]
        except Exception as ex:
            print(ex)
            min_price = None
            max_price = None
            messages.error(request, 'Le prix minimum et maximum sont incorrects.')
    # ---------------- Number of products ----------------
    number_elements = len(products)
    # ---------------- Pagination ----------------
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 2)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    # ---------------- Last Products ----------------
    latest_products_ids = Stock.objects.filter(product__is_active=True).values('product').distinct().order_by(
        'product__add_date').values('product')
    latest_products = list()
    for p_id in latest_products_ids:
        latest_products.append(Product.objects.get(id=p_id['product']))
    # ---------------- Brands ----------------
    brands = Brand.objects.all()
    # ---------------- Inject Context ----------------
    context = {
        'products': products,
        'brands': brands,
        'latest_products': latest_products,
        'number_elements': number_elements,
        'brand': brand,
        'category': category,
        'sort_type': sort_type,
        'GoPageForm': gopageform,
        'PriceFilterForm': PriceFilterForm,
        'category_error': category_error,
        'brand_error': brand_error,
        'min_price': min_price,
        'max_price': max_price,
        'search': search,
        'category_from_search': category_from_search
    }
    return render(request, 'ecommerce/products.html', context)

# ---------------- Product ----------------
def product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.number_views += 1
        product.save()
        calculate_new_prices(product)
        related_products = Product.objects.filter(categories__in=product.categories.all()).exclude(id=product.id)
        print(len(related_products))
        calculate_new_prices(related_products)
        product.quantity_in_stock = product.stock_set.aggregate(quantity=Sum('quantity'))["quantity"]
        context = {
            'product': product,
            'related_products': related_products
        }
        return render(request, 'ecommerce/product.html', context)
    except Product.DoesNotExist:
        messages.error(request, "Le produit demandé n'éxiste pas!")
        return redirect('ecommerce:home')

# ---------------- Compare List ----------------
@login_required
def compare_list(request):
    context = dict()
    # ---------------- Wish list products ----------------
    profile = request.user.profile
    compares_products = Compare.objects.filter(profile=profile).values('products')
    compare_list_products = list()
    if compares_products.exists():
        for id in compares_products:
            if id['products'] is not None:
                compare_list_products.append(Product.objects.filter(id=id['products']).first())
    # ---------------- Calculating Product Price Depending On Stock Sup Price And Sales ----------------
    for product in compare_list_products:
        stock = product.stock_set.all()
        if stock.exists():
            product.price += stock.all().order_by('price_sup').first().price_sup
        sale = product.sale_set.filter(date_end__gte=datetime.date.today())
        if sale.exists():
            product.is_sale = True
            product.old_price = product.price
            product.price -= sale.all().order_by('-percentage').first().saved_amount()
    # ---------------- Calculating Quantity Sum in Store ----------------
    for product in compare_list_products:
        product.quantity_in_stock = product.stock_set.aggregate(quantity=Sum('quantity'))["quantity"]
    # ---------------- Cart products ----------------
    products_ids = profile.cart_set.all().values('product')
    cart_products = list()
    for id in products_ids:
        cart_products.append(Product.objects.filter(id=id['product']).first())
    # ---------------- Pagination ----------------
    page = request.GET.get('page', 1)
    paginator = Paginator(compare_list_products, 3)
    try:
        compare_list_products = paginator.page(page)
    except PageNotAnInteger:
        compare_list_products = paginator.page(1)
    except EmptyPage:
        compare_list_products = paginator.page(paginator.num_pages)

    context = {
        'compare_list_products': compare_list_products,
        'cart_products': cart_products
    }
    print(compare_list_products.object_list)
    return render(request, 'ecommerce/compare.html', context)

# ---------------- Wish List ----------------

class WishListView(LoginRequiredMixin, View):

    def get(self, request):
        wish_list = request.user.profile.wishlist_set.all()
        for wish in wish_list:
            calculate_new_prices(wish.product)
            wish.product.quantity_in_stock = wish.product.stock_set.aggregate(quantity=Sum('quantity'))["quantity"]
        # ---------------- Pagination ----------------
        page = request.GET.get('page', 1)
        paginator = Paginator(wish_list, 3)
        try:
            wish_list = paginator.page(page)
        except PageNotAnInteger:
            wish_list = paginator.page(1)
        except EmptyPage:
            wish_list = paginator.page(paginator.num_pages)
        context = {
            'wish_list': wish_list
        }
        return render(request, 'ecommerce/wishlist.html', context)

# ---------------- Delete Wish List ----------------

class RemoveWishListView(LoginRequiredMixin, View):
    def post(self, request):
        wishlist_id = request.POST.get('wish_list', "None")
        message_error = message_success = ""
        is_success = False
        profile = request.user.profile
        wishlist = WishList.objects.filter(id=wishlist_id).first()
        profile_wishs = WishList.objects.filter(profile=profile)
        if wishlist is not None and wishlist.delete():
            is_success = True
            message_success = wishlist.product.name + " à été supprimé de votre liste des souhaits"
        else:
            is_success = False
            message_error = "Une erreur est survenue, veuillez ressayer!"
        data = {
            'is_success': is_success,
            'message_success': message_success,
            'message_error': message_error,
            'number_wishs': profile_wishs.count()
        }
        return JsonResponse(data, safe=False)

# ---------------- User Cart ----------------
@login_required
def UserCarts(request):
    carts = request.user.profile.cart_set.all()
    for cart in carts:
        calculate_new_prices(cart.product, cart.color)
        cart.max_quantity = cart.color.stock_set.filter(product=cart.product).first().quantity
        print(f"AFTER: {cart.product}")
    total_price_in_cart = sum([cart.total() for cart in carts])
    return(carts, total_price_in_cart)

# ---------------- User Cart ----------------
class CartView(View):
    def get(self, request):
        carts, total_price_in_cart = UserCarts(request)
        number_products_in_cart = carts.count()
        # ---------------- Pagination ----------------
        page = request.GET.get('page', 1)
        paginator = Paginator(carts, 3)
        try:
            carts = paginator.page(page)
        except PageNotAnInteger:
            carts = paginator.page(1)
        except EmptyPage:
            carts = paginator.page(paginator.num_pages)
        context = {
            'my_carts': carts,
            'total_price_in_cart': total_price_in_cart,
            'number_products_in_cart': number_products_in_cart
        }
        return render(request, 'ecommerce/cart.html', context)

# ---------------- Update User Cart ----------------
class UpdateCartView(LoginRequiredMixin, View):
    def post(self, request):
        is_success = True
        message_error = ""
        total_price_in_cart = single_cart_price = float
        cart_id = request.POST.get('cart')
        new_quantity = request.POST.get('quantity')
        try:
            cart = Cart.objects.get(id=cart_id, profile=request.user.profile)
            stock = cart.color.stock_set.get(product=cart.product)
            if( stock.quantity >= int(new_quantity) ):
                cart.quantity = int(new_quantity)
                cart.save()
                total_price_in_cart = UserCarts(request)[1]
                if float(total_price_in_cart).is_integer():
                    total_price_in_cart = int(total_price_in_cart)
                else:
                    total_price_in_cart = Decimal(total_price_in_cart).normalize()
                calculate_new_prices(cart.product, cart.color)
                single_cart_price = Decimal(cart.product.price * cart.quantity)
                if float(single_cart_price).is_integer():
                    single_cart_price = int(single_cart_price)
                else:
                    single_cart_price = Decimal(single_cart_price).normalize()
            else:
                is_success = False
                message_error = "La quantité saisie n'est pas disponible dans le stock"
        except Cart.DoesNotExist:
            is_success = False
            message_error = "Ce produit n'existe plus dans votre panier"
        except Stock.DoesNotExist:
            is_success = False
            message_error = "Ce produit n'éxiste pas dans le stock"
        data = {
            'is_success': is_success,
            'message_error': message_error,
            'total_price_in_cart': total_price_in_cart,
            'new_quantity': new_quantity,
            'single_cart_price': single_cart_price
        }
        return JsonResponse(data, safe=False)


# ---------------- Update User Cart ----------------
class CheckOutView(LoginRequiredMixin, View):
    def get(self, request):
        cart_dict = UserCarts(request)
        carts, total_price_in_cart = cart_dict[0], cart_dict[1]
        if request.user.profile.cart_set.all().count() == 0:
            messages.error(request, "Aucun produit n'a été ajouté dans votre panier")
            return redirect('ecommerce:cart')
        elif total_price_in_cart > settings.MAX_AMOUNT:
            messages.error(request, "Votre panier contient un montant qui dépasse le montant maximal de "+str(settings.MAX_AMOUNT)+" Dhs.")
            return redirect('ecommerce:cart')
        elif total_price_in_cart < settings.MIN_AMOUNT:
            messages.error(request, "Votre panier contient un montant inférieure au montant minimal "+str(settings.MIN_AMOUNT)+" Dhs.")
            return redirect('ecommerce:cart')
        user = request.user
        order_id = request.session.get('order_id', None)
        order = Order.objects.filter(id=order_id)
        if order_id is None or not order.exists():
            order = Order.objects.create(amount=total_price_in_cart, profile=user.profile, comment="COMMENTAIRE DE CREATION D'ORDRE")
            order.track_number = order.pk
            order.save()
        else:
            order = order.first()
            order.amount = total_price_in_cart
            order.save()

        request.session['order_id'] = order.id

        unavailable_products = list()
        for cart in carts:
            orderLine = OrderLine.objects.filter(product=cart.product, color=cart.color, order=order, quantity=cart.quantity)
            if not orderLine.exists():
                orderLine = OrderLine.objects.create(quantity=cart.quantity, total=cart.total(), order=order, product=cart.product, color=cart.color)
                orderLine.save()
        mail_context = {
            'title': 'INFORAMTIONS COMMANDE',
            'subject': 'Initialisation du paiement',
            'description': "<p>Bonjour,</p><p>Votre Commande a été confirmée avec succés.</p><p>Commande numéro <b>#{}</b>.</p><p>Montant : <b>{} Dh</b></p>".format(order.pk, order.amount)
        }
        message = render_to_string('ecommerce/mail/payment_email.html', mail_context)
        send_mail(
            'ECOMMERCE NOTIFICATION : INFORAMTIONS COMMANDE #{}'.format(order.pk),
            message,
            "haytham.dahri@ecommerce.ma",
            [order.profile.user.email],
            fail_silently=False,
            html_message=message,
        )

        checkout_form_initial = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        }
        Checkout_form = CheckOutForm(initial=checkout_form_initial)
        context = {'Checkout_form':Checkout_form, 'carts': carts, 'total_price_in_cart': total_price_in_cart}
        return render(request, 'ecommerce/checkout.html', context)
    def post(self, request):
        return redirect('ecommerce:checkout')

# ---------------- Initiate Payment process ----------------
class ProcessPayment(View):
    def get(self, request):
        messages.warning(request, "Veuillez finaliser votre commande!")
        return redirect('ecommerce:checkout')
    def post(self, request):
        context = dict()
        payment_method = 1
        cart_dict = UserCarts(request)
        carts, total_price_in_cart = cart_dict[0], cart_dict[1]
        user = request.user
        order_id = request.session.get('order_id', None)
        order = Order.objects.filter(id=order_id)
        if order_id is None or not order.exists():
            return redirect('ecommerce:checkout')
        order = order.first()
        checkout_form = CheckOutForm(request.POST)
        if not checkout_form.is_valid():
            messages.error(request, "Veuillez remplir tous les champs correctement!")
            return redirect('ecommerce:checkout')

        #------------ Update order informations ------------
        order.address = checkout_form.cleaned_data['address']
        order.zipcode = checkout_form.cleaned_data['zipcode']
        order.company = checkout_form.cleaned_data['company_name']
        order.city = checkout_form.cleaned_data['city']
        order.country = 'MA'
        order.state = checkout_form.cleaned_data['state']
        payment_method = checkout_form.cleaned_data['payment_method']
        if payment_method == '2':
            paypal_dict = {
                "business": settings.PAYPAL_RECEIVER_EMAIL,
                "amount": str(total_price_in_cart/10),
                "item_name": str("Panier de "+user.email),
                "invoice": order.pk,
                "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
                "return": request.build_absolute_uri(reverse('ecommerce:payment_done')),
                "cancel_return": request.build_absolute_uri(reverse('ecommerce:payment_cancelled')),
                "address1": checkout_form.cleaned_data['address'],
                "city": checkout_form.cleaned_data['city'],
                "email": checkout_form.cleaned_data['email'],
                "first_name": checkout_form.cleaned_data['first_name'],
                "last_name": checkout_form.cleaned_data['last_name'],
                "lc": "fr-MA",
                "num_cart_items": carts.count(),
                "zip": checkout_form.cleaned_data['zipcode'],
                "cbt": "Retourner vers mon compte",
                "custom": "premium_plan",  # Custom command to correlate to some function later (optional),
                "style": {
                 "size": "large",
                 "color": "gold",
                 "shape": "pill",
                 "label": "Payer",
                 "tagline": "true",
                 "fundingicons": "true"
                }
            }
            print("WITH PAYPAL")
            order.payment_method = 'Paypal'
            # Create the instance.
            form = PayPalPaymentsForm(initial=paypal_dict)
            context = {"form": form, 'Checkout_form': checkout_form, 'total_price_in_cart': total_price_in_cart, 'carts': carts, 'order': order}
        else:
            order.payment_method = 'Cash On Delivery'
            context = {'Checkout_form': checkout_form, 'total_price_in_cart': total_price_in_cart, 'carts': carts, 'order': order, 'payment_method': payment_method}
        order.save()
        return render(request, 'ecommerce/process_payment.html', context)

# ---------------- Password reset ----------------
def password_reset(request, is_admin_site=False, template_name='ecommerce/registration/password_reset_form.html',
                   email_template_name='ecommerce/registration/password_reset_email.html',
                   subject_template_name='ecommerce/registration/password_reset_subject.txt',
                   password_reset_form=PasswordResetForm, token_generator=default_token_generator,
                   post_reset_redirect=None, from_email=None, current_app=None, extra_context=None,
                   html_email_template_name='ecommerce/registration/password_reset_email.html'):
    if post_reset_redirect is None:
        post_reset_redirect = reverse('ecommerce:password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
                'html_email_template_name': html_email_template_name,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form_reset_password': form,
        'title': ('Password reset'),
    }
    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app

    return TemplateResponse(request, template_name, context)

# ---------------- Payment done view ----------------
class PasswordResetDoneView(View):

    def get(self, request):
        return render(request, 'ecommerce/registration/password_reset_done.html')
    def post(self, request):
        return redirect('ecommerce:password_reset_done')
# ---------------- Payment done view ----------------
class PaymentDone(LoginRequiredMixin, View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(PaymentDone, self).dispatch(*args, **kwargs)

    def get(self, request):
        del request.session['order_id']
        return render(request, 'ecommerce/paypal/payment_done.html')
    def post(self, request):
        del request.session['order_id']
        return render(request, 'ecommerce/paypal/payment_done.html')

# ---------------- payment cancelled view ----------------
class PaymentCancelled(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'ecommerce/paypal/payment_cancelled.html')
    def post(self, request):
        return render(request, 'ecommerce/paypal/payment_cancelled.html')

class TrackOrder(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        form = TrackOrderForm()
        orders = user.profile.order_set.all()

        # ---------------- Pagination ----------------
        page = request.GET.get('page', 1)
        paginator = Paginator(orders, 10)
        try:
            orders = paginator.page(page)
        except PageNotAnInteger:
            orders = paginator.page(1)
        except EmptyPage:
            orders = paginator.page(paginator.num_pages)

        context = {
            'form': form,
            'orders': orders
        }
        return render(request, 'ecommerce/track-your-order.html', context)
    def post(self, request):
        context = dict()
        form = TrackOrderForm(request.POST or None)
        if form.is_valid():
            orders = Order.objects.filter(pk=form.cleaned_data['order_id'], profile__user__email=form.cleaned_data['order_email'])
            if orders.exists():
                context = {
                    'form': form,
                    'orders': orders
                }
                return render(request, 'ecommerce/track-your-order.html', context)
            else:
                messages.error(request, "La commande recherché n'est pas trouvée! Veullez verifier les informations saisies")
                context = {
                    'form': form
                }
                return render(request, 'ecommerce/track-your-order.html', context)

        messages.error(request, "Veuillez remplir les champs correctement puis ressayer!")
        context = {
            'form': form
        }
        return render(request, 'ecommerce/track-your-order.html', context)
        return redirect('ecommerce:track_your_order')

class CheckOutsView(LoginRequiredMixin, View):
    def get(self, request):
        pass



    def post(self, request):
        return redirect('ecommerce:checkouts')

class CashCheckout(LoginRequiredMixin, View):
    def get(self, request):
        return redirect('ecommerce:checkout')

    def post(self, request):
        user = request.user
        payment_method = request.POST.get('payment_method', None)
        order_id = request.POST.get('order', None)
        order = Order.objects.filter(id=order_id)
        if payment_method == "1" and order.exists():
            order = order.first()
            order.payment_method = "Cash On Delivery"
            order.status = "Shipped"
            order.date_complete = datetime.date.today()
            for order_line in order.orderline_set.all():
                try:
                    stock = Stock.objects.get(product=order_line.product, color=order_line.color)
                    stock.quantity -= order_line.quantity
                    stock.save()
                except Stock.DoesNotExist:
                    messages.error(request, "Une erreur est survenue, veuillez ressayer!")
                    return redirect('ecommerce:checkout')
            order.save()
            del request.session['order_id']
            Cart.objects.filter(profile=user.profile).delete()
            message = "<p>Salut,</p><p>Votre Commande <b>#{}</b> :</p>" \
                      "<p>Montant : <b>{}</b></p>" \
                      "<p>Date : <b>{}</b></p>" \
                      "<p>Méthode de Paiement : <b>{}</b></p>" \
                      "<p>Méthode de Livraison : <b>{}</b></p>" \
                      "<p>a été expédiée, votre Track Number : <b>{}</b>.</p><p>Merci.</p>".format(order.pk,order.amount, order.date, order.payment_method, order.delivery_method, order.id)
            mail_context = {
                'title': 'INFORMATIONS COMMANDE',
                'subject': 'Commande effectuée',
                'description': message
            }
            message = render_to_string('ecommerce/mail/payment_email.html', mail_context)
            send_mail(
                    'ECOMMERCE NOTIFICATION : INFORAMTIONS COMMANDE #{}'.format(order.pk),
                    message,
                    "haytham.dahri@ecommerce.ma",
                    [order.profile.user.email],
                    fail_silently=False,
                    html_message=message,
                    )
            messages.success(request, "Votre commande à été effectuée et elle sera livrée dans le plutôt possible. Merci")
            return redirect('ecommerce:track_your_order')
        else:
            return redirect('ecommerce:checkout')
