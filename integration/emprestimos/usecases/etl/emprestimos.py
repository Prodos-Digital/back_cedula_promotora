import pandas as pd


class EtlEmprestimos():

    def empty_object(self):
        return {
                    'data': [],
                    'indicadores': {
                        "vl_emprestimo": 0,
                        "vl_capital_giro": 0,    
                        "vl_tt_juros": 0,    
                        "vl_tt_juros_a": 0,    
                        "vl_tt_juros_b": 0,    
                        "vl_capital_giro_corrente": 0,    
                        "qtd_emprestimos": {
                            'total': 0,
                            'acordo': 0,
                            'andamento': 0,
                            'quitado':0,
                    },                         
                    }
                }

    def execute(self, data):       

        df = pd.DataFrame.from_dict(data)
        pd.set_option('display.expand_frame_repr', False)    

        if df.empty: 
             return self.empty_object() 
        
        def contar_parcelas(parcelas):
            pagas = sum(1 for parcela in parcelas if parcela['status_pagamento'] == 'pago' and parcela['tp_pagamento'] == 'parcela')
            nao_pagas = sum(1 for parcela in parcelas if parcela['status_pagamento'] == 'pendente' or parcela['status_pagamento'] == 'pago_parcial')
            return pd.Series([pagas, nao_pagas])
        
        def dividir_juros(valor):
            return valor / 2 if valor != 0 else 0
        
        df["vl_emprestimo"] = df["vl_emprestimo"].astype(float)
        df["vl_capital_giro"] = df["vl_capital_giro"].astype(float)   
        df["vl_juros"] = df["vl_juros"].astype(float)    

        df["vl_juros_a"] = df["vl_juros"].apply(dividir_juros)
        df["vl_juros_b"] = df["vl_juros"].apply(dividir_juros)
        

        status_filtro = ['acordo', 'quitado', 'andamento']
        filtered_df = df[df['status'].isin(status_filtro)]
        contagem_por_status = filtered_df.groupby('status').size()
        contagem_por_status_dict = contagem_por_status.to_dict()     

        
        df[['parcelas_pagas', 'parcelas_nao_pagas']] = df['parcelas'].apply(contar_parcelas)
        df['capital_giro_corrente'] = df.apply(lambda row: round(row['vl_capital_giro'] * row['parcelas_nao_pagas'], 2) if row['parcelas_nao_pagas'] > 0 else 0, axis=1)
        print(df[['vl_capital_giro','parcelas_pagas','parcelas_nao_pagas','capital_giro_corrente']])    
        #breakpoint()

        return {
                'data': df.to_dict('records'),
                'indicadores': {
                    "vl_emprestimo": df["vl_emprestimo"].sum(),
                    "vl_capital_giro": df["vl_capital_giro"].sum(),    
                    "vl_tt_juros": df["vl_juros"].sum(),    
                    "vl_tt_juros_a": df["vl_juros_a"].sum(),    
                    "vl_tt_juros_b": df["vl_juros_b"].sum(),    
                    "vl_capital_giro_corrente": df["capital_giro_corrente"].sum(),    
                    "qtd_emprestimos": {
                        'total': df["id"].count(),
                        'acordo': contagem_por_status_dict.get('acordo', 0),
                        'andamento': contagem_por_status_dict.get('andamento', 0),
                        'quitado': contagem_por_status_dict.get('quitado', 0),
                    },              
                }
            }

if __name__ == '__main__':
    from integration.emprestimos.usecases.etl.emprestimos import EtlEmprestimos
    etl = EtlEmprestimos()    
    #etl.execute(data) #Popular o execute com o data
    etl.execute()
