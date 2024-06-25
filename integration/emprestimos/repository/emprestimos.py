from django.db import connection
from integration.helpers.utils import dictfetchall

class EmprestimosRepository():

    def get_emprestimos(self, dt_inicio=None, dt_final=None, dt_filter=None): 

        SQL = f"""           
                SELECT
                    ee.*,
                    (
                        SELECT json_agg(eep ORDER BY eep.dt_vencimento)
                        FROM emp_emprestimo_parcelas eep
                        WHERE eep.emprestimo_id = ee.id
                    ) AS parcelas
                FROM
                    emp_emprestimos ee
                WHERE ee.{dt_filter} BETWEEN '{dt_inicio}' AND '{dt_final}'
                ORDER BY ee.{dt_filter} DESC;
            """   
           
        
        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []
  