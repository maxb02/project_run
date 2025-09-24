from django.core.exceptions import ValidationError


def latitude_validator(value):
    if not (-90 <= value <= 90):
        raise ValidationError('Latitude must be in the [-90; 90] range')


def longitude_validator(value):
    if not (-180 <= value <= 180):
        raise ValidationError('Longitude must be in the [-180; 180] range')
