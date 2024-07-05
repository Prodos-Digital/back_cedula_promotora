import pandas as pd
import numpy as np


class EtlParcelasAcordos():

    def empty_object(self):
        return {
                    'data': [],
                    'indicadores': {
                        "vl_tt_juros_adicional": df["vl_juros_adicional"].sum(),
                        "vl_tt_capital_giro": df["vl_capital_giro"].sum(),    
                        "qtd_parcelas": df["id"].count(),
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
        
        df["vl_juros_adicional"] = df["vl_juros_adicional"].fillna(0).astype(float)
        df["vl_capital_giro"] = df["vl_capital_giro"].fillna(0).astype(float)
        
        # df[['parcelas_pagas', 'parcelas_nao_pagas']] = df['parcelas'].apply(contar_parcelas)
        # df['capital_giro_corrente'] = df.apply(lambda row: round(row['vl_capital_giro'] * row['parcelas_nao_pagas'], 2) if row['parcelas_nao_pagas'] > 0 else 0, axis=1)
        # #print(df[['vl_capital_giro','parcelas_pagas','parcelas_nao_pagas','capital_giro_corrente']])    
        # #breakpoint()

        df = df.replace([np.inf, -np.inf], np.nan).fillna(0)
        
        return {
                'data': df.to_dict('records'),
                'indicadores': {
                    "vl_tt_juros_adicional": df["vl_juros_adicional"].sum(),
                    "vl_tt_capital_giro": df["vl_capital_giro"].sum(),    
                    "qtd_parcelas": df["id"].count(),
                }
            }

if __name__ == '__main__':
    from integration.emprestimos.usecases.etl.emprestimos import EtlEmprestimos
    etl = EtlEmprestimos()    
    #etl.execute(data) #Popular o execute com o data
    etl.execute()
