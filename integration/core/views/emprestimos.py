from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from integration.core.models import Emprestimo, EmprestimoItem 
from integration.core.serializer import EmprestimoMS, EmprestimoItemMS

from datetime import datetime, timedelta


class EmprestimosViewSet(viewsets.ModelViewSet):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoMS
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        return serializer

    def list(self, request):

        try:
            emprestimos = Emprestimo.objects.all()
            serializer = EmprestimoMS(emprestimos, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

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

            query = f"SELECT * FROM core_emprestimoitem WHERE dt_vencimento = '{date}' AND dt_pagamento is NULL"
            vencimentos = EmprestimoItem.objects.raw(query)
            serializer = EmprestimoItemMS(vencimentos, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)
