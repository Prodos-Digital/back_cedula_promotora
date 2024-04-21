from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from integration.core.models import Contrato
from integration.core.serializer import ContratoMS
import pandas as pd
from datetime import datetime, timedelta
from integration.core.usecases.contratos import DashboardContratos
from integration.core.repository.contratos import ContratosRepository


class ContratosViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.all()
    serializer_class = ContratoMS
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        return serializer

    def list(self, request):       

        dt_inicio = request.GET.get("dt_inicio", datetime.now() - timedelta(days=1))
        dt_final = request.GET.get("dt_final", datetime.now())

        try:           
            contratos = Contrato.objects.filter(dt_digitacao__range=[dt_inicio, dt_final]).order_by('-dt_digitacao')
            serializer = ContratoMS(contratos, many=True)

            df = pd.DataFrame(serializer.data)

            if df.empty:
                data = {
                    'data': [],
                    'indicadores': {
                         "vl_contrato": 0,
                         "vl_parcela": 0,
                         "vl_comissao": 0
                    }
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

            df["vl_contrato"] = df["vl_contrato"].astype(float)
            df["vl_parcela"] = df["vl_parcela"].astype(float)
            df["vl_comissao"] = df["vl_comissao"].astype(float)

            data = {
                'data': serializer.data,
                'indicadores': {
                    "vl_contrato": df["vl_contrato"].sum(),
                    "vl_parcela": df["vl_parcela"].sum(),
                    "vl_comissao": df["vl_comissao"].sum()
                }
            }

            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):

        try:
            contrato = Contrato.objects.get(nr_contrato=pk)
            serializer = ContratoMS(contrato)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        try:
            serializer = ContratoMS(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):

        try:
            contrato = Contrato.objects.get(id=pk)
            serializer = ContratoMS(instance=contrato, data=request.data)

            if serializer.is_valid():
                serializer.save()

                return Response(data=serializer.data, status=status.HTTP_200_OK)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):

        id = request.GET.get("id")

        try:
            contrato = Contrato.objects.get(id=id)
            contrato.delete()

            return Response(status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)
        

    @action(detail=False, methods=['GET'], url_path='dashboard')
    def dashboard_contratos(self, request):        

        dt_inicio = request.GET.get("dt_inicio", datetime.now() - timedelta(days=1))
        dt_final = request.GET.get("dt_final", datetime.now())       
        convenios_query = request.GET.get("convenios", None) if request.GET.get("convenios") else ""
        bancos_query = request.GET.get("bancos", None) if request.GET.get("bancos") else ""
        promotoras_query = request.GET.get("promotoras", None) if request.GET.get("promotoras") else ""
        corretores_query = request.GET.get("corretores", None) if request.GET.get("corretores") else ""
        operacoes_query = request.GET.get("operacoes", None) if request.GET.get("operacoes") else ""

        convenios = tuple(convenios_query.split(',')) if len(convenios_query.split(',')) > 1 else convenios_query 
        bancos = tuple(bancos_query.split(',')) if len(bancos_query.split(',')) > 1 else bancos_query 
        promotoras = tuple(promotoras_query.split(',')) if len(promotoras_query.split(',')) > 1 else promotoras_query 
        corretores = tuple(corretores_query.split(',')) if len(corretores_query.split(',')) > 1 else corretores_query 
        operacoes = tuple(operacoes_query.split(',')) if len(operacoes_query.split(',')) > 1 else operacoes_query 

        try:            

            contratos_repo = ContratosRepository()
            contratos = contratos_repo.dashboard_contratos(
                dt_inicio=dt_inicio, 
                dt_final=dt_final, 
                convenios=convenios,
                bancos=bancos, 
                promotoras=promotoras, 
                corretores=corretores, 
                operacoes=operacoes, 
            )
            serializer = ContratoMS(contratos, many=True)  

            # Contabilizar os dados utilizando pandas
            etl = DashboardContratos()
            data = etl.execute(serializer.data)         

            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)
        

    @action(detail=False, methods=['GET'], url_path='bancos')
    def listar_bancos(self, request):        

        try:           
            data = Contrato.objects.filter().values('banco').distinct().order_by('banco') 
            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)
        

    @action(detail=False, methods=['GET'], url_path='promotoras')
    def listar_promotoras(self, request):        

        try:           
            data = Contrato.objects.filter().values('promotora').distinct().order_by('promotora') 
            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['GET'], url_path='corretores')
    def listar_corretores(self, request):        

        try:           
            data = Contrato.objects.filter().values('corretor').distinct().order_by('corretor') 
            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)