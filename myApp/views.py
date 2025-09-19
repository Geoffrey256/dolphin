from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from .models import Product

# ----------------------
# Constants
# ----------------------
CART_SESSION_KEY = "cart"
WISHLIST_SESSION_KEY = "wishlist"


# ----------------------
# Home Page
# ----------------------
# def home(request):
#     aquarium_products = [
#         {"id": 1, "name": "Goldfish Bowl", "price": "45,000",
#             "image": "https://via.placeholder.com/200"},
#         {"id": 2, "name": "Aquarium Filter", "price": "120,000",
#             "image": "https://via.placeholder.com/200"},
#     ]
#     gas_products = [
#         {"id": 3, "name": "6kg Gas Cylinder", "price": "150,000",
#             "image": "https://via.placeholder.com/200"},
#         {"id": 4, "name": "Gas Stove", "price": "250,000",
#             "image": "https://via.placeholder.com/200"},
#     ]
#     supplements = Product.objects.filter(
#         category=Product.CATEGORY_SUPPLEMENT)[:4]

#     return render(request, "home.html", {
#         "aquarium_products": aquarium_products,
#         "gas_products": gas_products,
#         "supplements": supplements,
#     })


def home(request):
    query = request.GET.get("q")

    # Default: hardcoded items for aquarium and gas
    aquarium_products = [
        {"id": 1, "name": "Goldfish Bowl", "price": "45,000",
            "image": "https://via.placeholder.com/200"},
        {"id": 2, "name": "Aquarium Filter", "price": "120,000",
            "image": "https://via.placeholder.com/200"},
    ]
    gas_products = [
        {"id": 3, "name": "6kg Gas Cylinder", "price": "150,000",
            "image": "https://via.placeholder.com/200"},
        {"id": 4, "name": "Gas Stove", "price": "250,000",
            "image": "https://via.placeholder.com/200"},
    ]

    # If searching, override default products
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        return render(request, "search_results.html", {"products": products, "query": query})

    # Normal home view
    supplements = Product.objects.filter(
        category=Product.CATEGORY_SUPPLEMENT).order_by('-created_at')[:4]

    return render(request, "home.html", {
        "aquarium_products": aquarium_products,
        "gas_products": gas_products,
        "supplements": supplements,
    })


# ----------------------
# Helpers for session cart/wishlist
# ----------------------
def _get_cart(request):
    return request.session.get(CART_SESSION_KEY, {})


def _save_cart(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def _get_wishlist(request):
    return request.session.get(WISHLIST_SESSION_KEY, [])


def _save_wishlist(request, wishlist):
    request.session[WISHLIST_SESSION_KEY] = wishlist
    request.session.modified = True


def cart_items_and_total(cart):
    """
    cart: dict mapping product_id -> {"quantity": n, "price": "str"}
    returns list of {product, quantity, unit_price, subtotal} and total Decimal
    """
    items = []
    total = Decimal("0.00")
    product_ids = [int(pid) for pid in cart.keys()] if cart else []
    products = Product.objects.in_bulk(product_ids)
    for pid_str, data in cart.items():
        pid = int(pid_str)
        product = products.get(pid)
        if not product:
            continue
        quantity = int(data.get("quantity", 1))
        unit_price = Decimal(
            data.get("price", str(product.get_discounted_price())))
        subtotal = (unit_price * quantity).quantize(Decimal("0.01"))
        items.append({
            "product": product,
            "quantity": quantity,
            "unit_price": unit_price,
            "subtotal": subtotal,
        })
        total += subtotal
    return items, total.quantize(Decimal("0.01"))


# ----------------------
# Product Pages
# ----------------------
def supplements_list(request):
    supplements = Product.objects.filter(category=Product.CATEGORY_SUPPLEMENT)
    return render(request, "supplements.html", {"supplements": supplements})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, "product_detail.html", {"product": product})


