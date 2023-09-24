from django.shortcuts import render
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.core.signing import Signer

# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

signer = Signer()
# Create your views here.
def homepage(request):
    return render(request,"homepage.html",{})

# def view_that_asks_for_money(request):

#     # What you want the button to do.
#     paypal_dict = {
#         "business": "receiver_email@example.com",
#         "amount": "10000000.00",
#         "item_name": "name of the item",
#         "invoice": "unique-invoice-id",
#         "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
#     }

#     # Create the instance.
#     form = PayPalPaymentsForm(initial=paypal_dict)
#     context = {"form": form}
#     return render(request, "payment.html", context)

def show_payment_options(request):
    # import pdb;pdb.set_trace();
    currency = 'INR'
    amount = int(request.POST.get('amount')) * 100
    amount_encrypted = signer.sign_object(amount)
    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,currency=currency,payment_capture='0'))
 
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = '/paymenthandler'
 
    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url
    context['amount_encrypted'] = amount_encrypted
 
    return render(request, 'payment_options.html', context=context)

@csrf_exempt
def paymenthandler(request):
    # import pdb;pdb.set_trace();
 
    # only accept POST request.
    if request.method == "POST":
        try:
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature,
            }
 
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                # import pdb;pdb.set_trace();
                amount = signer.unsign_object(request.GET.get('amount'))
                # amount = 100
                try:
 
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
 
                    # render success page on successful caputre of payment
                    return render(request, 'paymentsuccess.html')
                except:
 
                    # if there is an error while capturing payment.
                    return render(request, 'paymentfail.html')
            else:
 
                # if signature verification fails.
                return render(request, 'paymentfail.html')
        except:
 
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
       # if other than POST request is made.
        return HttpResponseBadRequest()
