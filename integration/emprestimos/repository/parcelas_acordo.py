from django.db import connection
from integration.helpers.utils import dictfetchall

class ParcelasAcordoRepository():

    def get_acordos_parcelas(self, dt_inicio=None, dt_final=None, tipo_parcela=None):    

        QUERY_FILTER = ''
        
        if tipo_parcela == 'pendentes':
            QUERY_FILTER = f"""
                    AND (eep.status_pagamento = 'pendente' OR eep.status_pagamento = 'pago_parcial')
                    AND eep.acordo_id NOT IN (SELECT acordo_id FROM parcelas_em_atraso))
                    OR (eep.dt_vencimento < '{dt_inicio}' AND (eep.status_pagamento = 'pendente' OR eep.status_pagamento = 'pago_parcial')
                    """
        elif tipo_parcela == 'pagos':
            QUERY_FILTER = f"""
					AND eep.status_pagamento = 'pago'
				    """        
    
        SQL = f"""
                DROP TABLE IF EXISTS temp_cobrancas_acordos;

                CREATE TEMP TABLE temp_cobrancas_acordos AS 
                    WITH parcelas_em_atraso AS (
                        SELECT DISTINCT acordo_id
                        FROM emp_acordo_parcelas
                        WHERE dt_vencimento < '{dt_inicio}'
                        AND (status_pagamento = 'pendente' OR status_pagamento = 'pago_parcial')
                    )
                    SELECT
                        distinct on(eep.acordo_id)  
                        eep.acordo_id,
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
                        CASE
                            WHEN eep.dt_vencimento = current_date THEN 2    
                            WHEN eep.dt_vencimento < current_date THEN 1
                            WHEN eep.dt_vencimento > current_date THEN 3
                        END AS situacao_prazo
                    FROM
                        emp_acordo_parcelas eep
                    LEFT JOIN
                        emp_acordos ee ON eep.acordo_id = ee.id
                    WHERE
                        (eep.dt_vencimento BETWEEN '{dt_inicio}' AND '{dt_final}'
                        {QUERY_FILTER}                    
                        )
                    ORDER BY                    
                        eep.acordo_id,  
                        eep.nr_parcela DESC;

                SELECT *
				FROM temp_cobrancas_acordos
				ORDER BY situacao_prazo, dt_vencimento asc;
        """
        
        print(SQL)

        with connection.cursor() as cursor:   
            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []
