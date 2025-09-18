from django.shortcuts import render


# def home(request):
#     return render(request, "home.html")

def home(request):
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
    supplements = [
        {"id": 5, "name": "Vitamin C Tablets", "price": "30,000",
            "image": "https://via.placeholder.com/200"},
        {"id": 6, "name": "Protein Powder", "price": "220,000",
            "image": "https://via.placeholder.com/200"},
    ]

    return render(request, "home.html", {
        "aquarium_products": aquarium_products,
        "gas_products": gas_products,
        "supplements": supplements,
    })


def product_detail(request, product_id):
    # For now, just a placeholder
    return render(request, "product_detail.html", {"product_id": product_id})


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


def supplements(request):
    return render(request, "supplements.html")
