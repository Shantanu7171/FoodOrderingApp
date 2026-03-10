from django.shortcuts import render, get_object_or_404
from .models import Category, Dish
from django.db.models import Q

def home(request):
    # Fetch top 8 popular dishes (or just 8 random ones for now)
    popular_dishes = Dish.objects.filter(is_available=True).order_by('?')[:8]
    categories = Category.objects.all()
    context = {
        'popular_dishes': popular_dishes,
        'categories': categories,
    }
    return render(request, 'home.html', context)

def menu(request):
    categories = Category.objects.all()
    dishes = Dish.objects.filter(is_available=True)
    
    category_slug = request.GET.get('category')
    keyword = request.GET.get('keyword')

    if category_slug:
        dishes = dishes.filter(category__slug=category_slug)
    
    if keyword:
        dishes = dishes.filter(Q(description__icontains=keyword) | Q(name__icontains=keyword))

    context = {
        'categories': categories,
        'dishes': dishes,
        'dish_count': dishes.count(),
    }
    return render(request, 'menu/menu.html', context)
