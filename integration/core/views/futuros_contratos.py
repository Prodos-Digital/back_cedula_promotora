from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from integration.core.models import FuturoContrato
from integration.users.models import User

from integration.core.serializer import FuturoContratoMS
from datetime import datetime, timedelta
from django.db import transaction

class FuturoContratoViewSet(viewsets.ModelViewSet):
    queryset = FuturoContrato.objects.all()
    serializer_class = FuturoContratoMS
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        return serializer

    def list(self, request):    

        print('Listagem de futuros contratos')

        dt_inicio = request.GET.get("dt_inicio", datetime.now() - timedelta(days=1))
        dt_final = request.GET.get("dt_final", datetime.now())
        print(1)
        try:        
            QUERY = f"""
                        SELECT fc.*, 
                            b.name AS "nome_banco",                             
                            c.name AS "nome_convenio",
                            o.name AS "nome_operacao"
                        FROM futuros_contratos fc 
                        LEFT JOIN bancos b ON fc.banco::INTEGER = b.id                       
                        LEFT JOIN convenios c ON fc.convenio::INTEGER = c.id                        
                        LEFT JOIN operacoes o ON fc.operacao::INTEGER = o.id
                        WHERE TO_CHAR(fc.dt_efetivacao_emprestimo, 'YYYY-MM-DD') BETWEEN '{dt_inicio}' AND '{dt_final}'                       
                        ORDER BY fc.dt_efetivacao_emprestimo DESC;
                    """               
            print(QUERY)
            print(2)
            futuros_contratos = FuturoContrato.objects.raw(QUERY)
            serializer = FuturoContratoMS(futuros_contratos, many=True)
            print(3)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):            
       
        try:
          
            futuros_contrato = FuturoContrato.objects.get(id=pk) 
            serializer = FuturoContratoMS(futuros_contrato)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):       

        try:
            serializer = FuturoContratoMS(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):       

        try:
            futuros_contrato = FuturoContrato.objects.get(id=pk)
            serializer = FuturoContratoMS(instance=futuros_contrato, data=request.data)

            if serializer.is_valid():
                serializer.save()

                return Response(data=serializer.data, status=status.HTTP_200_OK)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):

        try:
            futuros_contrato = FuturoContrato.objects.get(pk=pk)
            futuros_contrato.delete()

            return Response(status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)
