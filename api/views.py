from rest_framework.response import Response
from rest_framework.decorators import api_view
from paymentapp.models import Merchant
from django.core import serializers
from django.http import JsonResponse


@api_view(['GET'])
def get_data(request):
    print(request.headers['Postheader'])
    # print(request.body)
    merchants = Merchant.objects.all()
    serialised_merch = serializers.serialize('json', merchants)
    return Response(serialised_merch)
    # return Response(serialised_merch)
