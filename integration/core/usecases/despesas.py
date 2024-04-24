
import pandas as pd


class DashboardDespesas():

    def empty_object(self):
        return {
            'indicadores': {
                'despesas': [],                
            },         
        }

    def execute(self, data):       

        '''
            TOTALIZADORES DE RECEITAS E DESPESAS
        '''

        df = pd.DataFrame.from_dict(data)
        pd.set_option('display.expand_frame_repr', False)    

        if df.empty: 
             return self.empty_object() 
        
        df["valor"] = df["valor"].astype(float) 

        df['dt_vencimento_datetime'] = pd.to_datetime(df['dt_vencimento'])
        df['ano'] = df['dt_vencimento_datetime'].dt.year
        df['mes'] = df['dt_vencimento_datetime'].dt.month      

        df['nome_mes'] = df['dt_vencimento_datetime'].dt.strftime('%B')

        df['ano_mes'] = df['ano'].astype(str) + "-" +  df['mes'].astype(str).str.zfill(2) 

        ano_mes = df.groupby(['ano_mes'], as_index=False)['valor'].agg(['count','sum']).rename(columns={'count': 'qtd', 'sum': 'vlr_total'}).sort_values(by=['qtd'], ascending=False).reset_index()

        #Totalizadores NATUREZA DAS DEPESAS
        natureza_despesa = df.groupby(['natureza_despesa'], as_index=False)['valor'].agg(['sum','count']).rename(columns={'sum':'vlr_total', 'count': 'qtd'}).sort_values(by=['qtd'], ascending=False).reset_index()
        natureza_despesa['perc_qtd'] = round(natureza_despesa['qtd']/natureza_despesa['qtd'].sum() * 100,2)
        tt_natureza_despesa = natureza_despesa.to_dict('records')

        #Totalizadores TIPO DAS DEPESAS
        tipo_despesas = df.groupby(['tp_despesa'], as_index=False)['valor'].agg(['sum','count']).rename(columns={'sum':'vlr_total', 'count': 'qtd'}).sort_values(by=['qtd'], ascending=False).reset_index()
        tipo_despesas['perc_qtd'] = round(tipo_despesas['qtd']/tipo_despesas['qtd'].sum() * 100,2)
        tt_tipo_despesas = tipo_despesas.to_dict('records')

        #Totalizadores DESCRIÇÃO DAS DESPESAS
        descricao = df.groupby(['descricao'], as_index=False)['valor'].agg(['sum','count']).rename(columns={'sum':'vlr_total', 'count': 'qtd'}).sort_values(by=['qtd'], ascending=False).reset_index()
        descricao['perc_qtd'] = round(descricao['qtd']/descricao['qtd'].sum() * 100,2)
        tt_descricao = descricao.to_dict('records')

        #Totalizadores TIPO LOJA
        tipo_loja = df.groupby(['tipo_loja'], as_index=False)['valor'].agg(['sum','count']).rename(columns={'sum':'vlr_total', 'count': 'qtd'}).sort_values(by=['qtd'], ascending=False).reset_index()
        tipo_loja['perc_qtd'] = round(tipo_loja['qtd']/tipo_loja['qtd'].sum() * 100,2)
        tt_tipo_loja = tipo_loja.to_dict('records')

        #Totalizadores TIPO LOJA
        ano_mes = df.groupby(['ano_mes'], as_index=False)['valor'].agg(['sum','count']).rename(columns={'sum':'vlr_total', 'count': 'qtd'}).sort_values(by=['qtd'], ascending=False).reset_index()
        ano_mes['perc_qtd'] = round(ano_mes['qtd']/ano_mes['qtd'].sum() * 100,2)
        tt_ano_mes = ano_mes.to_dict('records')

        #breakpoint()

        return {
            'indicadores': {
                'despesas': {
                    'ano_mes': tt_ano_mes,
                    'naturezas': tt_natureza_despesa,
                    'tipo_despesas': tt_tipo_despesas,
                    'descricoes': tt_descricao,
                    'tipo_loja': tt_tipo_loja
                },  
            }, 
            'data': data           
        }

if __name__ == '__main__':
    from integration.core.usecases.despesas import DashboardDespesas
    etl = DashboardDespesas()    
    #etl.execute(data) #Popular o execute com o data
    etl.execute()
