from django.db import connection
from integration.helpers.utils import dictfetchall

class ParcelasAcordoRepository():

    def get_acordos_parcelas(self, dt_inicio=None, dt_final=None, tipo_parcela=None):    

        QUERY_FILTER = ''
        
        if tipo_parcela == 'pendentes':
            QUERY_FILTER = f"""
            		eep.dt_vencimento BETWEEN '{dt_inicio}' AND '{dt_final}' AND (eep.status_pagamento = 'pendente' OR eep.status_pagamento = 'pago_parcial')
				    OR (eep.dt_vencimento < '{dt_inicio}' AND (eep.status_pagamento = 'pendente' OR eep.status_pagamento = 'pago_parcial'))
                    """
        elif tipo_parcela == 'pagos':
            QUERY_FILTER = f"""
					eep.dt_vencimento BETWEEN '{dt_inicio}' AND '{dt_final}' AND eep.status_pagamento = 'pago'
				    """        

        elif tipo_parcela == 'todos':
            QUERY_FILTER = f"""
                    eep.dt_vencimento BETWEEN '{dt_inicio}' AND '{dt_final}'
                    """

        SQL = f"""
            SELECT
                DISTINCT ON (eep.acordo_id) eep.*, ea.nome
            FROM
                emp_acordo_parcelas eep
             LEFT JOIN
			    emp_acordos ea 
			    ON eep.acordo_id = ea.id
            WHERE
                {QUERY_FILTER} 
            ORDER BY
                eep.acordo_id,
                eep.nr_parcela DESC;
        """
        
        print(SQL)

        with connection.cursor() as cursor:   
            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []
