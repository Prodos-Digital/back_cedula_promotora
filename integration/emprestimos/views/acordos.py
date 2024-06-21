from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import  IsAuthenticated
from integration.emprestimos.models import Acordo 
from integration.emprestimos.serializer import AcordoMS
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class AcordosViewSet(viewsets.ModelViewSet):
    queryset = Acordo.objects.all()
    serializer_class = AcordoMS
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        return serializer  
    
            
    def list(self, request):    

        try:
            dt_inicio = request.GET.get("dt_inicio", datetime.now() - timedelta(days=1))
            dt_final = request.GET.get("dt_final", datetime.now())           
           
            parcelas = Acordo.objects.filter(dt_acordo__range=[dt_inicio, dt_final]).order_by('dt_acordo') 
            serializer = AcordoMS(parcelas, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):   

        print('Entrou no create de acordos')    
      
        try:
            data = request.data

            serializer = AcordoMS(data=data) 
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
         
        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)
               
    def retrieve(self, request, pk):     

        try:
            
            parcelas = Acordo.objects.filter(id=pk)           
            serializer = AcordoMS(parcelas, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)
