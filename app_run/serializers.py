from rest_framework import serializers
from .models import Run
from django.contrib.auth import get_user_model


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = 'id', 'date_joined', 'username', 'last_name', 'first_name', 'type'

    def get_type(self, obj):
        if obj.is_staff:
            return 'coach'
        return 'athlete'
