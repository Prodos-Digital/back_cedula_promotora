from django.db import connection
from integration.helpers.utils import dictfetchall

class PreContratosRepository():

    def get_pre_contratos(self, dt_inicio=None, dt_final=None, convenios=None, bancos=None, promotoras=None, corretores=None, operacoes=None, has_contrato=None, FILTER_USER_ID=None):       

        CONVENIOS_QUERY = f"""AND pc.convenio IN {convenios}""" if type(convenios) == tuple else f"""AND pc.convenio = '{convenios}' """ if convenios  else ""
        BANCOS_QUERY = f"""AND pc.banco IN {bancos}""" if type(bancos) == tuple else f"""AND pc.banco = '{bancos}' """ if bancos  else ""
        CORRETORES_QUERY = f"""AND pc.corretor IN {corretores}""" if type(corretores) == tuple else f"""AND pc.corretor = '{corretores}' """ if corretores  else ""
        PROMOTORAS_QUERY = f"""AND pc.promotora IN {promotoras}""" if type(promotoras) == tuple else f"""AND pc.promotora = '{promotoras}' """ if promotoras  else ""
        OPERACOES_QUERY = f"""AND pc.operacao IN {operacoes}""" if type(operacoes) == tuple else f"""AND pc.operacao = '{operacoes}' """ if operacoes  else ""
        
        if has_contrato == 'nao_transmitidos':
            FILTER_HAS_CONTRATO = " AND pc.contrato_criado = FALSE"
        elif has_contrato == 'transmitidos':
            FILTER_HAS_CONTRATO = " AND pc.contrato_criado = TRUE"
        else:
            FILTER_HAS_CONTRATO = ""

        SQL = f"""
                        SELECT pc.*, 
                            b.name AS "nome_banco", 
                            p.name AS "nome_promotora", 
                            c.name AS "nome_convenio",
                            co.name AS "nome_corretor",
                            o.name AS "nome_operacao"
                        FROM pre_contratos pc 
                        LEFT JOIN bancos b ON pc.banco::INTEGER = b.id
                        LEFT JOIN promotoras p ON pc.promotora::INTEGER = p.id
                        LEFT JOIN convenios c ON pc.convenio::INTEGER = c.id
                        LEFT JOIN corretores co ON pc.corretor ::INTEGER = co.id
                        LEFT JOIN operacoes o ON pc.operacao::INTEGER = o.id
                        WHERE pc.dt_pag_cliente BETWEEN '{dt_inicio}' AND '{dt_final}'
                        {CONVENIOS_QUERY}
                        {BANCOS_QUERY}
                        {CORRETORES_QUERY}
                        {PROMOTORAS_QUERY}
                        {OPERACOES_QUERY}
                        {FILTER_HAS_CONTRATO}
                        {FILTER_USER_ID}
                        ORDER BY pc.dt_pag_cliente DESC;
        """       

        #print(SQL)

        with connection.cursor() as cursor:   

            cursor.execute(SQL)
            data = dictfetchall(cursor)

        return data if data else []
    