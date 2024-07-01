from rest_framework import serializers
from integration.emprestimos.models import *

class EmpClienteMS(serializers.ModelSerializer):
    class Meta:
        model = EmpCliente 
        fields = '__all__'

class EmprestimoMS(serializers.ModelSerializer):
    class Meta:
        model = Emprestimo 
        fields = '__all__'

class EmprestimoParcelaMS(serializers.ModelSerializer):
    class Meta:
        model = EmprestimoParcela 
        fields = '__all__'

class AcordoMS(serializers.ModelSerializer):
    class Meta:
        model = Acordo 
        fields = '__all__'

class AcordoParcelaMS(serializers.ModelSerializer):
    class Meta:
        model = AcordoParcela 
        fields = '__all__'
