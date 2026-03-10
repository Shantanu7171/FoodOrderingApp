from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from menu.models import Category, Dish
from cart.models import Cart, CartItem

class CartTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.dish = Dish.objects.create(
            name='Test Dish', 
            slug='test-dish', 
            category=self.category, 
            price=10.00
        )
        self.add_cart_url = reverse('add_cart', args=[self.dish.id])
        self.remove_cart_url = reverse('remove_cart', args=[self.dish.id])
        self.remove_cart_item_url = reverse('remove_cart_item', args=[self.dish.id])

    def test_add_to_cart_authenticated(self):
        self.client.login(email='test@example.com', password='password')
        response = self.client.post(self.add_cart_url)
        self.assertEqual(response.status_code, 302) # Redirect to cart
        
        # Verify Cart exists for user
        cart = Cart.objects.get(user=self.user)
        self.assertIsNotNone(cart)
        
        # Verify Item exists
        cart_item = CartItem.objects.get(cart=cart, dish=self.dish)
        self.assertEqual(cart_item.quantity, 1)

    def test_increment_quantity(self):
        self.client.login(email='test@example.com', password='password')
        self.client.post(self.add_cart_url) # Add once
        self.client.post(self.add_cart_url) # Add again
        
        cart = Cart.objects.get(user=self.user)
        cart_item = CartItem.objects.get(cart=cart, dish=self.dish)
        self.assertEqual(cart_item.quantity, 2)

    def test_decrement_quantity(self):
        self.client.login(email='test@example.com', password='password')
        self.client.post(self.add_cart_url)
        self.client.post(self.add_cart_url) # Qty = 2
        
        self.client.get(self.remove_cart_url) # Should decrease to 1
        
        cart = Cart.objects.get(user=self.user)
        cart_item = CartItem.objects.get(cart=cart, dish=self.dish)
        self.assertEqual(cart_item.quantity, 1)

    def test_remove_item_completely(self):
        self.client.login(email='test@example.com', password='password')
        self.client.post(self.add_cart_url)
        
        self.client.get(self.remove_cart_item_url)
        
        cart = Cart.objects.get(user=self.user)
        self.assertFalse(CartItem.objects.filter(cart=cart, dish=self.dish).exists())

    def test_login_required(self):
        response = self.client.post(self.add_cart_url)
        self.assertNotEqual(response.status_code, 302) # Should check redirect location, but generally it redirects to login
        # Standard login_required redirects to login page.
        # Check if it redirects to /accounts/login/ or similar
        self.assertTrue('/accounts/login/' in response.url or '/login/' in response.url)
