from rest_framework import serializers
from .models import Run, AthleteInfo, Challenge, Positions, CollectibleItem
from django.contrib.auth import get_user_model


class UserSerializerLong(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ('id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished')

    def get_type(self, obj):
        if obj.is_staff:
            return 'coach'
        return 'athlete'

    def get_runs_finished(self, obj):
        return obj.runs.filter(status=Run.Status.FINISHED).count()


class UserSerializerBase(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = 'id', 'username', 'last_name', 'first_name',


class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserSerializerBase(source='athlete', read_only=True)

    class Meta:
        model = Run
        fields = '__all__'


class AthleteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AthleteInfo
        fields = ('weight', 'goals')


class ChallengeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name_display', read_only=True)

    class Meta:
        model = Challenge
        fields = ('full_name', 'athlete')


class PositionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Positions
        fields = '__all__'

    def validate_longitude(self, value):
        if -180 <= value <= 180:
            return value
        raise serializers.ValidationError('Longitude must be between -180 and 180 degrees')

    def validate_latitude(self, value):
        if -90 <= value <= 90:
            return value
        raise serializers.ValidationError('Latitude must be between -90 and 90 degrees')

    def validate_run(self, value):
        if value.status == Run.Status.IN_PROGRESS:
            return value
        raise serializers.ValidationError(f'The run status must be "in_process"; current status:{value.status}')

class CollectibleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectibleItem
        fields = '__all__'

    def validate_longitude(self, value):
        if -180 <= value <= 180:
            return value
        raise serializers.ValidationError('Longitude must be between -180 and 180 degrees')

    def validate_latitude(self, value):
        if -90 <= value <= 90:
            return value
        raise serializers.ValidationError('Latitude must be between -90 and 90 degrees')