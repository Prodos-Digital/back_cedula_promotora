from django.db import connection
from integration.helpers.utils import dictfetchall

class ParcelasEmprestimosRepository():

    def get_emprestimos_parcelas(self, dt_inicio=None, dt_final=None, tipo_parcela=None):    

        QUERY_FILTER = ''
        
        if tipo_parcela == 'pendentes':
            QUERY_FILTER = f"""
            		eep.dt_vencimento BETWEEN '{dt_inicio}' AND '{dt_final}' AND (eep.status_pagamento = 'pendente' AND eep.tp_pagamento <> 'acordo' OR eep.status_pagamento = 'pago_parcial')
				    OR (eep.dt_vencimento < '{dt_inicio}' AND (eep.status_pagamento = 'pendente' AND eep.tp_pagamento <> 'acordo' OR eep.status_pagamento = 'pago_parcial'))
                    """
        elif tipo_parcela == 'pagos':
            QUERY_FILTER = f"""
					eep.dt_vencimento BETWEEN '{dt_inicio}' AND '{dt_final}' AND eep.status_pagamento = 'pago' AND tp_pagamento <> 'juros' AND eep.tp_pagamento <> 'acordo'
				    """        
        elif tipo_parcela == 'juros':
            QUERY_FILTER = f"""
            		eep.dt_vencimento BETWEEN '{dt_inicio}' AND '{dt_final}' AND tp_pagamento = 'juros'
            		"""
        elif tipo_parcela == 'todos':
            QUERY_FILTER = f"""
                    eep.dt_vencimento BETWEEN '{dt_inicio}' AND '{dt_final}' AND eep.tp_pagamento <> 'acordo'
                    """

        SQL = f"""
            SELECT
                DISTINCT ON (eep.emprestimo_id) eep.*
            FROM
                emp_emprestimo_parcelas eep
            WHERE
                {QUERY_FILTER} 
            ORDER BY
                eep.emprestimo_id,
                eep.nr_parcela DESC;
        """
        
        print(SQL)

        with connection.cursor() as cursor:   
            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []
