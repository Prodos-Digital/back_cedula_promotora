from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from integration.core.models import Contrato
from integration.core.serializer import ContratoMS

import pandas as pd
from datetime import datetime, timedelta


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
            #contratos = Contrato.objects.all()
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
        print('Entrou no cadastrar contrato')
        print(request.data)

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

        nr_contrato = request.GET.get("nr_contrato")

        try:
            contrato = Contrato.objects.get(nr_contrato=nr_contrato)
            contrato.delete()

            return Response(status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)
