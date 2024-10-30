from django.db import connection
from integration.helpers.utils import dictfetchall

class ClientesRepository():

    def get_clientes(self, user_id=None):       

        QUERY_BY_USER = f"WHERE cc.created_by_user_id = {user_id} " if user_id else ""


        SQL = f"""           
                SELECT cc.*, 
				c.name AS "nome_convenio", 
				cac.name AS "nome_canal_aquisicao",
                umu.username
                FROM core_cliente cc 
                LEFT JOIN convenios c 
                ON cc.convenio::VARCHAR = c.id::VARCHAR  
                LEFT JOIN canal_aquisicao_clientes cac 
                ON cc.canal_aquisicao::VARCHAR = cac.id::VARCHAR
                LEFT JOIN users_module_user umu 
                ON cc.created_by_user_id = umu.id  
                {QUERY_BY_USER}
                ORDER BY cc.id DESC ;
            """      
        
        #print(SQL)

        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []
  