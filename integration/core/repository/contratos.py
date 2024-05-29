from django.db import connection
from integration.helpers.utils import dictfetchall

class ContratosRepository():

    def dashboard_contratos(self, dt_inicio=None, dt_final=None, convenios=None, bancos=None, promotoras=None, corretores=None, operacoes=None):       

        CONVENIOS_QUERY = f"""AND cc.convenio IN {convenios}""" if type(convenios) == tuple else f"""AND cc.convenio = '{convenios}' """ if convenios  else ""
        BANCOS_QUERY = f"""AND cc.banco IN {bancos}""" if type(bancos) == tuple else f"""AND cc.banco = '{bancos}' """ if bancos  else ""
        CORRETORES_QUERY = f"""AND cc.corretor IN {corretores}""" if type(corretores) == tuple else f"""AND cc.corretor = '{corretores}' """ if corretores  else ""
        PROMOTORAS_QUERY = f"""AND cc.promotora IN {promotoras}""" if type(promotoras) == tuple else f"""AND cc.promotora = '{promotoras}' """ if promotoras  else ""
        OPERACOES_QUERY = f"""AND cc.operacao IN {operacoes}""" if type(operacoes) == tuple else f"""AND cc.operacao = '{operacoes}' """ if operacoes  else ""
        
        SQL = f"""
            SELECT
                cc.*,
                b.name AS "nome_banco",
                p.name AS "nome_promotora",
                c.name AS "nome_convenio",
                co.name AS "nome_corretor",
                o.name AS "nome_operacao"
            FROM
                core_contrato cc
            LEFT JOIN bancos b ON
                cc.banco::VARCHAR = b.id::VARCHAR
            LEFT JOIN promotoras p ON
                cc.promotora::VARCHAR = p.id::VARCHAR
            LEFT JOIN convenios c ON
                cc.convenio::VARCHAR = c.id::VARCHAR
            LEFT JOIN corretores co ON
                cc.corretor ::VARCHAR = co.id::VARCHAR
            LEFT JOIN operacoes o ON
                cc.operacao::VARCHAR = o.id::VARCHAR
            WHERE cc.dt_pag_cliente BETWEEN '{dt_inicio}' AND '{dt_final}' 
            {CONVENIOS_QUERY}
            {BANCOS_QUERY}
            {CORRETORES_QUERY}
            {PROMOTORAS_QUERY}
            {OPERACOES_QUERY}
            ORDER BY dt_pag_cliente DESC;
        """       

        #print(SQL)

        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []
    