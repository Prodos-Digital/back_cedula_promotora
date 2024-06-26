from django.db import connection
from integration.helpers.utils import dictfetchall

class ParcelasEmprestimosRepository():

    def get_emprestimos_parcelas(self, dt_inicio=None, dt_final=None, tipo_parcela=None): 

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
                WHERE ee.dt_cobranca BETWEEN '{dt_inicio}' AND '{dt_final}'
                AND ee.status <> 'acordo'
                ORDER BY ee.dt_cobranca DESC;
            """   
           
        
        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []
  