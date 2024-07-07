
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from integration.core.models import CanalAquisicaoCliente 
from integration.core.serializer import CanalAquisicaoClienteMS

class CanalAquisicaoClienteViewSet(viewsets.ModelViewSet):
    queryset = CanalAquisicaoCliente.objects.all()
    serializer_class = CanalAquisicaoClienteMS
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        return serializer

    def list(self, request): 

        try:         
            only_actives = request.GET.get("ativas", "")

            if only_actives:
                lojas = CanalAquisicaoCliente.objects.filter(is_active=True).order_by('name')
                serializer = CanalAquisicaoClienteMS(lojas, many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            
            data = CanalAquisicaoCliente.objects.all()           
            serializer = CanalAquisicaoClienteMS(data, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)    

    def create(self, request):

        try:

            data = request.data           
            has_duplicated_name = CanalAquisicaoCliente.objects.filter(name=data["name"]).first()           

            if has_duplicated_name:               
                return Response(data={"message": "Nome já existente"}, status=status.HTTP_403_FORBIDDEN)        

            serializer = CanalAquisicaoClienteMS(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):

        try:
            data = CanalAquisicaoCliente.objects.get(id=pk)
            serializer = CanalAquisicaoClienteMS(instance=data, data=request.data)            

            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)
