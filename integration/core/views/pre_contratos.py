from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from integration.core.models import PreContrato, Contrato
from integration.users.models import User
from integration.core.serializer import PreContratoMS, PreContratoRelatorioMS, ContratoMS
from datetime import datetime, timedelta
from django.db import transaction
from integration.core.repository.pre_contratos import PreContratosRepository
from integration.core.usecases.pre_contratos import EtlApuracaoPreContratos

class PreContratosViewSet(viewsets.ModelViewSet):
    queryset = PreContrato.objects.all()
    serializer_class = PreContratoMS
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        return serializer

    def list(self, request):          

        dt_inicio = request.GET.get("dt_inicio", datetime.now() - timedelta(days=1))
        dt_final = request.GET.get("dt_final", datetime.now())
        user_id = request.GET.get("user_id", "")
        has_contrato = request.GET.get("has_contrato", "")     

        convenios_query = request.GET.get("convenios", None) if request.GET.get("convenios") else ""
        bancos_query = request.GET.get("bancos", None) if request.GET.get("bancos") else ""
        promotoras_query = request.GET.get("promotoras", None) if request.GET.get("promotoras") else ""
        corretores_query = request.GET.get("corretores", None) if request.GET.get("corretores") else ""
        operacoes_query = request.GET.get("operacoes", None) if request.GET.get("operacoes") else ""

        convenios = tuple(convenios_query.split(',')) if len(convenios_query.split(',')) > 1 else convenios_query 
        bancos = tuple(bancos_query.split(',')) if len(bancos_query.split(',')) > 1 else bancos_query 
        promotoras = tuple(promotoras_query.split(',')) if len(promotoras_query.split(',')) > 1 else promotoras_query 
        corretores = tuple(corretores_query.split(',')) if len(corretores_query.split(',')) > 1 else corretores_query 
        operacoes = tuple(operacoes_query.split(',')) if len(operacoes_query.split(',')) > 1 else operacoes_query 

        user = User.objects.get(id=user_id)

        if user.is_superuser:
            FILTER_USER_ID = ""
        else:
            FILTER_USER_ID = f"""AND pc.user_id_created = {user_id}""" if user_id else ""

        try:        
            
            pre_contratos_repository = PreContratosRepository()
            pre_contratos = pre_contratos_repository.get_pre_contratos(dt_inicio, dt_final, convenios, bancos, promotoras, corretores, operacoes, has_contrato, FILTER_USER_ID)

            etl = EtlApuracaoPreContratos()
            data = etl.execute(pre_contratos)

            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):            
       
        try:
            user_id = request.GET.get("user_id", "")
            pre_contrato = PreContrato.objects.get(id=pk)

            user = User.objects.get(id=user_id)            

            if user.is_superuser == False:
                if user_id and pre_contrato:
                    if int(pre_contrato.user_id_created) != int(user_id):
                        serializer = PreContratoMS(pre_contrato)
                        return Response(data={"message": 'Não permitido'}, status=status.HTTP_401_UNAUTHORIZED)            

            serializer = PreContratoMS(pre_contrato)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        try:
            serializer = PreContratoMS(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):       

        try:
            pre_contratos = PreContrato.objects.get(id=pk)
            serializer = PreContratoMS(instance=pre_contratos, data=request.data)

            if serializer.is_valid():
                serializer.save()

                return Response(data=serializer.data, status=status.HTTP_200_OK)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):

        id = request.GET.get("id")

        try:
            pre_contratos = PreContrato.objects.get(id=id)
            pre_contratos.delete()

            return Response(status=status.HTTP_200_OK)

        except Exception as error:
            print("Error: ", error)
            return Response(data={'success': False, 'message': str(error)}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'], url_path="send-to-contrato")
    def send_to_contrato(self, request): 

        data = request.data    
        contrato = Contrato.objects.filter(id_pre_contrato=data['id_pre_contrato']).first()  

        if contrato:
            return Response(data={'message': 'já transmitido'},status=status.HTTP_409_CONFLICT)
        
        try:    

            with transaction.atomic():
                pre_contrato = PreContrato.objects.filter(id=request.data['id']).first()

                if pre_contrato:
                    pre_contrato.contrato_criado = True
                    pre_contrato.save()

                serializer = ContratoMS(data=data)
            
                if serializer.is_valid():
                    serializer.save() 
                    return Response(data=serializer.data, status=status.HTTP_201_CREATED)       
                else:
                    print("Serializer is not valid. Errors:", serializer.errors)
                    return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as err:
            print("ERROR>>>", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)  