
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from integration.core.models import Corretor 
from integration.core.serializer import CorretorMS

class CorretoresViewSet(viewsets.ModelViewSet):
    queryset = Corretor.objects.all()
    serializer_class = CorretorMS
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        return serializer

    def list(self, request):      

        try:   
            only_actives = request.GET.get("ativas", "")

            if only_actives:
                data = Corretor.objects.filter(is_active=True)
                serializer = CorretorMS(data, many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)  
                 
            data = Corretor.objects.all()           
            serializer = CorretorMS(data, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)    

    def create(self, request):

        try:
            serializer = CorretorMS(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):

        try:
            data = Corretor.objects.get(id=pk)
            serializer = CorretorMS(instance=data, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)
