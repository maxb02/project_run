from rest_framework import serializers
from .models import Run
from django.contrib.auth import get_user_model


class UserSerializerLong(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = 'id', 'date_joined', 'username', 'last_name', 'first_name', 'type'

    def get_type(self, obj):
        if obj.is_staff:
            return 'coach'
        return 'athlete'

class UserSerializerBase(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = 'id', 'username', 'last_name', 'first_name',




class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserSerializerBase(source='athlete')

    class Meta:
        model = Run
        fields = '__all__'
