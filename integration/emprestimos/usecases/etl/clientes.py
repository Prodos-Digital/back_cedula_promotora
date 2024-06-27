import pandas as pd


class HistoricoClienteEmprestimos():

    def empty_object(self):
        return {
                'data': [],   
                'dados_cliente': [],
                'indicadores': {
                     "qtd_tt_emprestimos": 0,
                      "tt_emprestimos": 0,
                    }                    
            }
            

    def execute(self, data, cliente):       

        df = pd.DataFrame.from_dict(data)
        pd.set_option('display.expand_frame_repr', False)    

        if df.empty: 
             return self.empty_object() 
        
        emprestimos = df.groupby(['status'], as_index=False)['status'].agg(['count']).rename(columns={'count': 'qtd'}).sort_values(by=['qtd'], ascending=False).reset_index()
        emprestimos['perc_qtd'] = round(emprestimos['qtd']/emprestimos['qtd'].sum() * 100,2)
        tt_emprestimos = emprestimos.to_dict('records')
        
        #breakpoint()

        return {
                'data': df.to_dict('records'),   
                'dados_cliente': cliente,
                'indicadores': {
                     "qtd_tt_emprestimos": df["id"].count(),
                      "tt_emprestimos": tt_emprestimos,
                }
            }

if __name__ == '__main__':
    from integration.emprestimos.usecases.etl.clientes import HistoricoClienteEmprestimos
    etl = HistoricoClienteEmprestimos()    
    #etl.execute(data) #Popular o execute com o data
    etl.execute()
