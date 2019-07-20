import os
import time
import uuid

from ckeditor.fields import RichTextField
from colorful.fields import RGBColorField
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
# Create your models here.
from django.utils.deconstruct import deconstructible
from django.utils.timezone import now


@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        # eg: filename = 'my uploaded file.jpg'
        ext = filename.split('.')[-1]  # eg: 'jpg'
        uid = uuid.uuid4().hex[:10]  # eg: '567ae32f97'

        # eg: 'my-uploaded-file'
        new_name = '-'.join(filename.replace('.%s' % ext, '').split())

        # eg: 'my-uploaded-file_64c942aa64.jpg'
        renamed_filename = '%(new_name)s_%(uid)s.%(ext)s' % {'new_name': new_name, 'uid': uid, 'ext': ext}

        # eg: 'images/2017/01/29/my-uploaded-file_64c942aa64.jpg'
        return os.path.join(self.path, renamed_filename)


class Image(models.Model):
    name = models.CharField(null=False, blank=False, max_length=6000, unique=True)
    upload_date = models.DateTimeField(default=timezone.now)
    image_path = time.strftime('images/%Y/%m/%d')
    file = models.FileField(upload_to=PathAndRename(image_path))

    def __str__(self):
        return self.name + " | " + self.file.name


class Category(models.Model):
    name = models.CharField(blank=False, null=False, max_length=60, unique=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    icon = models.CharField(blank=True, null=True, max_length=450)

    def __str__(self):
        return "Category: " + self.name

    def get_absolute_url(self):
        return reverse("ecommerce:category_products", kwargs={'category_id': self.id})


class Brand(models.Model):
    name = models.CharField(max_length=300)
    description = RichTextField(max_length=15000, null=True, blank=True)
    logo = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return "Brand(Company): " + self.name

    def get_absolute_url(self):
        return reverse("ecommerce:brand_products", kwargs={'brand_id': self.id})


rates = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))


class Product(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    price = models.DecimalField(max_digits=15, decimal_places=2, null=False, blank=False)
    images = models.ManyToManyField(Image, blank=False)
    add_date = models.DateTimeField(default=timezone.now)
    categories = models.ManyToManyField(Category, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    old_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    number_views = models.IntegerField(default=0)
    rate = models.IntegerField(null=True, blank=True, choices=rates)
    quantity_min = models.IntegerField(default=1, null=True, blank=True)
    # Offre spéciale (oui | non)
    is_featured = models.BooleanField(default=False)
    price_from = models.DecimalField(blank=True, max_digits=16, decimal_places=2, null=True)

    def __str__(self):
        return "Product: " + self.name + " | Price: " + str(self.price)

    def get_absolute_url(self):
        return reverse('ecommerce:product', kwargs={'product_id': self.id})

    def rating(self):
        rate = self.rate if self.rate is not None else 0
        return rate * 20


class Description(models.Model):
    text = RichTextField()
    product = models.OneToOneField(Product, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return f"Description of: {self.product}"


class Specification(models.Model):
    text = models.TextField(max_length=60000, null=True, blank=True)
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return "{} : {}".format(self.text, self.text[:200])


class Color(models.Model):
    code_hex = RGBColorField()

    def __str__(self):
        if self.code_hex is not None:
            return self.code_hex
        return "#FFFFFF"


class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0, null=False, blank=False)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, blank=True, null=True)
    first_quantity = models.IntegerField(default=0)
    price_sup = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)

    def __str__(self):
        return "Product: " + str(self.product.name) + " | Quantity: " + str(self.quantity) + " | Color: " + str(
            self.color)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ForeignKey(Image, on_delete=models.CASCADE)
    token_email = models.CharField(max_length=300, blank=True, null=True, default="")
    token_email_expiration = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "User: " + self.user.first_name + " " + self.user.last_name

    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"


# Offres
class Sale(models.Model):
    percentage = models.IntegerField()
    date_end = models.DateTimeField(blank=False, default=timezone.now)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_daily = models.BooleanField(default=False)

    def __str__(self):
        return str(self.percentage) + "% for " + self.product.name

    def new_price(self):
        return self.product.price - ((self.product.price * self.percentage) / 100)

    def saved_amount(self):
        return ((self.product.price * self.percentage) / 100)

    def rating(self):
        return (self.product.rate * 100) / 5


class Compare(models.Model):
    products = models.ManyToManyField(Product)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return "Products To Compare: " + str(self.products.all().count())


class WishList(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.profile.user.username + ' ' + self.product.name

delivery_method = (('Free Shipping', 'Free Shipping'), ('Flat Shipping Rate', 'Flat Shipping Rate'))
payment_method = (('1', 'Cash On Delivery'), ('2', 'Paypal'))
class Order(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=200, default="Created")
    comment = models.TextField(null=False, blank=True, default="")
    track_number = models.CharField(max_length=300, null=True, blank=True)
    date_payment = models.DateField(null=True, blank=True)
    date_complete = models.DateField(null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    payment_method = models.CharField(max_length=20, choices=payment_method, default='Cash On Delivery')
    delivery_method = models.CharField(max_length=20, choices=delivery_method, default='Free Shipping')
    company = models.CharField(max_length=254, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=254)
    zipcode = models.CharField(max_length=254)
    country = models.CharField(max_length=254)
    state = models.CharField(max_length=254)

    def __str__(self):
        return 'Order {0} de {1}'.format(str(self.pk), self.profile.user.username)


class OrderLine(models.Model):
    quantity = models.IntegerField()
    total = models.DecimalField(max_digits=15, decimal_places=2)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True)

    def price_unit(self):
        return self.total / self.quantity

    def __str__(self):
        return f"PRODUIT: {self.product} | TOTAL: {self.total} | ORDER: {self.order}"


class Cart(models.Model):
    quantity = models.IntegerField(default=1)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)

    def total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return '{0} x {1} : {2}'.format(str(self.quantity), self.product.name, self.profile.user.username)


class Banner(models.Model):
    title = models.CharField(max_length=650)
    description = RichTextField(max_length=100000)
    price_from = models.DecimalField(max_digits=16, decimal_places=2)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)
    external_url = models.CharField(max_length=500, null=True, blank=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)

    # ====================== To edit later ======================
    def get_absolut_url(self):
        if self.external_url is None:
            return reverse('ecommerce:home')
        return reverse('ecommerce:home')

    def get_rest(self):
        print(str((self.price_from % int(self.price_from)).normalize())[2:])
        return str((self.price_from % int(self.price_from)).normalize())[2:]

    def get_banner_image(self):
        if self.image is None or self.image == "":
            return self.product.images.first().file.url
        return self.image.file.url


class NewsLetter(models.Model):
    email = models.EmailField(max_length=255, null=False, blank=False, unique=True)
    subscribe_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"email: {self.email} | date: {self.subscribe_date} | activity: {self.is_active}"


class Message(models.Model):
    first_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(max_length=255, null=False, blank=False)
    subject = models.CharField(max_length=255, null=False, blank=False)
    message = models.TextField(max_length=20000, null=False, blank=False)

    def __str__(self):
        return f'Sender: {self.email} | Message: {self.message}'
