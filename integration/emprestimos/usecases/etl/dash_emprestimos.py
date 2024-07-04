import pandas as pd

class EtlDashEmprestimos():

    def empty_object(self):
        return {
                  'indicadores':{
                    'emprestimos': {
                        'total': 0,                        
                        'andamento': 0,
                        'acordo': 0,
                        'quitado': 0,  
                        'parcelas_pagas': 0,
                        'parcelas_nao_pagas': 0,
                        'vl_capital_giro': 0,
                        'vl_capital_giro_corrente': 0            
                    },
                    'acordos': {
                        'total': 0,                        
                        'andamento': 0,
                        'quitado': 0, 
                        'vl_capital_giro_corrente': 0                       
                    }
                }     
            }

    def execute(self, emprestimos, acordos):       

        df_emprestimos = pd.DataFrame.from_dict(emprestimos)
        df_acordos = pd.DataFrame.from_dict(acordos)
        pd.set_option('display.expand_frame_repr', False)    

        if df_emprestimos.empty: 
             return self.empty_object() 
        
        def contar_parcelas(parcelas):
            pagas = sum(1 for parcela in parcelas if parcela['status_pagamento'] == 'pago' and parcela['tp_pagamento'] == 'parcela')
            nao_pagas = sum(1 for parcela in parcelas if parcela['status_pagamento'] == 'pendente' or parcela['status_pagamento'] == 'pago_parcial')
            return pd.Series([pagas, nao_pagas])

        status_filtro = ['quitado', 'andamento', 'acordo']

        # CONTADORES DOS EMPRÉSTIMOS
        df_emprestimos["vl_emprestimo"] = df_emprestimos["vl_emprestimo"].astype(float)    
        df_emprestimos["vl_capital_giro"] = df_emprestimos["vl_capital_giro"].astype(float)
        df_emprestimos["vl_juros"] = df_emprestimos["vl_juros"].astype(float)
        df_emprestimos[['parcelas_pagas', 'parcelas_nao_pagas']] = df_emprestimos['parcelas'].apply(contar_parcelas)
        df_emprestimos['capital_giro_corrente'] = df_emprestimos.apply(lambda row: round(row['vl_capital_giro'] * row['parcelas_nao_pagas'], 2) if row['parcelas_nao_pagas'] > 0 else 0, axis=1)

        filtered_df_emprestimos = df_emprestimos[df_emprestimos['status'].isin(status_filtro)]
        contagem_por_status_emprestimos = filtered_df_emprestimos.groupby('status').size()
        contagem_por_status_emprestimos_dict = contagem_por_status_emprestimos.to_dict() 

        # CONTADORES DOS ACORDOS
        df_acordos["vl_emprestimo"] = df_acordos["vl_emprestimo"].astype(float)
        df_acordos["vl_juros_adicional"] = df_acordos["vl_juros_adicional"].astype(float)
        df_acordos["vl_cobrado"] = df_acordos["vl_emprestimo"] + df_acordos["vl_juros_adicional"]
        df_acordos[['parcelas_pagas', 'parcelas_nao_pagas']] = df_acordos['parcelas'].apply(contar_parcelas)
        df_acordos['capital_giro_corrente'] = df_acordos['vl_emprestimo'] + df_acordos['vl_juros_adicional'] 

        filtered_df_acordos = df_acordos[df_acordos['status'].isin(status_filtro)]
        contagem_por_status_acordos = filtered_df_acordos.groupby('status').size()
        contagem_por_status_acordos_dict = contagem_por_status_acordos.to_dict() 
   
        #breakpoint()

        # filtro por status        

        return {                             
                'indicadores':{
                    'emprestimos': {
                        'total': df_emprestimos["id"].count(),                        
                        'andamento': contagem_por_status_emprestimos_dict.get('andamento', 0),
                        'acordo': contagem_por_status_emprestimos_dict.get('acordo', 0),
                        'quitado': contagem_por_status_emprestimos_dict.get('quitado', 0),  
                        'parcelas_pagas': df_emprestimos["parcelas_pagas"].sum(),
                        'parcelas_nao_pagas': df_emprestimos["parcelas_nao_pagas"].sum(),
                        'vl_capital_giro': df_emprestimos["vl_capital_giro"].sum(),
                        'vl_capital_giro_corrente': df_emprestimos['capital_giro_corrente'].sum(),
                        'vl_emprestimo': df_emprestimos['vl_emprestimo'].sum(),
                        'vl_juros': df_emprestimos['vl_juros'].sum()           
                    },
                    'acordos': {
                        'total': df_acordos["id"].count(),                        
                        'andamento': contagem_por_status_acordos_dict.get('andamento', 0),
                        'quitado': contagem_por_status_acordos_dict.get('quitado', 0), 
                        'parcelas_pagas': df_acordos["parcelas_pagas"].sum(),
                        'parcelas_nao_pagas': df_acordos["parcelas_nao_pagas"].sum(),
                        'vl_capital_giro_corrente': df_acordos['capital_giro_corrente'].sum(),
                        'vl_emprestimo': df_acordos['vl_emprestimo'].sum(),   
                        'vl_juros_adicional': df_acordos['vl_juros_adicional'].sum(),                            
                    }
                }            
            }

if __name__ == '__main__':
    from integration.emprestimos.usecases.etl.dash_emprestimos import EtlDashEmprestimos
    etl = EtlDashEmprestimos()    
    #etl.execute(data) #Popular o execute com o data
    etl.execute()




