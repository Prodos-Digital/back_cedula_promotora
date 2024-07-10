from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from integration.core.models import PreContrato, Contrato
from integration.users.models import User
from integration.core.serializer import PreContratoMS, PreContratoRelatorioMS, ContratoMS
from datetime import datetime, timedelta
from django.db import transaction

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

        user = User.objects.get(id=user_id)

        if user.is_superuser:
            FILTER_USER_ID = ""
        else:
            FILTER_USER_ID = f"""AND pc.user_id_created = {user_id}""" if user_id else ""

        if has_contrato == 'nao_transmitidos':
            FILTER_HAS_CONTRATO = " AND pc.contrato_criado = FALSE"
        elif has_contrato == 'transmitidos':
            FILTER_HAS_CONTRATO = " AND pc.contrato_criado = TRUE"
        else:
            FILTER_HAS_CONTRATO = ""

        try:        
            QUERY = f"""
                        SELECT pc.*, 
                            b.name AS "nome_banco", 
                            p.name AS "nome_promotora", 
                            c.name AS "nome_convenio",
                            co.name AS "nome_corretor",
                            o.name AS "nome_operacao"
                        FROM pre_contratos pc 
                        LEFT JOIN bancos b ON pc.banco::INTEGER = b.id
                        LEFT JOIN promotoras p ON pc.promotora::INTEGER = p.id
                        LEFT JOIN convenios c ON pc.convenio::INTEGER = c.id
                        LEFT JOIN corretores co ON pc.corretor ::INTEGER = co.id
                        LEFT JOIN operacoes o ON pc.operacao::INTEGER = o.id
                        WHERE pc.dt_pag_cliente BETWEEN '{dt_inicio}' AND '{dt_final}'
                        {FILTER_USER_ID}
                        {FILTER_HAS_CONTRATO}
                        ORDER BY pc.dt_pag_cliente DESC;
                    """    
            print(QUERY)           
            
            pre_contratos = PreContrato.objects.raw(QUERY)              
            serializer = PreContratoRelatorioMS(pre_contratos, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

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