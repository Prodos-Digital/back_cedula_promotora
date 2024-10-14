import pandas as pd

class EtlApuracaoPreContratos():   

    def empty_object(self):
        return {
             'indicadores': {
                 'valor_total': 0,
                 'qtd_total': 0,
                 'apuracao': [],
             },    
             'pre_contratos': []   
        }

    def execute(self, pre_contratos):         

        df_pre_contratos = pd.DataFrame.from_dict(pre_contratos)   
        pd.set_option('display.expand_frame_repr', False) 


        if df_pre_contratos.empty:
            return self.empty_object()  

        df_pre_contratos["vl_contrato"] = df_pre_contratos["vl_contrato"].astype(float)  

        corretores = df_pre_contratos.groupby(['nome_corretor'], as_index=False)['vl_contrato'].agg(['sum','count']).rename(columns={'sum':'vlr_total', 'count': 'qtd'}).sort_values(by=['vlr_total'], ascending=False).reset_index()
        corretores['perc_qtd'] = round(corretores['qtd']/corretores['qtd'].sum() * 100,2)  

        def get_grouped_data(df, group_by_col, target_col_label):
            grouped = df.groupby(group_by_col).agg(qtd=('vl_contrato', 'size'), vlr_total=('vl_contrato', 'sum')).reset_index()
            grouped.rename(columns={group_by_col: target_col_label}, inplace=True)
            grouped = grouped.sort_values(by=['vlr_total'], ascending=False)
            
            return grouped.to_dict('records')
        
        resultado_apurado = []
        valor_total_acumulado = 0.0
        qtd_total_acumulado = 0
        for _, corretor_row in corretores.iterrows():
            valor_total_acumulado = corretor_row['vlr_total']
            qtd_total_acumulado = corretor_row['qtd']

            corretor_data = {
                'corretor': corretor_row['nome_corretor'],
                'valor_total': round(valor_total_acumulado, 2),
                'qtd_total': qtd_total_acumulado,
                'bancos': get_grouped_data(df_pre_contratos[df_pre_contratos['nome_corretor'] == corretor_row['nome_corretor']], 'nome_banco', 'nome_banco'),
                'operacoes': get_grouped_data(df_pre_contratos[df_pre_contratos['nome_corretor'] == corretor_row['nome_corretor']], 'nome_operacao', 'nome_operacao'),
                'convenios': get_grouped_data(df_pre_contratos[df_pre_contratos['nome_corretor'] == corretor_row['nome_corretor']], 'nome_convenio', 'nome_convenio'),
                'promotoras': get_grouped_data(df_pre_contratos[df_pre_contratos['nome_corretor'] == corretor_row['nome_corretor']], 'nome_promotora', 'nome_promotora')
            }
            resultado_apurado.append(corretor_data)


        # breakpoint()

        return {
            "indicadores": {
                'valor_total': round(df_pre_contratos["vl_contrato"].sum(), 2),
                'qtd_total': df_pre_contratos['id'].count(),
                'apuracao': resultado_apurado,
            },
            "pre_contratos": df_pre_contratos.to_dict("records")
        }

if __name__ == '__main__':
    from integration.core.usecases.pre_contratos import EtlApuracaoPreContratos
    etl = EtlApuracaoPreContratos()    
    #etl.execute(data) #Popular o execute com o data
    etl.execute()
