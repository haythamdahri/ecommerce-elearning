from django.contrib.auth import views as auth_views
from django.http import HttpResponseRedirect
from django.urls import path, re_path, reverse

from . import views

app_name = "ecommerce"

urlpatterns = [
    path('', views.home.as_view(), name="home"),
    path('subscribe-email/', views.subscribe_email, name="subscribe_email"),
    # ---------------------- User management ----------------------
    path('account/', views.account, name="account"),
    path('login/', views.login_user, name="login"),
    path('logout/', views.log_out_user, name="logout"),
    # ---------------------- Delete from cart ----------------------
    path('delete_cart/', views.delete_cart, name="delete_cart"),
    # ---------------------- Add to wish list----------------------
    path('add-wish-list/', views.add_wish, name='add_to_wish_list'),
    # ---------------------- Add to cart ----------------------
    path('add-cart/', views.add_cart, name='add_to_cart'),
    # ---------------------- Compare list ----------------------
    path('compare-list/', views.compare_list, name='compare_list'),
    # ---------------------- Add to compare list ----------------------
    path('add-compare/', views.add_compare, name='add_to_compare'),
    # ---------------------- Delete from compare list----------------------
    path('delete-product-compare/', views.delete_product_compare, name='delete_from_compare'),
    # ---------------------- Load more carts----------------------
    path('load_carts/', views.load_carts, name='load_carts'),
    # ---------------------- Contact us ----------------------
    path('contact-us/', views.contact_us, name='contact_us'),
    # ---------------------- All products ----------------------
    path('products/', views.products, name='products'),
    # ---------------------- Category products----------------------
    path('category/products/<int:category_id>/', views.products, name='category_products'),
    # ---------------------- Single product ----------------------
    path('product/<int:product_id>/', views.product, name='product'),
    # ---------------------- COMMANDS TRACKER ----------------------
    path('commands-tracker/', views.product, name='commands_tracker'),
    # ---------------------- Wish list ----------------------
    path('wish-list/', views.WishListView.as_view(), name='wish_list'),
    # ---------------------- Delete wish list ----------------------
    path('remove-wish-list/', views.RemoveWishListView.as_view(), name='remove_wish_list'),
    # ---------------------- brand products ----------------------
    path('brand/products/<int:brand_id>/', views.products, name='brand_products'),
    # ---------------------- brand products ----------------------
    path('cart/', views.CartView.as_view(), name='cart'),
    # ---------------------- brand products ----------------------
    path('cart-update/', views.UpdateCartView.as_view(), name='update_cart'),
    # ---------------------- Checkout ----------------------
    path('checkout/', views.CheckOutView.as_view(), name='checkout'),
    # ---------------------- Checkout ----------------------
    path('checkouts/', views.CheckOutsView.as_view(), name='checkouts'),
    # ---------------------- Checkout ----------------------
    path('cash-checkout/', views.CashCheckout.as_view(), name='cash_checkout'),
    # ---------------------- Checkout ----------------------
    path('checkout/process', views.ProcessPayment.as_view(), name='process_payment'),
    # ---------------------- Payment Done ----------------------
    path('payment-done/', views.PaymentDone.as_view(), name='payment_done'),
    # ---------------------- Payment Cancelled ----------------------
    path('payment-cancelled/', views.PaymentCancelled.as_view(), name='payment_cancelled'),
    # ---------------------- Payment Cancelled ----------------------
    path('track-your-order/', views.TrackOrder.as_view(), name='track_your_order'),
    # ---------------------- Sign up Process Handlet ----------------------
    path('signup-complete/', views.signup_complete, name='signup_complete'),
    path('confirm-email/<int:id_user>/<str:token_email>/', views.confirm_email_signup, name='confirm_email_signup'),
    path('confirm_mail/resend/', views.ConfirmMailResendView.as_view(), name='confirm_mail_resend'),
    # ---------------------- Reset Password Handler ----------------------
    path('reset-password/', views.password_reset, name='password_reset'),
    path('reset-password/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    re_path('reset-password/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
            auth_views.PasswordResetConfirmView.as_view(template_name="ecommerce/registration/password_reset_confirm.html",
                                                        success_url='/ecommerce/reset-password/complete/'),
            name='password_reset_confirm'),
    path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='ecommerce/registration/password_reset_complete.html'),
         name='password_reset_complete'),

]
