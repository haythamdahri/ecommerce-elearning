import datetime

from Ecommerce.forms import SearchForm, SubscribeEmail
from Ecommerce.models import Category, Brand, Stock, Product, Sale, Cart


# ---------------- Calculating Product Price Depending On Stock Sup Price And Sales ----------------
def calculate_new_prices(products):
    try:
        product_iterator = iter(products)
        for product in products:
            stock = product.stock_set.all()
            if stock.exists():
                product.price += stock.all().order_by('price_sup').first().price_sup
            sale = product.sale_set.filter(date_end__gte=datetime.date.today())
            if sale.exists():
                product.is_sale = True
                product.old_price = product.price
                product.price -= sale.all().order_by('-percentage').first().saved_amount()
    except TypeError as te:
        product = products
        stock = product.stock_set.all()
        if stock.exists():
            product.price += stock.all().order_by('price_sup').first().price_sup
        sale = product.sale_set.filter(date_end__gte=datetime.date.today())
        if sale.exists():
            product.is_sale = True
            product.old_price = product.price
            product.price -= sale.all().order_by('-percentage').first().saved_amount()

def global_vars(request):
    context = dict()
    # --------------- All categories ---------------
    categories = Category.objects.all()
    # --------------- Search form ---------------
    search_form = SearchForm()
    # --------------- Brands ---------------
    brands = Brand.objects.all()
    # --------------- Featured products ---------------
    featured_products_footer_ids = Stock.objects.filter(product__is_featured=True).order_by('-product__number_views').values('product').distinct()[:10]
    featured_products_footer = list()
    for p_id in featured_products_footer_ids:
        featured_products_footer.append(Product.objects.get(id=p_id['product']))
    calculate_new_prices(featured_products_footer)
    # --------------- On sale products ---------------
    sale_products_ids = Sale.objects.filter(product__stock__quantity__gt=0).values('product').distinct().values('product_id')
    sale_products = []
    for p_id in sale_products_ids:
        sale_products.append(Product.objects.get(id=p_id['product_id']))
    calculate_new_prices(sale_products)
    for p in sale_products:
        print(f'PRODUCT {p}')
    # --------------- Top Rated Products ---------------
    stock_rated_products, stock_rated_products_ids = list(), list()
    for stock in Stock.objects.filter(product__is_active=True).order_by('-product__rate').distinct():
        if stock.product.pk not in stock_rated_products_ids :
            stock_rated_products.append(stock)
            stock_rated_products_ids.append(stock.product.pk)
    rated = stock_rated_products if len(stock_rated_products)>0 else Stock.objects.all().order_by('-product__number_views')
    for rate in rated:
        calculate_new_prices(rate.product)
    # --------------- Carts ---------------
    my_cart_result = my_cart(request.user)
    number_products_in_cart = my_cart_result['number_products_in_cart']
    total_price_in_cart = my_cart_result['total_price_in_cart']
    cart_result = my_cart_result['cart']
    # --------------- Subscribe NewsLetter Form ---------------
    subscribe_email = SubscribeEmail()

    context = {
        'categories': categories,
        'search_form': search_form,
        'brands': brands,
        'featured_products_footer': featured_products_footer,
        'rated': rated,
        'sale_products': sorted(sale_products, key=lambda s:s.price, reverse=True),
        'carts': cart_result,
        'total_price_in_cart': total_price_in_cart,
        'number_products_in_cart': number_products_in_cart,
        'subscribe_email': subscribe_email
    }
    return context

def my_cart(user):
    number_products_in_cart = 0
    total_price_in_cart = 0
    cart_result = None
    if user.is_authenticated:
        cart_result = Cart.objects.filter(profile=user.profile)
        for el in cart_result:
            stock = el.product.stock_set.filter(color=el.color)
            if stock.exists():
                el.product.price += stock.all()[0].price_sup
            number_products_in_cart += 1
            sale = el.product.sale_set.filter(date_end__gte=datetime.date.today())
            if sale.exists():
                el.product.price -= sale.all()[0].saved_amount()
            total_price_in_cart += (el.product.price * el.quantity)
    return {'cart': cart_result, 'number_products_in_cart': number_products_in_cart, 'total_price_in_cart': total_price_in_cart}