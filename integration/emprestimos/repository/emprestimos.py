from django.db import connection
from integration.helpers.utils import dictfetchall

class EmprestimosRepository():

    def get_emprestimos(self, dt_inicio=None, dt_final=None, dt_filter=None, has_acordo=None): 

        QUERY_HAS_ACORDO = f"""AND ee.status <> 'acordo'""" if has_acordo == 'nao' else ""

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
                WHERE ee.{dt_filter} BETWEEN '{dt_inicio}' AND '{dt_final}' {QUERY_HAS_ACORDO}
                ORDER BY ee.{dt_filter} DESC;
            """  
        
        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []
    
    def get_emprestimo_by_id(self, id=None): 

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
                WHERE ee.id = '{id}';
            """              
        print(SQL)
        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data[0] if data else []


    def get_emprestimos_for_dashboard(self, dt_inicio=None, dt_final=None, dt_filter=None): 

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
                WHERE ee.{dt_filter} BETWEEN '{dt_inicio}' AND '{dt_final}';
            """  
        
        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []