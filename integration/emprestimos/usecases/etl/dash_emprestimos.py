import pandas as pd


class EtlDashEmprestimos():

    def empty_object(self):
        return {
                    'data': [],
                    'indicadores': {
                        "vl_emprestimo": 0,
                        "vl_capital_giro": 0,
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
        
        # def contar_parcelas(parcelas):
        #     pagas = sum(1 for parcela in parcelas if parcela['status_pagamento'] == 'pago' and parcela['tp_pagamento'] == 'parcela')
        #     nao_pagas = sum(1 for parcela in parcelas if parcela['status_pagamento'] == 'pendente' or parcela['status_pagamento'] == 'pago_parcial')
            # return pd.Series([pagas, nao_pagas])
        
   
        #breakpoint()

        return {
                'data': df.to_dict('records')               
            }

if __name__ == '__main__':
    from integration.emprestimos.usecases.etl.dash_emprestimos import EtlDashEmprestimos
    etl = EtlDashEmprestimos()    
    #etl.execute(data) #Popular o execute com o data
    etl.execute()




