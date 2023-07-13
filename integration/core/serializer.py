from rest_framework import serializers
from integration.core.models import *


class ClienteMS(serializers.ModelSerializer):
    class Meta:
        model = Cliente 
        fields = '__all__'
