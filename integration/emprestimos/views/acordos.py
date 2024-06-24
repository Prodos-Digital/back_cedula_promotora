from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import  IsAuthenticated
from integration.emprestimos.models import Acordo, Emprestimo, EmprestimoParcela
from integration.emprestimos.serializer import AcordoMS
from datetime import datetime, timedelta

class AcordosViewSet(viewsets.ModelViewSet):
    queryset = Acordo.objects.all()
    serializer_class = AcordoMS
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        return serializer  
    
            
    def list(self, request):    

        try:
            print('Entrou aqui no list de acordos')
            dt_inicio = request.GET.get("dt_inicio", datetime.now() - timedelta(days=1))
            dt_final = request.GET.get("dt_final", datetime.now())           
           
            parcelas = Acordo.objects.filter(dt_acordo__range=[dt_inicio, dt_final]).order_by('-dt_acordo') 
            serializer = AcordoMS(parcelas, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):   
      
        try:
            id_emprestimo = request.GET.get("id_emprestimo")
            data = request.data

            with transaction.atomic(): 
                if id_emprestimo:
                    emprestimo = Emprestimo.objects.get(id=id_emprestimo)
                    emprestimo.status = 'acordo'
                    emprestimo.save()       

                    parcelas = EmprestimoParcela.objects.filter(
                        emprestimo=id_emprestimo
                    ).exclude( 
                        status_pagamento__in=['pago', 'pago_parcial']
                    ) 

                    for parcela in parcelas:
                        parcela.tp_pagamento = 'acordo'
                        parcela.save()

       
                serializer = AcordoMS(data=data) 
                if serializer.is_valid():
                    serializer.save()
                    return Response(data=serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
         
        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)
               
    def retrieve(self, request, pk):     

        try:
            
            acordo = Acordo.objects.filter(id=pk)           
            serializer = AcordoMS(acordo, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):

        try:
            acordo = Acordo.objects.get(id=pk)
            acordo.delete()

            return Response(status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)