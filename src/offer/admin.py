from django.contrib import admin


# Register your models here.
from offer.models import Offer, Review, Like, Category, Type


@admin.register(Offer)
class OfferAdminModel(admin.ModelAdmin):
    pass


@admin.register(Review)
class ReviewAdminModel(admin.ModelAdmin):
    pass


@admin.register(Like)
class LikeAdminModel(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdminModel(admin.ModelAdmin):
    pass


@admin.register(Type)
class TypeAdminModel(admin.ModelAdmin):
    pass
