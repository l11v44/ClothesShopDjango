from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from catalog.models import Product, Category
from cart.models import CartItem
from orders.models import Order, OrderItem
from orders.forms import MyNewOrderForm


# --- КОРЗИНА И ЗАКАЗЫ ---

def checkout(request):
    # Создаем сессию, если её нет
    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key
    cart_items = CartItem.objects.filter(session_id=session_id)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        form = MyNewOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            # Можно сохранить общую сумму, если поле есть в модели
            order.total_price = total_price
            order.save()

            # Создаем товары заказа
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )
            cart_items.delete() # Очищаем корзину
            return redirect('home') # Или на страницу успеха
    else:
        form = MyNewOrderForm()

    return render(request, 'checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price
    })

def cart_add(request, product_id):
    if not request.session.session_key:
        request.session.create()

    product = get_object_or_404(Product, id=product_id)
    item, created = CartItem.objects.get_or_create(
        product=product,
        session_id=request.session.session_key
    )
    if not created:
        item.quantity += 1
        item.save()

    return redirect('cart_detail')


def cart_detail(request):
    if not request.session.session_key:
        request.session.create()

    cart_items = CartItem.objects.filter(session_id=request.session.session_key)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


def cart_remove(request, product_id):
    if request.session.session_key:
        CartItem.objects.filter(product_id=product_id, session_id=request.session.session_key).delete()
    return redirect('cart_detail')


# --- КАТАЛОГ И ПРОДУКТЫ ---

def product_list(request):
    query = request.GET.get('q')
    category_slug = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort')

    products = Product.objects.all()

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

    return render(request, 'catalog.html', {
        'products': products,
        'categories': Category.objects.filter(parent=None)
    })


def product_detail(request, pk):
    return render(request, "product_detail.html", {"product": get_object_or_404(Product, pk=pk)})


def home(request):
    return render(request, "home.html")


# --- АУТЕНТИФИКАЦИЯ ---

@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            login(request, form.save())
            return redirect('home')
    else:
        form = UserCreationForm()
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'w-full px-4 py-3 rounded-xl border border-gray-200'})
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'w-full px-4 py-3 rounded-xl border border-gray-200'})
    return render(request, 'login.html', {'form': form})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required  # Доступ только для авторизованных
def profile(request):
    # Берем только те заказы, где user совпадает с тем, кто сейчас на сайте
    my_orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'profile.html', {
        'orders': my_orders
    })