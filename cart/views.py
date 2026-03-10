from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from menu.models import Dish
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.decorators import login_required

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

@login_required(login_url='login')
def add_cart(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)
    try:
        # If user is authenticated, use user for cart
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            # Fallback (though this view is login_required now)
            cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
        cart.save()
 
    try:
        cart_item = CartItem.objects.get(dish=dish, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            dish = dish,
            quantity = 1,
            cart = cart
        )
        cart_item.save()
    
    return redirect('cart')

@login_required(login_url='login')
def remove_cart(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            
        cart_item = CartItem.objects.get(dish=dish, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

@login_required(login_url='login')
def remove_cart_item(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            
        cart_item = CartItem.objects.get(dish=dish, cart=cart)
        cart_item.delete()
    except:
        pass
    return redirect('cart')

@login_required(login_url='login')
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.dish.price * cart_item.quantity)
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass # Just ignore if cart doesn't exist

    tax = (2 * total) / 100
    grand_total = total + tax

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'cart.html', context)
