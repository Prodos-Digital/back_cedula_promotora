from rest_framework.decorators import action
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import  IsAuthenticated
from integration.emprestimos.models import Emprestimo, EmprestimoParcela 
from integration.emprestimos.serializer import EmprestimoMS
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from integration.emprestimos.repository.emprestimos import EmprestimosRepository
from integration.emprestimos.usecases.etl.emprestimos import EtlEmprestimos
from integration.emprestimos.usecases.etl.dash_emprestimos import EtlDashEmprestimos
from integration.emprestimos.repository.clientes import ClientesRepository
from integration.emprestimos.usecases.etl.clientes import HistoricoClienteEmprestimos

class EmprestimosViewSet(viewsets.ModelViewSet):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoMS
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        return serializer

    def list(self, request):        

        try:
            dt_inicio = request.GET.get("dt_inicio", datetime.now() - timedelta(days=1))
            dt_final = request.GET.get("dt_final", datetime.now())
            dt_filter = request.GET.get("dt_filter","")
            has_acordo = request.GET.get("has_acordo","")            

            emprestimo_repository = EmprestimosRepository()
            emprestimos = emprestimo_repository.get_emprestimos(dt_inicio, dt_final, dt_filter, has_acordo)

            etl = EtlEmprestimos()
            data_etl = etl.execute(emprestimos)           

            return Response(data=data_etl, status=status.HTTP_200_OK)

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
                    vl_parcela = data['vl_parcela']
                    installments = []

                    for parcela in range(data['qt_parcela']):
                            mes_cobranca = parcela + 0
                            nr_parcela = parcela + 1
                            due_date = (data_emprestimo + relativedelta(months=mes_cobranca)).date()

                            installment = EmprestimoParcela(
                                dt_vencimento=due_date,
                                nr_parcela=nr_parcela,
                                dt_pagamento=None,
                                tp_pagamento="parcela",
                                status_pagamento="pendente",
                                vl_parcial=None,
                                vl_parcela= vl_parcela,
                                emprestimo=emprestimo,
                                qtd_tt_parcelas=data['qt_parcela']
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
      
        try:
            emprestimo_repository = EmprestimosRepository()
            emprestimo = emprestimo_repository.get_emprestimo_by_id(pk)

            return Response(data=emprestimo, status=status.HTTP_200_OK)

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
        

    @action(detail=False, methods=['GET'], url_path='historico-cliente')
    def historico_emprestimo(self, request):      
        print('Entrou no histórico de cliente') 
     
        try:
            cpf = request.GET.get("cpf", "")
            cliente_rep = ClientesRepository()
            historico_cliente = cliente_rep.get_historico_cliente(cpf)
            cliente = cliente_rep.get_dados_cliente(cpf)

            etl = HistoricoClienteEmprestimos()
            data_etl = etl.execute(historico_cliente, cliente)  

            return Response(data=data_etl, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)     
        
        
    @action(detail=False, methods=['GET'], url_path='dashboard')
    def historico_emprestimo_dashboard(self, request):       
     
        try:

            dt_inicio = request.GET.get("dt_inicio", datetime.now() - timedelta(days=1))
            dt_final = request.GET.get("dt_final", datetime.now())
            dt_filter = request.GET.get("dt_filter","")

           
            emprestimo_repository = EmprestimosRepository()
            emprestimos = emprestimo_repository.get_emprestimos_for_dashboard(dt_inicio, dt_final, dt_filter)

            etl = EtlDashEmprestimos()
            data_etl = etl.execute(emprestimos)  

            return Response(data=data_etl, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)  