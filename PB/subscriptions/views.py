from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, RetrieveAPIView, ListAPIView
from subscriptions.serializers import PurchaseSerializer, CardSerializer, SubscriptionSerializer, \
    ChooseSubscriptionSerializer, StartCancelSubscriptionSerializer
from rest_framework import response, status
from subscriptions.models import Purchase, Subscription
from datetime import timedelta
from django.utils import timezone


# see what subscription plans are available
class AvailableSubscriptionAPIView(ListAPIView):
    """
    Used to see which subscription plans options are available

    Resources used:
    - https://www.django-rest-framework.org/api-guide/generic-views/#examples
    -
    """
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()

    def list(self, request):
        auth_token = request.COOKIES.get('auth_token')

        if auth_token:
            queryset = self.get_queryset()
            serializer = SubscriptionSerializer(queryset, many=True)
            return response.Response({'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return response.Response(
                {'message': "you are not authorized to access available subscriptions, login again"},
                status=status.HTTP_401_UNAUTHORIZED)


class ChooseSubscriptionAPIView(APIView):
    """
    Used to choose a subscription plan
    """
    serializer_class = ChooseSubscriptionSerializer

    def post(self, request):
        auth_token = request.COOKIES.get('auth_token')

        if auth_token:
            serializer = self.serializer_class(data=request.data)

            # error check for payload
            if request.data['price'] == '':
                return response.Response({"price": "price is required"},
                                         status=status.HTTP_400_BAD_REQUEST)
            if request.data['length'] == '':
                return response.Response({"length": "length is required"},
                                         status=status.HTTP_400_BAD_REQUEST)

            if serializer.is_valid():
                serializer.save()
                return response.Response({'message': 'Subscription plan successfully chosen',
                                          'data': serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response({'message': "you are not authorized to choose subscriptions, login again"},
                                     status=status.HTTP_401_UNAUTHORIZED)


def today():
    return str(timezone.now())


def bi_weekly():
    return str(timezone.now() + timedelta(days=14))


def one_month():
    return str(timezone.now() + timedelta(days=30))


def one_year():
    return str(timezone.now() + timedelta(days=365))


class UpdateSubscriptionAPIView(RetrieveUpdateAPIView):
    """
    update subscription choice based on whether they are already subscribed or not
    """
    queryset = Purchase.objects.all()
    serializer_class = ChooseSubscriptionSerializer

    def put(self, request, pk):
        auth_token = request.COOKIES.get('auth_token')

        if auth_token:
            purchase = Purchase.objects.get(id=pk)

            # error check for payload
            if request.data['price'] == '':
                return response.Response({"price": "price is required"},
                                         status=status.HTTP_400_BAD_REQUEST)
            if request.data['length'] == '':
                return response.Response({"length": "length is required"},
                                         status=status.HTTP_400_BAD_REQUEST)

            # if user has a subscription already, re-initialize the charge dates
            if purchase.subscribed:
                if request.data['length'] == 'yearly':
                    purchase.current_charge = today()
                    purchase.next_charge = one_year()
                elif request.data['length'] == 'monthly':
                    purchase.current_charge = today()
                    purchase.next_charge = one_month()
                elif request.data['length'] == 'bi_weekly':
                    purchase.current_charge = today()
                    purchase.next_charge = bi_weekly()

            serializer = self.serializer_class(purchase, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return response.Response({'message': 'Successfully updated subscription plan',
                                          'data': serializer.data}, status=status.HTTP_200_OK)
            else:
                return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response(
                {'message': "you are not authorized to update the subscription plan, login again"},
                status=status.HTTP_401_UNAUTHORIZED)


class CardAPIView(RetrieveUpdateAPIView):
    """
    used to update credit card info
    """
    queryset = Purchase.objects.all()
    serializer_class = CardSerializer

    def put(self, request, pk):
        auth_token = request.COOKIES.get('auth_token')

        if auth_token:
            purchase = Purchase.objects.get(id=pk)
            serializer = self.serializer_class(purchase, data=request.data)

            # error check card information
            if len(request.data['card_number']) != 16:
                return response.Response({'card_number': "make sure card number is 16 characters in length"},
                                         status=status.HTTP_400_BAD_REQUEST)
            if len(request.data['expiry_month']) != 2:
                return response.Response({'expiry_month': "make sure expiry month is in the format MM"},
                                         status=status.HTTP_400_BAD_REQUEST)
            if len(request.data['expiry_year']) != 2:
                return response.Response({'expiry_year': "make sure expiry year is in the format YY"},
                                         status=status.HTTP_400_BAD_REQUEST)
            if len(request.data['cvc']) != 3:
                return response.Response({'cvc': " make sure cvc is 3 characters in length"},
                                         status=status.HTTP_400_BAD_REQUEST)

            if serializer.is_valid():
                serializer.save()
                return response.Response({'message': 'Successfully updated card details',
                                          'data': serializer.data}, status=status.HTTP_200_OK)
            else:
                return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response({'message': "you are not authorized to update card info, login again"},
                                     status=status.HTTP_401_UNAUTHORIZED)


class StartSubscriptionAPIView(RetrieveUpdateAPIView):
    """
    Used to start up a subscription and set a date for when the current and next charge will occur
    """
    queryset = Purchase.objects.all()
    serializer_class = StartCancelSubscriptionSerializer

    def put(self, request, pk):
        auth_token = request.COOKIES.get('auth_token')

        if auth_token:
            purchase = Purchase.objects.get(id=pk)
            purchase.subscribed = True

            # make sure you can't make a subscription until you enter your card info
            if purchase.name_on_card is None or purchase.card_number is None or purchase.cvc is None or \
                    purchase.expiry_month is None or purchase.expiry_year is None:
                return response.Response({"message": "incomplete card info, please provide all fields"},
                                         status=status.HTTP_400_BAD_REQUEST)

            # set user's subscription dates based on entry
            if purchase.length == 'yearly':
                purchase.current_charge = today()
                purchase.next_charge = one_year()
            elif purchase.length == 'monthly':
                purchase.current_charge = today()
                purchase.next_charge = one_month()
            elif purchase.length == 'bi_weekly':
                purchase.current_charge = today()
                purchase.next_charge = bi_weekly()

            serializer = self.serializer_class(purchase, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return response.Response({'message': 'Successfully started the subscription',
                                          'data': serializer.data}, status=status.HTTP_200_OK)
            else:
                return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response(
                {'message': "you are not authorized to start the subscription, login again"},
                status=status.HTTP_401_UNAUTHORIZED)


class AutoCancelSubscriptionAPIView(RetrieveUpdateAPIView):
    """
    "Automatically" cancel subscription once you send 'put' request
    (no need for body)
    """
    queryset = Purchase.objects.all()
    serializer_class = StartCancelSubscriptionSerializer

    def put(self, request, pk):
        auth_token = request.COOKIES.get('auth_token')

        if auth_token:
            purchase = Purchase.objects.get(id=pk)
            purchase.subscribed = False
            purchase.next_charge = None
            serializer = self.serializer_class(purchase, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return response.Response({'message': 'Successfully cancelled your subscription',
                                          'data': serializer.data}, status=status.HTTP_200_OK)
            else:
                return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response(
                {'message': "you are not authorized to cancel the subscription, login again"},
                status=status.HTTP_401_UNAUTHORIZED)


class PurchaseInfoAPIView(RetrieveAPIView):
    """
    Used to see your final purchase receipt
    """
    serializer_class = PurchaseSerializer

    def get(self, request, pk):
        auth_token = request.COOKIES.get('auth_token')

        if auth_token:
            try:
                purchase = Purchase.objects.get(id=pk)
                serializer = self.serializer_class(purchase)
                return response.Response({'data': serializer.data}, status=status.HTTP_200_OK)
            except Purchase.DoesNotExist:
                return response.Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response(
                {'message': "you are not authorized to access your subscription info, login again"},
                status=status.HTTP_401_UNAUTHORIZED)


class AutoUpdateNextChargeAPIView(RetrieveUpdateAPIView):
    """
    Once you send 'put' request, "Automatically" set the current charge and
    next charge based on when we have reached the next charge date
    (no need for body)
    """
    queryset = Purchase.objects.all()
    serializer_class = StartCancelSubscriptionSerializer

    def put(self, request, pk):
        auth_token = request.COOKIES.get('auth_token')

        if auth_token:
            purchase = Purchase.objects.get(id=pk)
            purchase.subscribed = True

            # set current charge to today and next charge to a year from now
            if purchase.length == 'yearly':
                if purchase.next_charge == today():
                    purchase.current_charge = today()
                    purchase.next_charge = one_year()
            # set current charge to today and next charge to a month from now
            elif purchase.length == 'monthly':
                if purchase.next_charge == today():
                    purchase.current_charge = today()
                    purchase.next_charge = one_month()
            elif purchase.length == 'bi_weekly':
                if purchase.next_charge == today():
                    purchase.current_charge = today()
                    purchase.next_charge = bi_weekly()

            serializer = self.serializer_class(purchase, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return response.Response({'message': 'Successfully auto-updated the charge cycle',
                                          'data': serializer.data}, status=status.HTTP_200_OK)
            else:
                return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response({'message': "you are not authorized, login again"},
                                     status=status.HTTP_401_UNAUTHORIZED)