# ----------------------
# Cart Views
# ----------------------
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    qty = int(request.POST.get("quantity", 1)
              ) if request.method == "POST" else 1
    if qty < 1:
        qty = 1

    if not product.is_in_stock():
        messages.error(request, "Sorry, this product is out of stock.")
        return redirect(product.get_absolute_url())

    if qty > product.stock:
        messages.warning(
            request, f"Only {product.stock} item(s) available; quantity adjusted.")
        qty = product.stock

    cart = _get_cart(request)
    pid = str(product.id)
    if pid in cart:
        new_qty = cart[pid]["quantity"] + qty
        if new_qty > product.stock:
            new_qty = product.stock
        cart[pid]["quantity"] = new_qty
    else:
        cart[pid] = {"quantity": qty, "price": str(
            product.get_discounted_price())}

    _save_cart(request, cart)
    messages.success(request, f"Added {product.name} (x{qty}) to your cart.")
    return redirect("cart")


def cart_view(request):
    cart = _get_cart(request)
    items, total = cart_items_and_total(cart)
    return render(request, "cart.html", {"items": items, "total": total})


def update_cart(request):
    if request.method != "POST":
        return redirect("cart")
    cart = _get_cart(request)
    pid = request.POST.get("product_id")
    try:
        qty = int(request.POST.get("quantity", 0))
    except (ValueError, TypeError):
        qty = 0
    if not pid or pid not in cart:
        return redirect("cart")

    product = get_object_or_404(Product, id=int(pid))
    if qty <= 0:
        cart.pop(pid, None)
    else:
        if qty > product.stock:
            qty = product.stock
            messages.warning(
                request, f"Only {product.stock} available; quantity adjusted.")
        cart[pid]["quantity"] = qty

    _save_cart(request, cart)
    return redirect("cart")


# ----------------------
# Wishlist Views
# ----------------------
def add_to_wishlist(request, slug):
    product = get_object_or_404(Product, slug=slug)
    wishlist = _get_wishlist(request)
    pid = str(product.id)
    if pid in wishlist:
        messages.info(request, "Item already in wishlist.")
    else:
        wishlist.append(pid)
        _save_wishlist(request, wishlist)
        messages.success(request, f"{product.name} added to your wishlist.")
    return redirect("wishlist")


# def wishlist_view(request):
#     wishlist = _get_wishlist(request)
#     product_ids = [int(i) for i in wishlist]
#     products = Product.objects.filter(id__in=product_ids)
#     ordered = sorted(products, key=lambda p: wishlist.index(str(p.id)))
#     return render(request, "wishlist.html", {"products": ordered})

def wishlist_view(request):
    wishlist = _get_wishlist(request)
    product_ids = [int(i) for i in wishlist]
    products = Product.objects.filter(id__in=product_ids)
    # Preserve order
    ordered = sorted(products, key=lambda p: wishlist.index(str(p.id)))
    return render(request, "wishlist.html", {"products": ordered})


def remove_from_wishlist(request, slug):
    product = get_object_or_404(Product, slug=slug)
    wishlist = _get_wishlist(request)
    pid = str(product.id)
    if pid in wishlist:
        wishlist.remove(pid)
        _save_wishlist(request, wishlist)
    return redirect("wishlist")


# ----------------------
# Checkout & Order
# ----------------------
def checkout(request):
    cart = _get_cart(request)
    items, total = cart_items_and_total(cart)
    return render(request, "checkout.html", {"items": items, "total": total})


def place_order(request):
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart")

    items, total = cart_items_and_total(cart)

    for it in items:
        if it["quantity"] > it["product"].stock:
            messages.error(
                request, f"Not enough stock for {it['product'].name}.")
            return redirect("cart")

    with transaction.atomic():
        for it in items:
            p = it["product"]
            p.stock = p.stock - it["quantity"]
            p.save()

        order_snapshot = {
            "items": [
                {"product_id": it["product"].id, "name": it["product"].name,
                 "unit_price": str(it["unit_price"]), "quantity": it["quantity"],
                 "subtotal": str(it["subtotal"])}
                for it in items
            ],
            "total": str(total)
        }
        request.session["last_order"] = order_snapshot
        request.session[CART_SESSION_KEY] = {}
        request.session.modified = True

    messages.success(request, "Order placed successfully (demo).")
    return redirect("order_success")


def order_success(request):
    order = request.session.get("last_order")
    return render(request, "order_success.html", {"order": order})


# ----------------------
# Static Pages
# ----------------------
def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def services(request):
    return render(request, "services.html")


def aquarium(request):
    return render(request, "aquarium.html")


def gas(request):
    return render(request, "gas.html")
