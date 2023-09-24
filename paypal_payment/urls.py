from django.urls import path
from . import views

urlpatterns = [
    path('',views.homepage,name='homepage'),
    path('payments/',views.show_payment_options,name='payment-options'),
    path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    # path('paypal-payments/',views.view_that_asks_for_money,name='paypal-form'),
]