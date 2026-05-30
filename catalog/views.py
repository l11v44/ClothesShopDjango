from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from catalog.models import Product, Category
from cart.models import CartItem
from orders.models import Order, OrderItem
from orders.forms import MyNewOrderForm
from django.contrib import messages
from orders.utils import send_order_confirmation

# --- КОРЗИНА И ЗАКАЗЫ ---

def checkout(request):
    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key
    cart_items = CartItem.objects.filter(session_id=session_id)

    # Считаем сумму, аккуратно вытягивая цену из вариации
    total_price = 0
    for item in cart_items:
        total_price += item.product_variant.product.price * item.quantity

    if request.method == 'POST':
        form = MyNewOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.total_price = total_price
            order.save()
            send_order_confirmation(order)

            # Создаем товары заказа
            for item in cart_items:
                product_obj = item.product_variant.product

                OrderItem.objects.create(
                    order=order,
                    product=product_obj,
                    product_variant=item.product_variant,
                    price=product_obj.price,
                    quantity=item.quantity
                )

            cart_items.delete()
            return redirect('home')
    else:
        form = MyNewOrderForm()

    return render(request, 'checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price
    })





from catalog.models import ProductVariant

def cart_add(request, variant_id):  # Принимаем variant_id
    if not request.session.session_key:
        request.session.create()

    # Ищем конкретную вариацию (размер/цвет)
    variant = get_object_or_404(ProductVariant, id=variant_id)

    # Ищем или создаем элемент корзины именно для этой вариации
    item, created = CartItem.objects.get_or_create(
        product_variant=variant,  # Теперь привязываемся к вариации
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
    # ИСПРАВЛЕНО:
    total_price = sum(item.product_variant.product.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

def cart_remove(request, variant_id):
    if request.session.session_key:

        CartItem.objects.filter(product_variant_id=variant_id, session_id=request.session.session_key).delete()
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


# catalog/views.py
def product_detail(request, slug):
    product = get_object_or_404(Product.objects.prefetch_related('variants'), slug=slug)
    return render(request, "product_detail.html", {"product": product})


def home(request):
    return render(request, "home.html")

def reviews(request):
    reviews_list = [
        {"name": "James Anderson", "text": "Exceptional service. The quality of the materials is beyond my expectations. Highly recommended!", "stars": 5},
        {"name": "Sophie Müller", "text": "Very reliable site. My order arrived in Berlin faster than expected and perfectly packaged.", "stars": 5},
        {"name": "Liam O'Connor", "text": "Great customer support! They helped me choose the right size and the item fits perfectly.", "stars": 4},
        {"name": "Emma Dubois", "text": "Absolutely love the aesthetic. The website is very easy to use and secure.", "stars": 5},
        {"name": "Lucas Schmidt", "text": "My second purchase here. Never disappointed. Professional and trustworthy brand.", "stars": 5},
        {"name": "Charlotte Bianchi", "text": "Authentic products and very fast shipping to Italy. A very smooth shopping experience.", "stars": 5},
        {"name": "Noah Petersen", "text": "Everything was exactly as described. Transparent and honest business practice.", "stars": 4},
        {"name": "Amelia Rossi", "text": "Stunning quality and fast, professional service. Definitely coming back for more.", "stars": 5},
        {"name": "William Taylor", "text": "Everything is flawless. From the checkout process to the final product quality. 10/10.", "stars": 5},
        {"name": "Isabella Jensen", "text": "Love this store! Very trendy collection and the delivery is incredibly fast.", "stars": 5},
    ]
    return render(request, "reviews.html", {"reviews": reviews_list})

def faq(request):
    return render(request, "faq.html")

def atelier(request):
    return render(request, "atelier.html")


def heritage(request):
    milestones = [
        {"year": "1960", "title": "The First Stitch", "desc": "Founded in the heart of Milan by master tailor Lorenzo Rossi. A small workshop dedicated to the art of bespoke elegance."},
        {"year": "1974", "title": "Silk Revolution", "desc": "Introduction of our signature silk-weaving technique, setting a new standard for luxury fabrics in European fashion houses."},
        {"year": "1988", "title": "Paris Debut", "desc": "The brand's first international showcase at Paris Fashion Week, establishing us as a global symbol of quiet luxury."},
        {"year": "1995", "title": "The Golden Ratio", "desc": "Patented a unique cutting system based on mathematical precision, ensuring the perfect silhouette for every body type."},
        {"year": "2008", "title": "Legacy of Sustainability", "desc": "Pioneered the 'Eternal Garment' initiative, focusing on durability and eco-friendly sourcing long before it was a trend."},
        {"year": "2020", "title": "Digital Atelier", "desc": "Merging tradition with technology. Launching our first 3D virtual fitting room for global clients."},
        {"year": "2026", "title": "The New Era", "desc": "Continuing the journey into the future, blending smart-fabrics with the soul of artisan craftsmanship."},
    ]
    return render(request, "heritage.html", {"milestones": milestones})

@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})
def about(request):
    return render(request, 'about.html')

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


@login_required
def order_detail(request, order_id):
    # Берем заказ, проверяя ID и пользователя
    order = get_object_or_404(Order, id=order_id, user=request.user)

    return render(request, 'order_detail.html', {
        'order': order
    })

