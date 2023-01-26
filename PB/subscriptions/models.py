from django.db import models


# Create your models here.
class Subscription(models.Model):
    name = models.CharField(blank=False, default='', max_length=200)
    price = models.IntegerField(blank=False)
    length = models.CharField(blank=False, max_length=200)


class Purchase(models.Model):
    # card info
    name_on_card = models.CharField(default='', max_length=50)
    card_number = models.IntegerField(default=None, null=True)
    expiry_month = models.IntegerField(default=None, null=True)
    expiry_year = models.IntegerField(default=None, null=True)
    cvc = models.IntegerField(default=None, null=True)

    # subscription info
    subscribed = models.BooleanField(default=False)
    price = models.IntegerField(blank=None, null=True)
    length = models.CharField(blank=False, max_length=10)

    # date info
    current_charge = models.DateTimeField(null=True)
    next_charge = models.DateTimeField(null=True)