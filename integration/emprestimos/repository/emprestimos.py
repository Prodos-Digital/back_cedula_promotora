from django.db import connection
from integration.helpers.utils import dictfetchall

class EmprestimosRepository():

    def get_emprestimos(self, dt_inicio=None, dt_final=None): 

        SQL = f"""           
            SELECT * FROM emp_emprestimos ee;
        """       

        print(SQL)

        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []
  