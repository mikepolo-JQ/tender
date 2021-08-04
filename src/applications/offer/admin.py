from django.contrib import admin


# Register your models here.
from applications.offer.models import Offer, Review, Store, Category, Type


@admin.register(Offer)
class OfferAdminModel(admin.ModelAdmin):
    pass


@admin.register(Store)
class StoreAdminModel(admin.ModelAdmin):
    pass


@admin.register(Review)
class ReviewAdminModel(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdminModel(admin.ModelAdmin):
    pass


@admin.register(Type)
class TypeAdminModel(admin.ModelAdmin):
    pass
