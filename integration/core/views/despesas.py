from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from integration.core.models import Despesa 
from integration.core.serializer import DespesaMS

from datetime import datetime, timedelta


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

        print(dt_inicio, dt_final)
        try:
            #despesas = Despesa.objects.all()
            despesas = Despesa.objects.filter(dt_vencimento__range=[dt_inicio, dt_final])
            serializer = DespesaMS(despesas, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

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
