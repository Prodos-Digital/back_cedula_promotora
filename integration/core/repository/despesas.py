from django.db import connection
from integration.helpers.utils import dictfetchall

class DespesasRepository():

    def get_despesas(self, dt_inicio=None, dt_final=None): 

        SQL = f"""           
            SELECT
                cd.*,
                cl.sg_loja, 
                nd.name AS "nome_natureza_despesa"
            FROM
                core_despesa cd
            LEFT JOIN core_lojas cl 
            ON
                cd.id_loja = cl.id
            LEFT JOIN natureza_despesas nd ON cd.natureza_despesa::VARCHAR = nd.id::VARCHAR   
            WHERE cd.dt_vencimento BETWEEN '{dt_inicio}' AND '{dt_final}' 
            ORDER BY
                dt_vencimento desc;
        """       

        #print(SQL)

        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []

    def get_comissoes(self, dt_inicio=None, dt_final=None): 

        SQL = f"""           
            SELECT
               *
            FROM
                core_contrato cc            
            WHERE cc.dt_pag_cliente BETWEEN '{dt_inicio}' AND '{dt_final}'           
            ORDER BY dt_pag_cliente DESC;
        """     

        print(SQL)

        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []    
    
  