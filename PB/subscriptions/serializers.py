from rest_framework import serializers
from subscriptions.models import Purchase, Subscription


class PurchaseSerializer(serializers.ModelSerializer):

    class Meta():
        model = Purchase
        fields = ('pk', 'name_on_card', 'card_number', 'expiry_month', 'expiry_year', 'cvc',
                  'subscribed', 'price', 'length', 'current_charge', 'next_charge')


class ChooseSubscriptionSerializer(serializers.ModelSerializer):
    class Meta():
        model = Purchase
        fields = ('pk', 'price', 'length')


class StartCancelSubscriptionSerializer(serializers.ModelSerializer):

    class Meta():
        model = Purchase
        fields = ()


class CardSerializer(serializers.ModelSerializer):

    class Meta():
        model = Purchase
        fields = ('pk', 'name_on_card', 'card_number', 'expiry_month', 'expiry_year', 'cvc')


class CancelSerializer(serializers.ModelSerializer):

    class Meta():
        model = Purchase
        fields = ()


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta():
        model = Subscription
        fields = ('name', 'price', 'length')