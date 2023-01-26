from django.contrib import admin
from subscriptions.models import Subscription, Purchase


# Register your models here.
class SubscriptionAdmin(admin.ModelAdmin):
    fields = ['name', 'price', 'length']


class PurchaseAdmin(admin.ModelAdmin):
    fields = ['name_on_card', 'card_number', 'expiry_month', 'expiry_year', 'cvc',
              'subscribed', 'price', 'length', 'current_charge', 'next_charge']


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Purchase, PurchaseAdmin)
