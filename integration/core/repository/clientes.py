from django.db import connection
from integration.helpers.utils import dictfetchall

class ClientesRepository():

    def get_clientes(self):         

        SQL = f"""           
                SELECT cc.*, c.name AS "nome_convenio"
                FROM core_cliente cc 
                LEFT JOIN convenios c 
                ON cc.convenio::VARCHAR = c.id::VARCHAR                        
                ORDER BY cc.id DESC ;
            """      

        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []
  