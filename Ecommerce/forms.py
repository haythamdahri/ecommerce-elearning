import re

from django import forms
from django.contrib.auth.models import User
from Ecommerce.models import Category, NewsLetter, Message

CATEGORIES = list()
CATEGORIES.append(('all','Tous les categories'))
CATEGORIES.extend(list((x.id, x.name) for x in Category.objects.all()))

class SearchForm(forms.Form):
    search = forms.CharField(required=False, max_length=50,
                             widget=forms.TextInput(attrs={'placeholder': 'Quest-ce que vous recherchez...',
                                                           'class': 'form-control search-field',
                                                           'dir': 'ltr',
                                                           'id': 'search'}))
    category = forms.ChoiceField(required=False,  choices=CATEGORIES, widget=forms.Select(attrs={'class': 'postform resizeselect',
                                                                                  'id': 'product_cat'}))

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs \
            .update({
            'class': 'level-0'
        })


class SignUpForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'id': 'signup_username', 'placeholder': 'Nom d\'utilisateur', 'class': 'input-text'}))
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'id': 'signup_email', 'placeholder': 'Email', 'class': 'input-text'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'id': 'signup_password', 'placeholder': 'Mot de passe', 'class': 'input-text', 'type': 'password'}))
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'signup_first_name', 'placeholder': 'Nom', 'class': 'input-text'}))
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'signup_last_name', 'placeholder': 'Prenom', 'class': 'input-text'}))

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'username']

    def clean_password(self):
        password = self.cleaned_data['password']
        if not re.match(r'^[a-zA-Z]{5,20}\d{1,10}$', password):
            raise forms.ValidationError(['Mot de passe non validé! [des lettres suivis par un ou plusieurs nombres]'])
        return password

    def clean_username(self):
        username = self.cleaned_data['username']
        print(User.objects.all().values('username'))
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(['Username déja utilisé!'])
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(['Adresse email déja utilisée!'])
        return email


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'id': 'login_email', 'placeholder': 'email', 'class': 'input-text'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'id': 'login_password', 'placeholder': 'mot de passe', 'class': 'input-text', 'type': 'password'}))

class ConfirmEmailForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'id': 'confirm_email', 'placeholder': 'Votre adresse email pour recevoir le lien d\'activation', 'class': 'input-text'}))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")


        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.add_error('email', 'Adresse email introuvable')


class SubscribeEmail(forms.ModelForm):
    class Meta:
        model = NewsLetter
        fields = ['email']


class ContactForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = '__all__'


class UserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'id': 'account_username', 'placeholder': 'Nom d\'utilisateur', 'class': 'input-text'}))
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'id': 'account_email', 'placeholder': 'Email', 'class': 'input-text'}))
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'account_first_name', 'placeholder': 'Nom', 'class': 'input-text'}))
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'account_last_name', 'placeholder': 'Prenom', 'class': 'input-text'}))
    is_password_change = forms.IntegerField(required=True, widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'is_password_change']



class UserPasswordForm(forms.ModelForm):
    password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'id': 'password_reset_password', 'placeholder': 'Ancien mot de passe', 'class': 'input-text'}))
    new_password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'id': 'password_reset_new_password', 'placeholder': 'Nouveau mot de passe', 'class': 'input-text'}))
    confirm_new_password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'id': 'confirm_new_password', 'placeholder': 'Confirmer nouveau mot de passe', 'class': 'input-text'}))
    is_password_change = forms.IntegerField(required=True, widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ['password', 'new_password', 'confirm_new_password', 'is_password_change']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        new_password = cleaned_data.get("new_password")
        confirm_new_password = self.cleaned_data['confirm_new_password']
        c = re.compile(r'^[a-zA-Z]{5,20}\d{1,10}$')
        print(new_password)
        if c.match(new_password) is None:
            print("BAD")
        else:
            print("GREAT")
        if not new_password == confirm_new_password:
            self.add_error('new_password', 'nouveau mot de passe non confirmé!')
            self.add_error('confirm_new_password', 'confirmation mot de passe invalide!')
        elif c.match(new_password) is None:
            self.add_error('new_password',
                           'Nouveau mot de passe non validé! [des lettres suivis par un ou plusieurs nombres]')

class GoPageForm(forms.Form):
    page = forms.CharField(required=True, widget=forms.NumberInput(attrs={'min': 1, 'step':1, 'class': 'form-control'}))


class PriceFilterForm(forms.Form):
    min_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'id':'min_price', 'placeholder':'Prix min', 'min':'0', 'class': 'form-control one-edge-shadow', 'style':'border: 2px solid #fed81c;'}))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'id':'max_price', 'placeholder':'Prix max', 'min':'0', 'class': 'form-control one-edge-shadow', 'style':'border: 2px solid #fed81c;'}))

PAYMENT_METHODS = (('Cash On Delivery', 'Paiement à la livraison'),('Paypal', 'Paiement en ligne'))
class CheckOutForm(forms.Form):
    first_name = forms.CharField(label="Nom", required=True, widget=forms.TextInput(attrs={'class': 'input-text', 'placeholder':'Nom'}))
    last_name = forms.CharField(label="Prenom", required=True, widget=forms.TextInput(attrs={'class': 'input-text', 'placeholder':'Prenom'}))
    company_name = forms.CharField(label="Societe", required=True, widget=forms.TextInput(attrs={'class': 'input-text', 'placeholder':'Societe'}))
    email = forms.EmailField(label="Email", required=True, widget=forms.EmailInput(attrs={'class': 'input-text', 'placeholder':'Email'}))
    phone = forms.CharField(label="Telephone", required=True, widget=forms.NumberInput(attrs={'class': 'input-text', 'placeholder':'Telephone'}))
    address = forms.CharField(label="Adresse de livraison", required=True, widget=forms.TextInput(attrs={'class': 'input-text', 'placeholder':'Address'}))
    state = forms.CharField(label="Region", required=True, widget=forms.TextInput(attrs={'class': 'input-text', 'placeholder':'Region'}))
    city = forms.CharField(label="Ville", required=True, widget=forms.TextInput(attrs={'class': 'input-text', 'placeholder':'Ville'}))
    zipcode = forms.CharField(label="Code postal", required=True, widget=forms.TextInput(attrs={'class': 'input-text', 'placeholder':'Code postale'}))
    order_note = forms.CharField(label="Commentaire", required=False, widget=forms.Textarea(attrs={'class': 'input-text', 'placeholder':'Commenter votre ordre', 'cols': '5', 'rows': '3'}))
    payment_method = forms.CharField(label="Methode de paiement", required=True, widget=forms.RadioSelect(choices=PAYMENT_METHODS))


class TrackOrderForm(forms.Form):
    order_id = forms.CharField(required=True, widget=forms.NumberInput(attrs={'class':'input-text', 'placeholder':'ID de la commande'}))
    order_email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class':'input-text', 'placeholder':'EMAIL de la commande'}))

