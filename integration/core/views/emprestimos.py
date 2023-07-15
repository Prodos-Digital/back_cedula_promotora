from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from integration.core.models import Emprestimo 
from integration.core.serializer import EmprestimoMS


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

    def create(self, request):

        try:
            serializer = EmprestimoMS(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
