from rest_framework import serializers
from .models import Pais, Estado, Ciudad

class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = '__all__'

class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = '__all__'

class CiudadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ciudad
        fields = '__all__'