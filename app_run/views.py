from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from django.conf import settings
from django.contrib.auth import get_user_model
from app_run.models import Run
from app_run.serializers import RunSerializer, UserSerializerLong
from rest_framework.filters import SearchFilter


@api_view(['GET'])
def company_details(request):
    return Response({
        'company_name': settings.COMPANY_NAME,
        'slogan': settings.SLOGAN,
        'contacts': settings.CONTACTS,
    })


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = get_user_model().objects.exclude(is_superuser=True)
    serializer_class = UserSerializerLong
    filter_backends = SearchFilter,
    search_fields = 'first_name', 'last_name'

    def get_queryset(self):
        qs = super().get_queryset()
        user_type = self.request.query_params.get('type', None)
        if user_type == 'coach':
            return qs.filter(is_staff=True)
        elif user_type == 'athlete':
            return qs.filter(is_staff=False)
        else:
            return qs
