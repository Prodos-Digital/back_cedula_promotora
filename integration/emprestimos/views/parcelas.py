from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import  IsAuthenticated
from integration.emprestimos.models import Emprestimo, EmprestimoParcela 
from integration.emprestimos.serializer import EmprestimoMS, EmprestimoParcelaMS
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class EmprestimoParcelasViewSet(viewsets.ModelViewSet):
    queryset = EmprestimoParcela.objects.all()
    serializer_class = EmprestimoParcelaMS
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        return serializer  
    
            
    def list(self, request):    
        print('Entrou no list de parcelas') 

        try:
            dt_inicio = request.GET.get("dt_inicio", datetime.now() - timedelta(days=1))
            dt_final = request.GET.get("dt_final", datetime.now())
            tipo_parcela = request.GET.get("tipo_parcela", "")
            print('tipo_parcela: ',tipo_parcela)
                     
            parcelas = EmprestimoParcela.objects.filter(dt_vencimento__range=[dt_inicio, dt_final]).order_by('dt_vencimento')  
            serializer = EmprestimoParcelaMS(parcelas, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
    def retrieve(self, request, pk):     

        try:
            
            parcelas = EmprestimoParcela.objects.filter(emprestimo=pk)           
            serializer = EmprestimoParcelaMS(parcelas, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):      

        try:

            data = request.data 
            
            print(data)
            print(data['emprestimo'])
            
            if data['tp_pagamento'] == 'vlr_total' or data['tp_pagamento'] == 'parcial':
                with transaction.atomic():
                    parcela = EmprestimoParcela.objects.filter(id=pk).update(                 
                        dt_pagamento=data['dt_pagamento'], 
                        tp_pagamento = data['tp_pagamento'], 
                        vl_parcial=data['vl_parcial']
                        )
            else:
                with transaction.atomic():
                    print(1)
                    parcelas = EmprestimoParcela.objects.filter(
                        emprestimo=data['emprestimo'],
                        nr_parcela__gte=data['nr_parcela']
                        # nr_parcela__isnull=False,
                        # dt_pagamento__isnull=True,
                    )
                    print(2)

                    parcela_a_copiar = parcelas.first()
                    print(parcela_a_copiar)
                    print(3)

                     # Criar a nova parcela como uma cópia da selecionada
                    nova_parcela = EmprestimoParcela.objects.create(
                        emprestimo=parcela_a_copiar.emprestimo,
                        nr_parcela=None,
                        dt_vencimento=parcela_a_copiar.dt_vencimento,
                        dt_pagamento=data['dt_pagamento'],
                        tp_pagamento=data['tp_pagamento'],
                        status_pagamento=None,
                        vl_parcial=None,
                        vl_parcela=None
                    )

                    print(4)
                    
                    for parcela in parcelas:
                        due_date = (parcela.dt_vencimento + relativedelta(months=1))
                        #parcela.tp_pagamento = data['tp_pagamento']
                        parcela.dt_vencimento = due_date
                        parcela.save()

                    

            return Response(data={'message': 'parcela atualizada com sucesso'},status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)
