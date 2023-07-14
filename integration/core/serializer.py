from rest_framework import serializers
from integration.core.models import *


class ClienteMS(serializers.ModelSerializer):
    class Meta:
        model = Cliente 
        fields = '__all__'

class ContratoMS(serializers.ModelSerializer):
    class Meta:
        model = Contrato 
        fields = '__all__'

class DespesaMS(serializers.ModelSerializer):
    class Meta:
        model = Despesa 
        fields = '__all__'
