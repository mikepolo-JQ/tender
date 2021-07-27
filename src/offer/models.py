from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

"""
lmd_id : Unique ID of the offer maintained by LinkMyDeals
Status : In case of Incremental Feed, this will be new/updated/suspended
Title : Offer title
Description : Offer description stating all important Terms & Conditions
Type : Coupon Code or Deal
Coupon Code : Code to be applied to avail the offer. Empty in case of a deal
Offer : Type of offer, i.e. Percentage Off, Price Off, Cashback, BOGO, Sign-Up, etc
Offer Value : The exact percentage or price that is discounted on using the offer
Store : Name of the Online store
Categories : Comma separated list of all categories
URL : URL of the Landing page
Image : Image URL
Affiliate Link : Deeplink by your preferred Affiliate Network
Start Date : Date from which offer is applicable
End Date : Date when the offer expires
"""


class Category(models.Model):
    name = models.CharField(null=False, blank=False, unique=True, max_length=50)
    description = models.TextField(null=True, blank=True, default=None)


class Type(models.Model):
    name = models.CharField(null=False, blank=False, unique=True, max_length=50)
    description = models.TextField(null=True, blank=True, default=None)


class Offer(models.Model):
    categories = models.ManyToManyField(Category, related_name="offers")
    types = models.ManyToManyField(Type, related_name="offers")
    users = models.ManyToManyField(User, related_name="offers")
    is_active = models.BooleanField(default=True)

    rating = models.FloatField(default=0)

    lmd_id = models.CharField(
        null=False, blank=False, unique=True, max_length=25, default=None
    )
    store = models.CharField(null=False, blank=False, max_length=50)
    offer_text = models.TextField(null=True, blank=True, default=None)
    offer_value = models.CharField(null=False, blank=False, max_length=1000)
    description = models.TextField(null=True, blank=True)

    code = models.CharField(null=True, blank=True, max_length=100)

    title = models.TextField(null=False, blank=False)

    featured = models.BooleanField(null=False, blank=False)
    url = models.URLField(max_length=1000)
    smart_link = models.URLField(max_length=1000)
    image_url = models.URLField(max_length=1000)

    status = models.CharField(null=False, blank=False, max_length=25)

    start_date = models.DateField()
    end_date = models.DateField()


class Review(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField(null=False, blank=False, default=None)
    rating_value = models.IntegerField(default=0)


class Like(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
