from django.db import connection
from integration.helpers.utils import dictfetchall

class ClientesRepository():

    def get_historico_cliente(self, cpf=None): 

        SQL = f"""           
                SELECT
                   *
                FROM
                    emp_emprestimos ee
                WHERE cpf = '{cpf}' 
                ORDER BY ee.dt_emprestimo DESC;
            """   
           
        
        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []
    
    def get_dados_cliente(self, cpf=None): 

        SQL = f"""           
                SELECT
                   *
                FROM
                    emp_emprestimos ee
                WHERE cpf = '{cpf}' 
                ORDER BY ee.dt_emprestimo DESC;
            """   
           
        
        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []
  