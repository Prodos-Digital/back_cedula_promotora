from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import  IsAuthenticated
from integration.emprestimos.models import Emprestimo, EmprestimoParcela 
from integration.emprestimos.serializer import EmprestimoMS, EmprestimoParcelaMS
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from integration.emprestimos.repository.parcelas import ParcelasEmprestimosRepository
from integration.emprestimos.usecases.etl.parcelas_emprestimos import EtlParcelasEmprestimos

class EmprestimoParcelasViewSet(viewsets.ModelViewSet):
    queryset = EmprestimoParcela.objects.all()
    serializer_class = EmprestimoParcelaMS
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        return serializer   
            
    def list(self, request):    

        try:
            dt_inicio = request.GET.get("dt_inicio", datetime.now() - timedelta(days=1))
            dt_final = request.GET.get("dt_final", datetime.now())
            tipo_parcela = request.GET.get("tipo_parcela", "")

            emprestimo_repository = ParcelasEmprestimosRepository()
            emprestimos = emprestimo_repository.get_emprestimos_parcelas(dt_inicio, dt_final, tipo_parcela)

            etl = EtlParcelasEmprestimos()
            data_etl = etl.execute(emprestimos)

            return Response(data=data_etl, status=status.HTTP_200_OK)
        
        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
    def retrieve(self, request, pk):     
        ''' Aqui é onde lista as parcelas a serem exibidas no modal de detalhes do empréstimo '''
        try:
            
            parcelas = EmprestimoParcela.objects.filter(emprestimo=pk).order_by('dt_pagamento')           
            serializer = EmprestimoParcelaMS(parcelas, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):   

        try:
            data = request.data
            print(data)

            if data['tp_pagamento'] == 'vlr_total' or data['tp_pagamento'] == 'parcial':

                with transaction.atomic():
                    emprestimo = Emprestimo.objects.filter(id=data['emprestimo']).first()  
                    parcela = EmprestimoParcela.objects.filter(id=pk).first()

                    if data['tp_pagamento'] == 'vlr_total' and parcela.nr_parcela == parcela.qtd_tt_parcelas:
                        emprestimo.status = 'quitado'
                        emprestimo.save()

                    parcela.dt_pagamento = data['dt_pagamento']
                    parcela.status_pagamento =  'pago' if data['tp_pagamento'] == 'vlr_total' else 'pago_parcial'
                    parcela.vl_parcial = None if data['tp_pagamento'] == 'vlr_total' else data['vl_parcial']
                    parcela.dt_prev_pag_parcial_restante = None if data['tp_pagamento'] == 'vlr_total' else data['dt_prev_pag_parcial_restante']
                    parcela.observacoes = data['observacoes'] if data['observacoes'] else None
                    parcela.save()
                    
            else:
                with transaction.atomic():
                    parcelas = EmprestimoParcela.objects.filter(
                        emprestimo=data['emprestimo'],
                        nr_parcela__gte=data['nr_parcela']
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
                        vl_parcela=None,
                        dt_prev_pag_parcial_restante=None
                    )

                    for parcela in parcelas:
                        due_date = (parcela.dt_vencimento + relativedelta(months=1))                       
                        parcela.dt_vencimento = due_date
                        
                        if parcela.status_pagamento == 'pago_parcial':
                            parcela.status_pagamento = 'pendente'
                            parcela.dt_pagamento = None
                            parcela.dt_prev_pag_parcial_restante = None
                            parcela.vl_parcial = None
                            parcela.observacoes = None

                        parcela.save()

            return Response(data={'message': 'parcela atualizada com sucesso'},status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)
