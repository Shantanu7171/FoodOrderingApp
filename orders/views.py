from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from cart.views import _cart_id
from .forms import OrderForm
from .models import Order, OrderItem, Payment
import datetime

@login_required(login_url='login')
def checkout(request):
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    except:
        cart_items = []

    if not cart_items:
        return redirect('menu')

    total = 0
    quantity = 0
    for item in cart_items:
        total += (item.dish.price * item.quantity)
        quantity += item.quantity
    
    tax = (2 * total) / 100
    grand_total = total + tax

    form = OrderForm()
    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'orders/checkout.html', context)

@login_required(login_url='login')
def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.payment_method = request.POST.get('payment_method', 'PayPal') # Access payment method from form if exists? Or separate? 
            # Defaulting to PayPal for now as per usual flows
            
            # Generate Order Number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order.order_number = current_date + str(order.user.id)
            
            # Calculate totals again based on cart (security)
            try:
                cart = Cart.objects.get(user=request.user)
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)
                total = 0
                for item in cart_items:
                    total += (item.dish.price * item.quantity)
                tax = (2 * total) / 100
                grand_total = total + tax
                order.total = grand_total
                order.tax_data = {'tax_type': {'tax_percentage': 2, 'tax_amount': float(tax)}}
                order.is_ordered = False # Not yet paid
                order.save()
                
                # Redirect to Payment
                return redirect('payments') # We will implement this
            except:
                return redirect('checkout')
        else:
             return redirect('checkout')
    return redirect('checkout')

from django.http import JsonResponse, HttpResponse
from django.conf import settings
import razorpay
import json

@login_required(login_url='login')
@login_required(login_url='login')
def payments(request):
    # try:
    # Get the order (assuming the latest one created in place_order)
    order = Order.objects.filter(user=request.user, is_ordered=False).order_by('-created_at').first()
    if not order:
        print("PAYMENTS VIEW: No pending order found.")
        return redirect('menu')
    
    # Razorpay Logic
    # client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    # amount = int(order.total * 100) # Amount in paise
    # currency = 'INR'
    # payment_capture = 1 # Auto capture
    
    # razorpay_order = client.order.create(dict(amount=amount, currency=currency, payment_capture=payment_capture))
    # print(f"PAYMENTS VIEW: Razorpay Order Created: {razorpay_order}")
    
    # context = {
    #     'order': order,
    #     'razorpay_order': razorpay_order,
    #     'razorpay_key_id': settings.RAZOR_KEY_ID,
    #     'currency': currency,
    #     'amount': amount,
    # }
    # return render(request, 'orders/payments.html', context)
    # except Exception as e:
    #     print(f"PAYMENTS VIEW ERROR: {e}")
    #     return redirect('menu')
    try:
        order = Order.objects.filter(user=request.user, is_ordered=False).order_by('-created_at').first()
        if not order:
            return redirect('menu')
        
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        amount = int(order.total * 100)
        currency = 'INR'
        payment_capture = 1
        
        razorpay_order = client.order.create(dict(amount=amount, currency=currency, payment_capture=payment_capture))
        print(f"Razorpay Order: {razorpay_order}")
        
        context = {
            'order': order,
            'razorpay_order': razorpay_order,
            'razorpay_key_id': settings.RAZOR_KEY_ID,
            'currency': currency,
            'amount': amount,
        }
        return render(request, 'orders/payments.html', context)
    except Exception as e:
        print(f"Error in payments view: {e}")
        # Render error page instead of redirect to see what happens
        return HttpResponse(f"Error processing payment: {e}")

@login_required(login_url='login')
def verify_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            print("VERIFY_PAYMENT: Request received.")
            print(f"Data: {data}")
            
            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            params_dict = {
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            }
            client.utility.verify_payment_signature(params_dict)
            print("VERIFY_PAYMENT: Signature verified.")
            
            payment = Payment.objects.create(
                user = request.user,
                payment_id = data['razorpay_payment_id'],
                payment_method = 'Razorpay',
                amount_paid = data['amount'],
                status = 'Completed'
            )
            
            order = Order.objects.get(user=request.user, is_ordered=False, order_number=data['order_number'])
            order.payment = payment
            order.is_ordered = True
            order.save()
            print("VERIFY_PAYMENT: Order updated.")
            
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            
            for item in cart_items:
                OrderItem.objects.create(
                    order = order,
                    dish = item.dish,
                    price = item.dish.price,
                    quantity = item.quantity
                )
            
            cart.delete()
            print("VERIFY_PAYMENT: Cart cleared.")
            
            return JsonResponse({'success': True, 'message': 'Payment Successful'})
        except razorpay.errors.SignatureVerificationError:
             print("VERIFY_PAYMENT: Signature mismatch!")
             return JsonResponse({'success': False, 'message': 'Payment Verification Failed'})
        except Exception as e:
             print(f"VERIFY_PAYMENT ERROR: {e}")
             return JsonResponse({'success': False, 'message': str(e)})

@login_required(login_url='login')
def order_complete(request):
    order_number = request.GET.get('order_number')
    trans_id = request.GET.get('payment_id')
    
    print(f"ORDER_COMPLETE: Checking for order {order_number}")
    
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_items = OrderItem.objects.filter(order=order)
        
        subtotal = 0
        for item in ordered_items:
            subtotal += (item.price * item.quantity)
            
        context = {
            'order': order,
            'ordered_items': ordered_items,
            'order_number': order.order_number,
            'trans_id': trans_id,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist) as e:
        print(f"ORDER_COMPLETE ERROR: {e}")
        # return redirect('home')
        return HttpResponse(f"Order not found: {e}")

