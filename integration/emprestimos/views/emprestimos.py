from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import  IsAuthenticated
from integration.emprestimos.models import Emprestimo, EmprestimoParcela 
from integration.emprestimos.serializer import EmprestimoMS
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from rest_framework.decorators import action
import pandas as pd

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

            if dt_filter == 'dt_emprestimo':
                emprestimo = Emprestimo.objects.filter(dt_emprestimo__range=[dt_inicio, dt_final]).order_by('dt_emprestimo')
            else:
                emprestimo = Emprestimo.objects.filter(dt_cobranca__range=[dt_inicio, dt_final]).order_by('dt_cobranca')  
                
            serializer = EmprestimoMS(emprestimo, many=True)

            df = pd.DataFrame(serializer.data)

            if df.empty:
                data = {
                    'data': [],
                    'indicadores': {
                        "vl_emprestimo": 0,
                        "vl_capital_giro": 0,
                        "qtd_emprestimos": {
                            'total': 0,
                            'acordo': 0,
                            'andamento': 0,
                            'finalizado':0,
                    },                         
                    }
                }

                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            
            df["vl_emprestimo"] = df["vl_emprestimo"].astype(float)
            df["vl_capital_giro"] = df["vl_capital_giro"].astype(float)      

            status_filtro = ['acordo', 'finalizado', 'andamento']
            filtered_df = df[df['status'].isin(status_filtro)]
            contagem_por_status = filtered_df.groupby('status').size()
            contagem_por_status_dict = contagem_por_status.to_dict()     
        
            data = {
                'data': serializer.data,
                'indicadores': {
                    "vl_emprestimo": df["vl_emprestimo"].sum(),
                    "vl_capital_giro": df["vl_capital_giro"].sum(),    
                    "qtd_emprestimos": {
                        'total': df["id"].count(),
                        'acordo': contagem_por_status_dict.get('acordo', 0),
                        'andamento': contagem_por_status_dict.get('andamento', 0),
                        'finalizado': contagem_por_status_dict.get('finalizado', 0),
                    },              
                }
            }

            return Response(data=data, status=status.HTTP_200_OK)

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
        

    @action(detail=False, methods=['GET'], url_path='historico-cliente')
    def historico_emprestimo(self, request):  
        print('Entrou no historico de emprestimo')

        try:
            cpf = request.GET.get("cpf", "")
            emprestimos = Emprestimo.objects.filter(cpf=cpf)
            serializer = EmprestimoMS(emprestimos, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)     
        

    @action(detail=False, methods=['GET'], url_path='dashboard')
    def dashboard_despesas(self, request):  
        # Endereço API: http://127.0.0.1:8005/integration/despesas/dashboard/

        dt_inicio = request.GET.get("dt_inicio", datetime.now() - timedelta(days=1))
        dt_final = request.GET.get("dt_final", datetime.now())
      
        try:

            pass
            
        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)