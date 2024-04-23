
import pandas as pd


class DashboardClientes():

    def empty_object(self):
        return {
            'indicadores': {
                'clientes': [],
                'tt_clientes': {
                    'total': 0,
                    'sem_especie': 0
                }
            },         
        }

    def execute(self, data):       

        '''
            TOTALIZADOR DE CLIENTES AGRUPADOS POR ESPÉCIE DO INSS
        '''

        df = pd.DataFrame.from_dict(data)
        pd.set_option('display.expand_frame_repr', False)    

        if df.empty: 
             return self.empty_object() 
        
        
        tt_clientes_especies = df[['id']].count()
        tt_clientes_sem_especies = df.loc[df['especie'].notna() & (df['especie'] != ''), 'id'].count()

        # Remover as linhas onde a coluna 'especie' é nula ou vazia ("")
        df = df.dropna(subset=['especie'])
        df = df.drop(df[df['especie'] == ""].index)
        
        # Totalizar as espécies
        especies = df.groupby(['especie'], as_index=False)['id'].agg(['count']).rename(columns={'count': 'qtd'}).sort_values(by=['qtd'], ascending=False).reset_index()
        especies['perc_qtd'] = round(especies['qtd']/especies['qtd'].sum() * 100,2)
        tt_especies = especies.to_dict('records')
       
        #breakpoint()

        return {
            'indicadores': {
                'especies': tt_especies,
                'tt_especies': {
                    'total': tt_clientes_especies,
                    'sem_especie': tt_clientes_especies - tt_clientes_sem_especies
                }
            },            
        }

if __name__ == '__main__':
    from integration.core.usecases.clientes import DashboardClientes
    etl = DashboardClientes()    
    #etl.execute(data) #Popular o execute com o data
    etl.execute()
