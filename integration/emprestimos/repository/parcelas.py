from django.db import connection
from integration.helpers.utils import dictfetchall

class ParcelasEmprestimosRepository():

    def get_emprestimos_parcelas(self, dt_inicio=None, dt_final=None, tipo_parcela=None):    

        QUERY_FILTER = ''
        
        if tipo_parcela == 'pendentes':
            QUERY_FILTER = f"""
                    AND (eep.status_pagamento = 'pendente' AND eep.tp_pagamento <> 'acordo' OR eep.status_pagamento = 'pago_parcial')
                    AND eep.emprestimo_id NOT IN (SELECT emprestimo_id FROM parcelas_em_atraso))
                    OR (eep.dt_vencimento < '{dt_inicio}' AND (eep.status_pagamento = 'pendente' AND eep.tp_pagamento <> 'acordo' OR eep.status_pagamento = 'pago_parcial')
                    """
        elif tipo_parcela == 'pagos':
            QUERY_FILTER = f"""
					AND eep.status_pagamento = 'pago' AND tp_pagamento <> 'juros' AND eep.tp_pagamento <> 'acordo'
				    """        
        elif tipo_parcela == 'juros':
            QUERY_FILTER = f"""
            		AND tp_pagamento = 'juros'
            		"""
        elif tipo_parcela == 'todos':
            QUERY_FILTER = f"""
                    AND eep.tp_pagamento <> 'acordo'
                    """

        SQL = f"""   
                DROP TABLE IF EXISTS temp_cobrancas_emprestimos;

                CREATE TEMP TABLE temp_cobrancas_emprestimos AS 
                    WITH parcelas_em_atraso AS (
                        SELECT DISTINCT emprestimo_id
                        FROM emp_emprestimo_parcelas
                        WHERE dt_vencimento < '{dt_inicio}'
                        AND (status_pagamento = 'pendente' AND tp_pagamento <> 'acordo' OR status_pagamento = 'pago_parcial')
                    )
                    SELECT
                        distinct on(eep.emprestimo_id)  
                        eep.emprestimo_id,
                        eep.id,
                        eep.nr_parcela,
                        eep.dt_vencimento,
                        eep.dt_pagamento,
                        eep.tp_pagamento,
                        eep.status_pagamento,
                        eep.vl_parcial,
                        eep.vl_parcela,
                        eep.qtd_tt_parcelas,
                        eep.dt_prev_pag_parcial_restante,
                        eep.observacoes,
                        ee.nome,
                        ee.vl_juros,
                        ee.vl_capital_giro,
                        CASE
                            WHEN eep.dt_vencimento = current_date THEN 2    
                            WHEN eep.dt_vencimento < current_date THEN 1
                            WHEN eep.dt_vencimento > current_date THEN 3
                        END AS situacao_prazo
                    FROM
                        emp_emprestimo_parcelas eep
                    LEFT JOIN
                        emp_emprestimos ee ON eep.emprestimo_id = ee.id
                    WHERE
                        (eep.dt_vencimento BETWEEN '{dt_inicio}' AND '{dt_final}'
                        {QUERY_FILTER}                    
                        )
                    ORDER BY                    
                        eep.emprestimo_id,  
                        eep.nr_parcela DESC;

                SELECT *
				FROM temp_cobrancas_emprestimos
				ORDER BY situacao_prazo, dt_vencimento asc;
       
        """
        
        #print(SQL)

        with connection.cursor() as cursor:   
            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []
