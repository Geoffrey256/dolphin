from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("services/", views.services, name="services"),
    path("aquarium/", views.aquarium, name="aquarium"),
    path("gas/", views.gas, name="gas"),

    path("supplements/", views.supplements_list, name="supplements"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    # cart & wishlist
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<slug:slug>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/", views.update_cart, name="update_cart"),

    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/add/<slug:slug>/",
         views.add_to_wishlist, name="add_to_wishlist"),
    path("wishlist/remove/<slug:slug>/",
         views.remove_from_wishlist, name="remove_from_wishlist"),

    # checkout
    path("checkout/", views.checkout, name="checkout"),
    path("place-order/", views.place_order, name="place_order"),
    path("order-success/", views.order_success, name="order_success"),

]
