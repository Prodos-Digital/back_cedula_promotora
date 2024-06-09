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

class ContratoRelatorioMS(serializers.ModelSerializer):
    nome_banco = serializers.CharField()
    nome_promotora = serializers.CharField()
    nome_convenio = serializers.CharField()
    nome_corretor = serializers.CharField()
    nome_operacao = serializers.CharField()

    class Meta:
        model = Contrato 
        fields = '__all__'

class DespesaMS(serializers.ModelSerializer):
    class Meta:
        model = Despesa 
        fields = '__all__'

class EmprestimoMS(serializers.ModelSerializer):
    class Meta:
        model = Emprestimo 
        fields = '__all__'

class EmprestimoItemMS(serializers.ModelSerializer):
    class Meta:
        model = EmprestimoItem 
        fields = '__all__'

class LojasMS(serializers.ModelSerializer):
    class Meta:
        model = Lojas 
        fields = '__all__'

class PromotoraMS(serializers.ModelSerializer):
    class Meta:
        model = Promotora 
        fields = '__all__'

class ConvenioMS(serializers.ModelSerializer):
    class Meta:
        model = Convenio 
        fields = '__all__'

class OperacaoMS(serializers.ModelSerializer):
    class Meta:
        model = Operacao 
        fields = '__all__'

class BancoMS(serializers.ModelSerializer):
    class Meta:
        model = Banco 
        fields = '__all__'

class CorretorMS(serializers.ModelSerializer):
    class Meta:
        model = Corretor 
        fields = '__all__'

class NaturezaDespesaMS(serializers.ModelSerializer):
    class Meta:
        model = NaturezaDespesa 
        fields = '__all__'

class PreContratoMS(serializers.ModelSerializer):   
    class Meta:
        model = PreContrato 
        fields = '__all__'

class PreContratoRelatorioMS(serializers.ModelSerializer):
    nome_banco = serializers.CharField()
    nome_promotora = serializers.CharField()
    nome_convenio = serializers.CharField()
    nome_corretor = serializers.CharField()
    nome_operacao = serializers.CharField()

    class Meta:
        model = PreContrato 
        fields = '__all__'

class FuturoContratoMS(serializers.ModelSerializer):   
    class Meta:
        model = FuturoContrato 
        fields = '__all__'

class FuturoContratoRelatorioMS(serializers.ModelSerializer):
    nome_banco = serializers.CharField()  
    nome_convenio = serializers.CharField()   
    nome_operacao = serializers.CharField()

    class Meta:
        model = FuturoContrato 
        fields = '__all__'