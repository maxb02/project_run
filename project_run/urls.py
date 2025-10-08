"""
URL configuration for project_run project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app_run.views import company_details, RunViewSet, UserViewSet, RunStarView, RunStopView, AthleteInfoView, \
    ChallengesView, PositionsViewSet, upload_file, CollectibleItemViewSet, challenge_summary, subscribe_coach, \
    rate_coach

router = DefaultRouter()
router.register('api/runs', RunViewSet, basename='runs')

router.register('api/users', UserViewSet, basename='users')
router.register('api/positions', PositionsViewSet, basename='positions')
router.register('api/collectible_item', CollectibleItemViewSet, basename='collectible_item')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/company_details/', company_details),
    path('', include(router.urls)),
    path('api/runs/<int:id>/start/', RunStarView.as_view(), name='run-start'),
    path('api/runs/<int:id>/stop/', RunStopView.as_view(), name='run-stop'),
    path('api/athlete_info/<int:user_id>/', AthleteInfoView.as_view(), name='athlete-info'),
    path('api/challenges/', ChallengesView.as_view({'get': 'list'}), name='challenges'),
    path('api/upload_file/', upload_file, name='upload-file'),
    path('api/challenges_summary/', challenge_summary, name='challenges-summary'),
    path('api/subscribe_to_coach/<int:coach_id>/', subscribe_coach, name='subscribe-coach'),
    path('api/rate_coach/<int:coach_id>/', rate_coach, name='rate-coach'),

]
