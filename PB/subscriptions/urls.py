from django.urls import path

from subscriptions.views import CardAPIView, PurchaseInfoAPIView, AvailableSubscriptionAPIView, \
    CardAPIView, AutoCancelSubscriptionAPIView, ChooseSubscriptionAPIView, StartSubscriptionAPIView, \
    AutoUpdateNextChargeAPIView, UpdateSubscriptionAPIView

app_name = 'subscriptions'

urlpatterns = [
    path('available/', AvailableSubscriptionAPIView.as_view(), name='available'),
    path('choose/', ChooseSubscriptionAPIView.as_view(), name='choose'),
    path('card/<int:pk>/', CardAPIView.as_view(), name='card'),
    path('start/<int:pk>/', StartSubscriptionAPIView.as_view(), name='start'),
    path('cancel/<int:pk>/', AutoCancelSubscriptionAPIView.as_view(), name='cancel'),
    path('info/<int:pk>/', PurchaseInfoAPIView.as_view(), name='info'),
    path('update/<int:pk>/', UpdateSubscriptionAPIView.as_view(), name='update_sub'),
    path('update/charge/<int:pk>/', AutoUpdateNextChargeAPIView.as_view(), name='update_charge'),
]
