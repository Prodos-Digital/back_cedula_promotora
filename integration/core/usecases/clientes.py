
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

        print(data)

        df = pd.DataFrame.from_dict(data)
        pd.set_option('display.expand_frame_repr', False)    

        if df.empty: 
             return self.empty_object() 
        
        tt_count_clientes = df[['id']].count()
        tt_count_clientes_sem_especies = df.loc[df['especie'].notna() & (df['especie'] != ''), 'id'].count()

        print('tt_count_clientes ',tt_count_clientes)
        print('tt_count_clientes_sem_especies ',tt_count_clientes_sem_especies)
        
        clientes = df.groupby(['especie'], as_index=False)['id'].agg(['count']).rename(columns={'count': 'qtd'}).sort_values(by=['qtd'], ascending=False).reset_index()
        clientes['perc_qtd'] = round(clientes['qtd']/clientes['qtd'].sum() * 100,2)
        tt_clientes = clientes.to_dict('records')
       
        #breakpoint()

        return {
            'indicadores': {
                'clientes': tt_clientes,
                'tt_clientes': {
                    'total': tt_count_clientes,
                    'sem_especie': tt_count_clientes_sem_especies
                }
            },            
        }

if __name__ == '__main__':
    from integration.core.usecases.clientes import DashboardClientes
    etl = DashboardClientes()    
    #etl.execute(data) #Popular o execute com o data
    etl.execute()
