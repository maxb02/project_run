from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Run, AthleteInfo, Challenge, Positions, CollectibleItem


class UserSerializerBase(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = 'id', 'username', 'last_name', 'first_name',


class UserSerializerLong(UserSerializerBase):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()

    class Meta(UserSerializerBase.Meta):
        model = get_user_model()
        fields = UserSerializerBase.Meta.fields + ('date_joined', 'type', 'runs_finished')

    def get_type(self, obj):
        if obj.is_staff:
            return 'coach'
        return 'athlete'

    def get_runs_finished(self, obj):
        return obj.runs.filter(status=Run.Status.FINISHED).count()


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

    def validate_run(self, value):
        if value.status == Run.Status.IN_PROGRESS:
            return value
        raise serializers.ValidationError(f'The run status must be "in_process"; current status:{value.status}')


class CollectibleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectibleItem
        fields = '__all__'


class UserSerializerDetail(UserSerializerLong):
    items = CollectibleItemSerializer(many=True, read_only=True, source='collectible_items')

    class Meta(UserSerializerLong.Meta):
        model = get_user_model()
        fields = UserSerializerLong.Meta.fields + ('items',)
