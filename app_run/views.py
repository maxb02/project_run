from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.views import APIView
from django.conf import settings
from django.contrib.auth import get_user_model
from app_run.models import Run, AthleteInfo, Challenge, Positions
from app_run.serializers import RunSerializer, UserSerializerLong, AthleteInfoSerializer, ChallengeSerializer, \
    PositionsSerializer
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from .utils import calculate_distance
from app_run.utils import award_challenge_if_completed


@api_view(['GET'])
def company_details(request):
    return Response({
        'company_name': settings.COMPANY_NAME,
        'slogan': settings.SLOGAN,
        'contacts': settings.CONTACTS,
    })


class Pagination(PageNumberPagination):
    page_size_query_param = 'size'


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer
    filter_backends = DjangoFilterBackend, OrderingFilter,
    filterset_fields = ('status', 'athlete')
    ordering_fields = ('created_at',)
    pagination_class = Pagination


class RunStarView(APIView):
    def post(self, request, id):
        run = get_object_or_404(Run, id=id)
        if run.status == Run.Status.INIT:
            run.status = Run.Status.IN_PROGRESS
            run.save()
            return Response({'message':
                                 'Run has started'},
                            status=status.HTTP_200_OK)
        return Response({'message':
                             f'The run status must be "init"; current status:{run.status}'},
                        status=status.HTTP_400_BAD_REQUEST)


class RunStopView(APIView):
    def post(self, request, id):
        run = get_object_or_404(Run, id=id)
        if run.status == Run.Status.IN_PROGRESS:
            run.status = Run.Status.FINISHED
            run.save()
            award_challenge_if_completed(athlete_id=run.athlete.id)
            calculate_distance(run_id=id)
            return Response({'message':
                                 'Run has finished'},
                            status=status.HTTP_200_OK)
        return Response({'message':
                             f'The run status must be "in_process"; current status:{run.status}'},
                        status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = get_user_model().objects.exclude(is_superuser=True).prefetch_related('runs')
    serializer_class = UserSerializerLong
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = 'first_name', 'last_name'
    ordering_fields = ('date_joined',)
    pagination_class = Pagination

    def get_queryset(self):
        qs = super().get_queryset()
        user_type = self.request.query_params.get('type', None)
        if user_type == 'coach':
            return qs.filter(is_staff=True)
        elif user_type == 'athlete':
            return qs.filter(is_staff=False)
        else:
            return qs


class AthleteInfoView(APIView):

    def _get_user(self, pk):
        return get_object_or_404(get_user_model(), pk=pk)

    def get(self, request, user_id):
        user = self._get_user(user_id)
        athlete_info, _ = AthleteInfo.objects.get_or_create(athlete_id=user.id)
        return Response({'user_id': athlete_info.athlete.id,
                         'weight': athlete_info.weight,
                         'goals': athlete_info.goals})

    def put(self, request, user_id):
        user = self._get_user(user_id)
        serializer = AthleteInfoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        athlete_info, _ = (AthleteInfo.objects.
                           update_or_create(athlete_id=user.id,
                                            defaults={
                                                'weight': serializer.validated_data.get('weight',
                                                                                        None),
                                                'goals': serializer.validated_data.get('goals',
                                                                                       None)}))

        return Response({'message':
                             'Athlete Info has created or updated'},
                        status=status.HTTP_201_CREATED)


class ChallengesView(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChallengeSerializer

    def get_queryset(self):
        athlete_id = self.request.query_params.get('athlete', None)
        if athlete_id:
            return Challenge.objects.filter(athlete_id=athlete_id).select_related('athlete')
        return Challenge.objects.all().select_related('athlete')


class PositionsViewSet(viewsets.ModelViewSet):
    serializer_class = PositionsSerializer

    def get_queryset(self):
        qs = Positions.objects.all()
        run_id = self.request.query_params.get('run', None)
        if run_id:
            return qs.filter(run_id=run_id)
        return qs
