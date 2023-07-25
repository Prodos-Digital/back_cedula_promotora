from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from integration.core.models import Emprestimo, EmprestimoItem 
from integration.core.serializer import EmprestimoMS, EmprestimoItemMS

import pandas as pd
from datetime import datetime, timedelta


class EmprestimosViewSet(viewsets.ModelViewSet):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoMS
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        return serializer

    def list(self, request):

        dt_inicio = request.GET.get("dt_inicio", datetime.now() - timedelta(days=1))
        dt_final = request.GET.get("dt_final", datetime.now())

        try:
            #emprestimos = Emprestimo.objects.all()
            emprestimos = Emprestimo.objects.filter(dt_emprestimo__range=[dt_inicio, dt_final]).order_by('dt_emprestimo')
            serializer = EmprestimoMS(emprestimos, many=True)

            df = pd.DataFrame(serializer.data)

            if df.empty:
                data = {
                    'data': [],
                    'indicadores': {
                        "vl_emprestimo": 0,
                        "vl_capital": 0,
                        "vl_juros": 0,
                        "vl_total": 0
                    }
                }

                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

            df["vl_emprestimo"] = df["vl_emprestimo"].astype(float)
            df["vl_capital"] = df["vl_capital"].astype(float)
            df["vl_juros"] = df["vl_juros"].astype(float)
            df["vl_total"] = df["vl_total"].astype(float)

            data = {
                'data': serializer.data,
                'indicadores': {
                    "vl_emprestimo": df["vl_emprestimo"].sum(),
                    "vl_capital": df["vl_capital"].sum(),
                    "vl_juros": df["vl_juros"].sum(),
                    "vl_total": df["vl_total"].sum()
                }
            }

            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):

        try:
            emprestimo = Emprestimo.objects.get(id=pk)
            serializer = EmprestimoMS(emprestimo)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):

        try:
            emprestimo = Emprestimo.objects.get(id=pk)
            serializer = EmprestimoMS(instance=emprestimo, data=request.data)

            if serializer.is_valid():
                serializer.save()

                return Response(data=serializer.data, status=status.HTTP_200_OK)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):

        try:
            emprestimo = Emprestimo.objects.get(id=pk)
            emprestimo.delete()

            return Response(status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], url_path='calcular')
    def calc_emprestimo(self, request):

        data = request.data
        
        if data:

            try:
                vl_capital = data['vl_emprestimo'] / data['qt_parcela']
                vl_juros = data['vl_emprestimo'] * 0.2

                valores_emprestimo = {
                    'vl_capital': vl_capital, 
                    'vl_juros': vl_juros, 
                    'vl_total': vl_capital + vl_juros
                }

                return Response(data=valores_emprestimo, status=status.HTTP_200_OK)
            
            except Exception as err:
                print("ERROR>>>", err)
                return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], url_path="save")
    def create_emprestimo(self, request):

        try:
            with transaction.atomic():
                data = request.data
                emprestimo = Emprestimo(**data)
                emprestimo.save()

                get_days = lambda x: x * 30

                for parcela in range(data['qt_parcela']):
                    nr_parcela = parcela + 1
                    date = datetime.now() + timedelta(days=get_days(nr_parcela))

                    new_parcela = EmprestimoItem(
                        dt_vencimento=date,
                        nr_parcela=nr_parcela,
                        dt_pagamento=None,
                        tp_pagamento="PARCELA",
                        emprestimo=emprestimo
                    )

                    new_parcela.save()

            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path="parcelas")
    def parcelas_emprestimo(self, request):

        try:
            _id = request.GET.get("id")

            emprestimo_items = EmprestimoItem.objects.filter(emprestimo=_id)
            serializer = EmprestimoItemMS(emprestimo_items, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path="vencimento")
    def vencimento_emprestimos(self, request):

        date = request.GET.get("date", datetime.now().date())

        try:

            query = f"SELECT * FROM core_emprestimoitem WHERE dt_vencimento <= '{date}' AND dt_pagamento is NULL"
            vencimentos = EmprestimoItem.objects.raw(query)
            serializer = EmprestimoItemMS(vencimentos, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], url_path="pagamento")
    def pagamento_emprestimo(self, request):

        data = request.data

        try:

            if data['tp_pagamento'] == 'TOTAL':
                prestacao = EmprestimoItem.objects.filter(id=data['id_emprestimo_item']).update(dt_pagamento=data['dt_pagamento'])

            else:
                vencimentos = EmprestimoItem.objects.filter(emprestimo_id=data['emprestimo'], dt_pagamento__isnull=True)

                parcela_juros = EmprestimoItem(
                        dt_vencimento=vencimentos[0].dt_vencimento,
                        nr_parcela=vencimentos[0].nr_parcela,
                        dt_pagamento=data['dt_pagamento'],
                        tp_pagamento="JUROS",
                        emprestimo=vencimentos[0].emprestimo
                )

                parcela_juros.save()

                for prestacao in vencimentos:
                    prestacao.dt_vencimento += timedelta(days=30)
                    prestacao.nr_parcela += 1

                    prestacao.save()

            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)
