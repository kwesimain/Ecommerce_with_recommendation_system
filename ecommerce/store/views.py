from django.shortcuts import render, get_object_or_404, redirect
from .models import OrderItem, Product, Category, Order, Customer, UserInteraction, UserProfile, ShippingAddress
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
import datetime
import json

def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    # Get recommended products for the logged-in user
    recommended_products = []
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        recommended_products = user_profile.recommended_products.all()

    return render(request, 'store/home.html', {'products': products, 'categories': categories, 'recommended_products': recommended_products})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Record a 'view' interaction
    if request.user.is_authenticated:
        UserInteraction.objects.create(user=request.user, product=product, interaction_type='view')

    return render(request, 'store/product_detail.html', {'product': product})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'store/category_list.html', {'categories': categories})

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'store/category_detail.html', {'category': category, 'products': products})

@login_required
def cart(request):
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.all()
    context = {
        'items': items,
        'order': order
    }
    return render(request, 'store/cart.html', context)


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(OrderItem, pk=item_id)
    item.delete()
    return redirect('cart')

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    customer = request.user.customer
    
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    
    order_item, item_created = OrderItem.objects.get_or_create(order=order, product=product)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if not item_created:
            order_item.quantity += quantity
        else:
            order_item.quantity = quantity
        order_item.save()

        # Record a 'add_to_cart' interaction
        UserInteraction.objects.create(user=request.user, product=product, interaction_type='add_to_cart')
    
    return redirect('cart')


def update_cart(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)
    quantity = request.POST.get('quantity')
    if quantity:
        item.quantity = int(quantity)
        item.save()
    return redirect('cart')

@login_required
def checkout(request):
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.all()
    context = {
        'items': items,
        'order': order
    }
    return render(request, 'store/checkout.html', context)


@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer, complete=True)
    order_items = order.orderitem_set.all()

    return render(request, 'store/order_summary.html', {'order': order, 'order_items': order_items})

@login_required
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer, complete=True)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if payment_method:
            return redirect('order_summary', order_id=order.id)
    
    return render(request, 'store/payment.html', {'order': order})

@login_required
def confirm_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer__user=request.user)
    
    order.complete = True
    order.save()
    
    OrderItem.objects.filter(order=order).update(order=order)

    return HttpResponseRedirect(reverse('order_summary', args=[order.id]))


@login_required
#@csrf_exempt
def process_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['address'],
                city=data['city'],
                state=data['region'],
                zipcode=data['gps']
            )
            order.complete = True
            order.save()
            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except KeyError:
            return JsonResponse({'error': 'Missing fields'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def order_success(request):
    return render(request, 'store/order_success.html')

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
            
            Customer.objects.get_or_create(user=user)
            
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})
