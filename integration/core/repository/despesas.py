from django.db import connection
from integration.helpers.utils import dictfetchall

class DespesasRepository():

    def dashboard_despesas(self, dt_inicio=None, dt_final=None):      

                
        SQL = f"""
            SELECT * FROM core_despesa cc 
            WHERE cc.dt_vencimento BETWEEN '{dt_inicio}' AND '{dt_final}'            
            ORDER BY dt_vencimento DESC;
        """       

        #print(SQL)

        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []