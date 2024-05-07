from django.db import connection
from integration.helpers.utils import dictfetchall

class DespesasRepository():

    def get_despesas(self, dt_inicio=None, dt_final=None): 

        SQL = f"""           
            SELECT
                cd.*, cl.sg_loja
            FROM
                core_despesa cd
            LEFT JOIN core_lojas cl 
            ON
                cd.id_loja = cl.id
            WHERE cd.dt_vencimento BETWEEN '{dt_inicio}' AND '{dt_final}' 
            ORDER BY
                dt_vencimento desc;
        """       

        #print(SQL)

        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []
  