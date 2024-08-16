from rest_framework import serializers

from .models import Radiation

class RadiationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Radiation
        fields = ['year', 'radiation_value']