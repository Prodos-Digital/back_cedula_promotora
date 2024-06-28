from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import  IsAuthenticated
from integration.emprestimos.models import EmpCliente 
from integration.emprestimos.serializer import EmpClienteMS
from rest_framework.decorators import action

class ClientesViewSet(viewsets.ModelViewSet):
    queryset = EmpCliente.objects.all()
    serializer_class = EmpClienteMS
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        return serializer

    def list(self, request):
        print('Entrou aqui no list de clientes de emprestimos...')

        try:
            clientes = EmpCliente.objects.all()
            serializer = EmpClienteMS(clientes, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)     
        
    def retrieve(self, request, pk):           

        try:           
            cliente = EmpCliente.objects.get(id=pk)   
            serializer = EmpClienteMS(cliente)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
      
        try:
            cpf = request.data.get("cpf")           
           
            if EmpCliente.objects.filter(cpf=cpf).exists():                
                return Response(data={'message': 'Já existe um cliente cadastrado com esse CPF'}, status=status.HTTP_409_CONFLICT)            
           
            serializer = EmpClienteMS(data=request.data)           
            if serializer.is_valid():                
                serializer.save()                
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)            
            
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, pk):      

        try:
            cliente = EmpCliente.objects.get(id=pk)
            serializer = EmpClienteMS(instance=cliente, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):

        try:
            cliente = EmpCliente.objects.get(id=pk)
            cliente.delete()

            return Response(status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

