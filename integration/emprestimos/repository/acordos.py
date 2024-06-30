from django.db import connection
from integration.helpers.utils import dictfetchall

class AcordosRepository():

    def get_acordos(self, dt_inicio=None, dt_final=None, dt_filter=None): 

        SQL = f"""           
                SELECT
                    ee.*,
                    (
                        SELECT json_agg(eep ORDER BY eep.dt_vencimento)
                        FROM emp_acordo_parcelas eep
                        WHERE eep.acordo_id = ee.id
                    ) AS parcelas
                FROM
                    emp_acordos ee
                WHERE ee.{dt_filter} BETWEEN '{dt_inicio}' AND '{dt_final}'
                ORDER BY ee.{dt_filter} DESC;
            """  
        
        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []
    
    def get_acordo_by_id(self, id=None): 

        SQL = f"""           
               SELECT
                    ee.*,
                    (
                        SELECT json_agg(eep ORDER BY eep.dt_vencimento)
                        FROM emp_acordo_parcelas eep
                        WHERE eep.acordo_id = ee.id
                    ) AS parcelas
                FROM
                    emp_acordos ee
                WHERE ee.id = '{id}';
            """              

        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data[0] if data else []
