
import pandas as pd


class DashboardDespesas():

    def empty_object(self):
        return {
            'indicadores': {
                'despesas': [],                
            },         
        }

    def execute(self, despesas, contratos):       

        '''
            TOTALIZADORES DE RECEITAS E DESPESAS
        '''

        df_despesas = pd.DataFrame.from_dict(despesas)
        df_contratos = pd.DataFrame.from_dict(contratos)
        pd.set_option('display.expand_frame_repr', False)    

        if df_despesas.empty: 
             return self.empty_object() 
        
        df_despesas["valor"] = df_despesas["valor"].astype(float) 
        df_despesas['dt_vencimento_datetime'] = pd.to_datetime(df_despesas['dt_vencimento'])
        df_despesas['ano'] = df_despesas['dt_vencimento_datetime'].dt.year
        df_despesas['mes'] = df_despesas['dt_vencimento_datetime'].dt.month 
        df_despesas['nome_mes'] = df_despesas['dt_vencimento_datetime'].dt.strftime('%B')
        df_despesas['ano_mes_despesas'] = df_despesas['ano'].astype(str) + "-" +  df_despesas['mes'].astype(str).str.zfill(2) 
        ano_mes_despesas = df_despesas.groupby(['ano_mes_despesas'], as_index=False)['valor'].agg(['count','sum']).rename(columns={'count': 'qtd_despesas', 'sum': 'vlr_total_despesas'}).sort_values(by=['qtd_despesas'], ascending=False).reset_index()

        #Totalizadores NATUREZA DAS DEPESAS
        # natureza_despesa = df_despesas.groupby(['natureza_despesa'], as_index=False)['valor'].agg(['sum','count']).rename(columns={'sum':'vlr_total', 'count': 'qtd'}).sort_values(by=['qtd'], ascending=False).reset_index()
        # natureza_despesa['perc_qtd'] = round(natureza_despesa['qtd']/natureza_despesa['qtd'].sum() * 100,2)
        # tt_natureza_despesa = natureza_despesa.to_dict('records')

        # #Totalizadores TIPO DAS DEPESAS
        # tipo_despesas = df_despesas.groupby(['tp_despesa'], as_index=False)['valor'].agg(['sum','count']).rename(columns={'sum':'vlr_total', 'count': 'qtd'}).sort_values(by=['qtd'], ascending=False).reset_index()
        # tipo_despesas['perc_qtd'] = round(tipo_despesas['qtd']/tipo_despesas['qtd'].sum() * 100,2)
        # tt_tipo_despesas = tipo_despesas.to_dict('records')

        # #Totalizadores DESCRIÇÃO DAS DESPESAS
        # descricao = df_despesas.groupby(['descricao'], as_index=False)['valor'].agg(['sum','count']).rename(columns={'sum':'vlr_total', 'count': 'qtd'}).sort_values(by=['qtd'], ascending=False).reset_index()
        # descricao['perc_qtd'] = round(descricao['qtd']/descricao['qtd'].sum() * 100,2)
        # tt_descricao = descricao.to_dict('records')

        # #Totalizadores TIPO LOJA
        # tipo_loja = df_despesas.groupby(['tipo_loja'], as_index=False)['valor'].agg(['sum','count']).rename(columns={'sum':'vlr_total', 'count': 'qtd'}).sort_values(by=['qtd'], ascending=False).reset_index()
        # tipo_loja['perc_qtd'] = round(tipo_loja['qtd']/tipo_loja['qtd'].sum() * 100,2)
        # tt_tipo_loja = tipo_loja.to_dict('records')

        # #Totalizadores TIPO LOJA
        # ano_mes = df_despesas.groupby(['ano_mes'], as_index=False)['valor'].agg(['sum','count']).rename(columns={'sum':'vlr_total', 'count': 'qtd'}).sort_values(by=['qtd'], ascending=False).reset_index()
        # ano_mes['perc_qtd'] = round(ano_mes['qtd']/ano_mes['qtd'].sum() * 100,2)
        # tt_ano_mes = ano_mes.to_dict('records')


        #-----------------------------------------------------------------
        #Totalizadores das comissões
        df_contratos["vl_comissao"] = df_contratos["vl_comissao"].astype(float) 
        df_contratos['dt_pag_cliente_datetime'] = pd.to_datetime(df_contratos['dt_pag_cliente'])
        df_contratos['ano'] = df_contratos['dt_pag_cliente_datetime'].dt.year
        df_contratos['mes'] = df_contratos['dt_pag_cliente_datetime'].dt.month      
        df_contratos['nome_mes'] = df_contratos['dt_pag_cliente_datetime'].dt.strftime('%B')
        df_contratos['ano_mes_contratos'] = df_contratos['ano'].astype(str) + "-" +  df_contratos['mes'].astype(str).str.zfill(2) 
       
        ano_mes_contratos = df_contratos.groupby(['ano_mes_contratos'], as_index=False)['vl_comissao'].agg(['count','sum']).rename(columns={'count': 'qtd_comissao', 'sum': 'vlr_total_comissao'}).sort_values(by=['qtd_comissao'], ascending=False).reset_index()
        df_merged = pd.merge(ano_mes_despesas, ano_mes_contratos, left_on='ano_mes_despesas', right_on='ano_mes_contratos', how='outer')       

        replace_values = {'vlr_total_despesas': 0, 'qtd_despesas': 0, 'perc_qtd_despesas': 0, 'qtd_comissao': 0}
        df_merged.fillna(value=replace_values, inplace=True)
        df_merged = df_merged.drop(columns=['index_x', 'index_y'])

        
        breakpoint()

        return {
            'indicadores': {
                'despesas': {
                    # 'ano_mes': tt_ano_mes,
                    # 'naturezas': tt_natureza_despesa,
                    # 'tipo_despesas': tt_tipo_despesas,
                    # 'descricoes': tt_descricao,
                    # 'tipo_loja': tt_tipo_loja
                },  
            }, 
            'data': despesas           
        }

if __name__ == '__main__':
    from integration.core.usecases.despesas import DashboardDespesas
    etl = DashboardDespesas()    
    #etl.execute(data) #Popular o execute com o data
    etl.execute()
