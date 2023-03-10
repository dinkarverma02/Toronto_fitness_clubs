import re

# Create your views here.

# use API for studio page
import requests
from django.http import HttpResponseRedirect, JsonResponse
from geopy import distance
from rest_framework.generics import CreateAPIView, \
    ListAPIView, ListCreateAPIView

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response

from rest_framework import filters, response, status

from accounts.views import LoginAPIView
from classes.models import Class
from rest_framework.views import APIView
from studio.models import Amenities, GeoProx, Image, Studio, StudioToDistance
from studio.serializers import GeoProxStudioByCurrentLocationSerializer, \
    GeoProxStudioByPinPointSerializer, \
    GeoProxStudioByPostalSerializer, \
    StudioClickOnSerializer, StudioSerializer


# need to clean up code alot!!

def calculate_proximity(lat, long):

    all_studios = []

    for studio in Studio.objects.all():
        studio_to_distance = [studio.id, distance.geodesic((lat, long), (
            studio.latitude, studio.longitude)).km, studio.name]
        all_studios.append(studio_to_distance)
    return all_studios


def user_to_studio_distance(user_id: str, lat: float, long: float):

    # [[studio_id, distance, name],...]
    studioID_distance_studio = calculate_proximity(lat, long)

    current_user = user_id
    print(f'current user {current_user}')

    # delete other call user made to get studio by specific location

    for instance in GeoProx.objects.all():
        if instance.user_id == current_user:
            instance.delete()

    # create a new geoprox object for user
    user_to_studio = GeoProx()
    user_to_studio.user_id = current_user
    print(f'calculating distnace for {current_user}')
    user_to_studio.current_lat = lat
    user_to_studio.current_long = long
    user_to_studio.save()

    # add to user_id distance to each studio
    for studio in studioID_distance_studio:
        studio_obj = StudioToDistance()
        studio_obj.studio_id = studio[0]
        studio_obj.distance_to_studio = studio[1]
        studio_obj.studio_name = studio[2]
        studio_obj.save()
        for item in Amenities.objects.all():
            if item.studios.id == studio[0]:
                studio_obj.studio_amenities.add(item)
        for item in Class.objects.all():
            if item.studio.id == studio[0]:
                studio_obj.studio_classes.add(item)

        user_to_studio.studio_to_distance.add(studio_obj)


class SearchStudioByCurrentLocation(ListCreateAPIView):

    serializer_class = StudioSerializer
    filter_backends = [filters.SearchFilter]

    search_fields = ['studio_name', 'studio_amenities__type',
                     'studio_classes__name', 'studio_classes__coach']

    def get_queryset(self):


        lat = float(self.kwargs['lat'])
        long = float(self.kwargs['long'])

        user_to_studio_distance('a', lat, long)

        geoprox_of_user = GeoProx.objects.filter(
            user_id=str('a')).first()

        if geoprox_of_user:
            return geoprox_of_user.studio_to_distance.all().order_by(
                'distance_to_studio')
        else:
            return set()


class ViewStudio(APIView):

    def get(self, request, *args, **kwargs):

        studio_user_clicked_on = str(self.kwargs['studio_id'])

        
        user_id = 'a'



        geoprox_of_user = GeoProx.objects.filter(
            user_id=str(user_id)).first()
        responsee = Response()
        responsee.data = {}

        # if user does not exsist return everything as usual but with link not having a starting point

        if geoprox_of_user:

            user_lat = geoprox_of_user.current_lat
            user_long = geoprox_of_user.current_long
            studio_info = {}

            studio = Studio.objects.all().filter(
                id=studio_user_clicked_on).first()
            if studio:
                studio_info['name'] = studio.name
                studio_info['id'] = studio.id
                studio_info['address'] = studio.address
                studio_info['phone_number'] = studio.phone_number
                studio_info[
                    'location'] = f'{studio.latitude}, {studio.longitude}'

                amenities = []
                for amenity in Amenities.objects.all():
                    if str(amenity.studios.id) == studio_user_clicked_on:
                        amenities.append(amenity.type)
                print(amenities)
                studio_info['amenities'] = f'{amenities}'
                link_to_directions = f'https://www.google.com/maps/dir/?api=1&origin={user_lat},{user_long}&' \
                                     f'destination={studio.latitude},{studio.longitude}&travelmode=driving'
                studio_info['link_to_directions'] = link_to_directions

                images = []
                for image in Image.objects.all():
                    if str(image.studios.id) == studio_user_clicked_on:
                        images.append(
                            'http://127.0.0.1:8000/media/' + image.image.name)
                studio_info['images'] = images

                responsee.data = studio_info
                responsee.status_code = status.HTTP_200_OK
                return JsonResponse({"data": [studio_info]})
            else:

                return response.Response(
                    {'message': "Enter a valid studio id"},
                    status=status.HTTP_404_NOT_FOUND)
