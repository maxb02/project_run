from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from django.conf import settings

from app_run.models import Run
from app_run.serializers import RunSerializer


@api_view(['GET'])
def company_details(request):
    return Response({
        'company_name': settings.COMPANY_NAME,
        'slogan': settings.SLOGAN,
        'contacts': settings.CONTACTS,
    })


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all()
    serializer_class = RunSerializer
