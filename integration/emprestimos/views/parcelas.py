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

            if tipo_parcela == 'todos':
                parcelas = EmprestimoParcela.objects.filter(dt_vencimento__range=[dt_inicio, dt_final]).order_by('dt_vencimento') 
            elif tipo_parcela == 'pendentes':
                parcelas = EmprestimoParcela.objects.filter(dt_vencimento__range=[dt_inicio, dt_final], dt_pagamento__isnull=True).order_by('dt_vencimento') 
            elif tipo_parcela == 'pagos':
                parcelas = EmprestimoParcela.objects.filter(dt_vencimento__range=[dt_inicio, dt_final], dt_pagamento__isnull=False).order_by('dt_vencimento') 
            elif tipo_parcela == 'pago_parcial':
                parcelas = EmprestimoParcela.objects.filter(dt_vencimento__range=[dt_inicio, dt_final],  vl_parcial__isnull=False).order_by('dt_vencimento') 
            elif tipo_parcela == 'juros':
                parcelas = EmprestimoParcela.objects.filter(dt_vencimento__range=[dt_inicio, dt_final], tp_pagamento='juros').order_by('dt_vencimento') 
            
            serializer = EmprestimoParcelaMS(parcelas, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        s
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
            
            if data['tp_pagamento'] == 'vlr_total' or data['tp_pagamento'] == 'parcial':
                with transaction.atomic():
                    parcela = EmprestimoParcela.objects.filter(id=pk).update(                 
                        dt_pagamento=data['dt_pagamento'],                         
                        vl_parcial=data['vl_parcial'],
                        status_pagamento='pago'
                        )
            else:
                with transaction.atomic():
                    parcelas = EmprestimoParcela.objects.filter(
                        emprestimo=data['emprestimo'],
                        nr_parcela__gte=data['nr_parcela']
                        # dt_pagamento__isnull=True,
                        # nr_parcela__isnull=False,
                    )
                   
                    parcela_a_copiar = parcelas.first()
                    
                    nova_parcela = EmprestimoParcela.objects.create(
                        emprestimo=parcela_a_copiar.emprestimo,
                        nr_parcela=None,
                        dt_vencimento=parcela_a_copiar.dt_vencimento,
                        dt_pagamento=data['dt_pagamento'],
                        tp_pagamento='juros',
                        status_pagamento='pago',
                        vl_parcial=None,
                        vl_parcela=None
                    )

                    for parcela in parcelas:
                        due_date = (parcela.dt_vencimento + relativedelta(months=1))                       
                        parcela.dt_vencimento = due_date
                        parcela.save()

            return Response(data={'message': 'parcela atualizada com sucesso'},status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)
