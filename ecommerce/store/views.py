# store/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import OrderItem, Product, Category, Order, Customer
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'store/home.html', {'products': products, 'categories': categories})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'store/category_list.html', {'categories': categories})

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'store/category_detail.html', {'category': category, 'products': products})

# store/views.py

@login_required
def cart(request):
    # Get the current user's cart items
    cart_items = OrderItem.objects.filter(order__customer=request.user.customer, order__complete=False)
    
    if request.method == 'POST':
        # Handle form submission to update quantities
        for item in cart_items:
            quantity_key = 'quantity_' + str(item.id)
            if quantity_key in request.POST:
                new_quantity = int(request.POST[quantity_key])
                if new_quantity > 0:
                    item.quantity = new_quantity
                    item.save()
                else:
                    # Remove item if quantity is set to 0
                    item.delete()
    
    return render(request, 'store/cart.html', {'cart_items': cart_items})

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(OrderItem, pk=item_id)
    item.delete()
    return redirect('cart')


@login_required
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = Product.objects.get(pk=product_id)
        
        # Check if the product is already in the cart
        order, created = Order.objects.get_or_create(customer=request.user.customer, complete=False)
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
        order_item.quantity += 1
        order_item.save()
        
        return redirect('cart')

    return redirect('home')  # Redirect to home if method is not POST

@login_required
def checkout(request):
    if request.method == 'POST':
        cart_items = OrderItem.objects.filter(order__customer=request.user.customer, order__complete=False)
        total = sum(item.product.price * item.quantity for item in cart_items)

        order = Order.objects.create(customer=request.user.customer, total=total, complete=False)
        
        cart_items.update(order=order)
        
        return HttpResponseRedirect(reverse('payment', args=[order.id]))
    else:
        cart_items = OrderItem.objects.filter(order__customer=request.user.customer, order__complete=False)
        total = sum(item.product.price * item.quantity for item in cart_items)
        return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total': total})


@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer__user=request.user)

    # Retrieve order items for the specific order
    order_items = OrderItem.objects.filter(order=order)

    # Calculate total price for each order item
    for order_item in order_items:
        order_item.total_price = order_item.product.price * order_item.quantity

    # Calculate total price of the order
    total_price = sum(order_item.total_price for order_item in order_items)

    context = {
        'order_items': order_items,
        'total_price': total_price,
        'order': order
    }

    # Render the order summary page
    return render(request, 'store/order_summary.html', context)


@login_required
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer__user=request.user)
    if request.method == 'POST':
        # Process the payment here, or redirect to a payment gateway
        return HttpResponseRedirect(reverse('confirm_payment', args=[order.id]))
    
    return render(request, 'store/payment.html', {'order': order})


@login_required
def confirm_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer__user=request.user)
    
    # Simulate payment processing here
    # For example, integrate with a payment gateway API
    
    # Mark the order as complete
    order.complete = True
    order.save()
    
    # Update related order items to mark them as part of a completed order
    OrderItem.objects.filter(order=order).update(order=order)

    return HttpResponseRedirect(reverse('order_summary', args=[order.id]))



@login_required
def order_history(request):
    orders = Order.objects.filter(customer=request.user.customer)
    return render(request, 'store/order_history.html', {'orders': orders})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('home'))
        else:
            return render(request, 'store/login.html', {'error': 'Invalid credentials'})
    return render(request, 'store/login.html')

def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

def user_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Create a Customer object only if it doesn't exist
            Customer.objects.get_or_create(user=user)
            
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})

