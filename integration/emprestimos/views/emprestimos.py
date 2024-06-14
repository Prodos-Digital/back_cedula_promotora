from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import  IsAuthenticated
from integration.emprestimos.models import Emprestimo, EmprestimoParcela 
from integration.emprestimos.serializer import EmprestimoMS
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class EmprestimosViewSet(viewsets.ModelViewSet):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoMS
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        return serializer

    def list(self, request):
        print('Entrou aqui no list de emprestimos...')

        try:
            emprestimo = Emprestimo.objects.all()
            serializer = EmprestimoMS(emprestimo, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)     


    def create(self, request):       
      
        try:

            data = request.data

            with transaction.atomic():

                serializer = EmprestimoMS(data=data) 
                if serializer.is_valid():
                    emprestimo = serializer.save()                     
                    data_emprestimo = datetime.strptime(data['dt_cobranca'], "%Y-%m-%d")
                    installments = []

                    for parcela in range(data['qt_parcela']):
                            nr_parcela = parcela + 1
                            due_date = (data_emprestimo + relativedelta(months=nr_parcela)).date()

                            installment = EmprestimoParcela(
                                dt_vencimento=due_date,
                                nr_parcela=nr_parcela,
                                dt_pagamento=None,
                                tp_pagamento="parcela",
                                status_pagamento="pendente",
                                vl_parcial=None,
                                emprestimo=emprestimo
                            )

                            installments.append(installment)                    

                    EmprestimoParcela.objects.bulk_create(installments)

                    return Response(data=serializer.data, status=status.HTTP_200_OK)
            
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
         
        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)
        

    def retrieve(self, request, pk):            
        print('Entrou aqui no retrieve de emprestimos ...')

        try:
            emprestimo = Emprestimo.objects.get(id=pk)           
            #serializer = EmprestimoMS(emprestimo)
            serializer = EmprestimoMS(instance=emprestimo)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, pk):      

        try:
            emprestimo = Emprestimo.objects.get(id=pk)
            serializer = EmprestimoMS(instance=emprestimo, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):

        try:
            emprestimo = Emprestimo.objects.get(id=pk)
            emprestimo.delete()

            return Response(status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

