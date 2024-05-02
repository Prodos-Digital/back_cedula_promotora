from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from integration.core.models import Despesa 
from integration.core.serializer import DespesaMS
from integration.core.models import Contrato 
from integration.core.serializer import ContratoMS

import pandas as pd
from datetime import datetime, timedelta

from integration.core.usecases.despesas import DashboardDespesas


class DespesasViewSet(viewsets.ModelViewSet):
    queryset = Despesa.objects.all()
    serializer_class = DespesaMS
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        return serializer

    def list(self, request):

        dt_inicio = request.GET.get("dt_inicio", datetime.now() - timedelta(days=1))
        dt_final = request.GET.get("dt_final", datetime.now())

        try:
            #despesas = Despesa.objects.all()
            despesas = Despesa.objects.filter(dt_vencimento__range=[dt_inicio, dt_final]).order_by('dt_vencimento')
            serializer = DespesaMS(despesas, many=True)

            df = pd.DataFrame(serializer.data)

            if df.empty:
                data = {
                    'data': [],
                    'indicadores': {
                        "pago": 0, 
                        "pendente": 0, 
                        "total": 0
                    }
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
           

            df["valor"] = df["valor"].astype(float)
            soma_por_situacao = df.groupby("situacao")["valor"].sum().reset_index()
            soma_por_situacao_dict = dict(zip(soma_por_situacao["situacao"], soma_por_situacao["valor"]))

            data = {
                'data': serializer.data,
                'indicadores': {
                    "pago": soma_por_situacao_dict.get("pago", 0), 
                    "pendente": soma_por_situacao_dict.get("pendente", 0), 
                    "total": df["valor"].sum()
                }
            }

            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):

        try:
            despesas = Despesa.objects.get(id=pk)
            serializer = DespesaMS(despesas)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        try:
            serializer = DespesaMS(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):

        try:
            despesa = Despesa.objects.get(id=pk)
            serializer = DespesaMS(instance=despesa, data=request.data)

            if serializer.is_valid():
                serializer.save()

                return Response(data=serializer.data, status=status.HTTP_200_OK)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):

        try:
            despesa = Despesa.objects.get(id=pk)
            despesa.delete()

            return Response(status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path='dashboard')
    def dashboard_despesas(self, request):  

        # dt_inicio = request.GET.get("dt_inicio", datetime.now() - timedelta(days=1))
        # dt_final = request.GET.get("dt_final", datetime.now())

        dt_inicio = '2023-01-01'
        dt_final = '2024-05-02'

        # http://127.0.0.1:8005/integration/despesas/dashboard/

        try:
           
            despesas = Despesa.objects.filter(dt_vencimento__range=[dt_inicio, dt_final]).order_by('dt_vencimento')
            serializer_despesas = DespesaMS(despesas, many=True)

            contratos = Contrato.objects.filter(dt_pag_cliente__range=[dt_inicio, dt_final]).order_by('dt_pag_cliente')
            serializer_contratos = ContratoMS(contratos, many=True)

            etl = DashboardDespesas()
            data = etl.execute(serializer_despesas.data, serializer_contratos.data)             

            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)