from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import  IsAuthenticated
from integration.emprestimos.models import Acordo, AcordoParcela 
from integration.emprestimos.serializer import  AcordoParcelaMS
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from integration.emprestimos.repository.parcelas_acordo import ParcelasAcordoRepository

class AcordoParcelasViewSet(viewsets.ModelViewSet):
    queryset = AcordoParcela.objects.all()
    serializer_class = AcordoParcelaMS
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        return serializer   
            
    def list(self, request):            

        try:
            dt_inicio = request.GET.get("dt_inicio", datetime.now() - timedelta(days=1))
            dt_final = request.GET.get("dt_final", datetime.now())
            tipo_parcela = request.GET.get("tipo_parcela", "")

            acordo_repository = ParcelasAcordoRepository()
            acordos = acordo_repository.get_acordos_parcelas(dt_inicio, dt_final, tipo_parcela)        

            return Response(data=acordos, status=status.HTTP_200_OK)
        
        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
    def retrieve(self, request, pk):     
        ''' Aqui é onde lista as parcelas a serem exibidas no modal de detalhes do empréstimo '''

        try:
            
            parcelas = AcordoParcela.objects.filter(acordo=pk).order_by('dt_vencimento')           
            serializer = AcordoParcelaMS(parcelas, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):   

        try:
            data = request.data  

            if data['tp_pagamento'] == 'vlr_total' or data['tp_pagamento'] == 'parcial':

                with transaction.atomic():
                    acordo = Acordo.objects.filter(id=data['acordo']).first()  
                    parcela = AcordoParcela.objects.filter(id=pk).first()

                    if data['tp_pagamento'] == 'vlr_total' and parcela.nr_parcela == parcela.qtd_tt_parcelas:
                        acordo.status = 'quitado'
                        acordo.save()

                    parcela.dt_pagamento = data['dt_pagamento']
                    parcela.status_pagamento =  'pago' if data['tp_pagamento'] == 'vlr_total' else 'pago_parcial'
                    parcela.vl_parcial = None if data['tp_pagamento'] == 'vlr_total' else data['vl_parcial']
                    parcela.dt_prev_pag_parcial_restante = None if data['tp_pagamento'] == 'vlr_total' else data['dt_prev_pag_parcial_restante']
                    parcela.observacoes = data['observacoes'] if data['observacoes'] else None
                    parcela.save()
                    
            return Response(data={'message': 'parcela atualizada com sucesso'},status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)
