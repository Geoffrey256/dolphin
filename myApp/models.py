from decimal import Decimal
from django.db import models, transaction
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings


class Product(models.Model):
    CATEGORY_AQUARIUM = "aquarium"
    CATEGORY_GAS = "gas"
    CATEGORY_SUPPLEMENT = "supplement"

    CATEGORY_CHOICES = [
        (CATEGORY_AQUARIUM, "Aquarium"),
        (CATEGORY_GAS, "Gas"),
        (CATEGORY_SUPPLEMENT, "Supplements"),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    brief = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveSmallIntegerField(default=0,
                                                        help_text="0-100")
    stock = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES,
                                default=CATEGORY_SUPPLEMENT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:200]
            slug = base
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_discounted_price(self) -> Decimal:
        """
        Returns the price after discount (or original price if no discount).
        """
        if not self.discount_percent:
            return self.price
        multiplier = Decimal(100 - int(self.discount_percent)) / Decimal(100)
        return (self.price * multiplier).quantize(Decimal("0.01"))

    def has_discount(self) -> bool:
        return bool(self.discount_percent)

    def get_discount_amount(self) -> Decimal:
        return (self.price - self.get_discounted_price()).quantize(Decimal("0.01"))

    def is_in_stock(self) -> bool:
        return self.stock > 0

    def is_low_stock(self, threshold: int = 5) -> bool:
        return 0 < self.stock <= threshold

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.slug])


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.quantity * (self.product.discount_price or self.product.price)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"


class WishlistItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} -> {self.product.name}"
