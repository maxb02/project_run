from rest_framework import serializers

from .models import Run, AthleteInfo, Challenge, Positions, CollectibleItem, User


class CollectibleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectibleItem
        fields = 'name', 'uid', 'latitude', 'longitude', 'picture', 'value'


class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = 'id', 'username', 'last_name', 'first_name',


class UserListSerializer(UserBaseSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.IntegerField(read_only=True)

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + ('date_joined', 'type', 'runs_finished')

    def get_type(self, obj):
        if obj.is_staff:
            return 'coach'
        return 'athlete'


class UserDetailSerializer(UserListSerializer):
    items = CollectibleItemSerializer(many=True, read_only=True, source='collectible_items')

    class Meta(UserListSerializer.Meta):
        fields = UserListSerializer.Meta.fields + ('items',)


class CoachDetailSerializer(UserDetailSerializer):
    pass
    # athletes = serializers.SerializerMethodField()
    # athletes = serializers.CharField(source='subscribe_athlet', read_only=True)

    # class Meta(UserDetailSerializer.Meta):
    #     fields = UserDetailSerializer.Meta.fields + ('athletes',)

    # def get_athletes(self, obj):
    #     return [i.athlete.id for i in obj.subscribed.all()]


class AthleteDetailSerializer(UserDetailSerializer):
    pass
    # coach = serializers.SerializerMethodField()
    # coach = serializers.CharField(source='subscribe_coach', read_only=True)

    # class Meta(UserDetailSerializer.Meta):
    #     fields = UserDetailSerializer.Meta.fields + ('coach',)

    # def get_coach(self, obj):
    #     if obj.subscribes.all():
    #         return obj.subscribes.first().coach_id


class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserBaseSerializer(source='athlete', read_only=True)

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
    date_time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%f')

    class Meta:
        model = Positions
        fields = '__all__'

    def validate_run(self, value):
        if value.status == Run.Status.IN_PROGRESS:
            return value
        raise serializers.ValidationError(f'The run status must be "in_process"; current status:{value.status}')




