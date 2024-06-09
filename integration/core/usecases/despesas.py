import pandas as pd

class DashboardDespesas():   

    def empty_object(self):
        return {
             'despesas': [],       
        }

    def execute(self, despesas, contratos, dt_inicio, dt_final):         

        '''
            TOTALIZADORES DE RECEITAS E DESPESAS
        '''        

        df_despesas = pd.DataFrame.from_dict(despesas)        
        df_contratos = pd.DataFrame.from_dict(contratos)        
        pd.set_option('display.expand_frame_repr', False) 

        if df_despesas.empty:
            df_despesas = pd.DataFrame(columns=['id','dt_vencimento','descricao','valor','situacao','tp_despesa','natureza_despesa','id_loja']) 

        if df_contratos.empty:
            df_contratos = pd.DataFrame(columns=['id','promotora','dt_digitacao','nr_contrato','no_cliente','cpf','convenio','operacao','banco','vl_contrato','qt_parcelas','vl_parcela','dt_pag_cliente','dt_pag_comissao','vl_comissao','porcentagem','corretor']) 
           
        if df_despesas.empty and df_contratos.empty: 
             return self.empty_object()       

        # Criando o range de meses
        range_meses = pd.DataFrame(pd.date_range(start=dt_inicio, end=dt_final, freq="M"), columns=['month_number'])
        range_meses['ano_mes'] = range_meses['month_number'].dt.strftime('%Y-%m')
        range_meses = range_meses.drop(columns=['month_number'])

        # Tratativas da tabela de despesas
        df_despesas["valor"] = df_despesas["valor"].astype(float) 
        df_despesas['dt_vencimento_datetime'] = pd.to_datetime(df_despesas['dt_vencimento'])
        df_despesas['ano'] = df_despesas['dt_vencimento_datetime'].dt.year
        df_despesas['mes'] = df_despesas['dt_vencimento_datetime'].dt.month 
        df_despesas['nome_mes'] = df_despesas['dt_vencimento_datetime'].dt.strftime('%B')
        df_despesas['ano_mes_despesas'] = df_despesas['ano'].astype(str) + "-" +  df_despesas['mes'].astype(str).str.zfill(2) 
        ano_mes_despesas = df_despesas[df_despesas['situacao'] == 'pago'].groupby(['ano_mes_despesas'], as_index=False)['valor'].agg(['count','sum']).rename(columns={'count': 'qtd_despesas', 'sum': 'vlr_total_despesas'}).sort_values(by=['qtd_despesas'], ascending=False).reset_index()

 
        # Totalizadores das comissões dos contratos
        df_contratos["vl_comissao"] = df_contratos["vl_comissao"].astype(float) 
        df_contratos['dt_pag_cliente_datetime'] = pd.to_datetime(df_contratos['dt_pag_cliente'])
        df_contratos['ano'] = df_contratos['dt_pag_cliente_datetime'].dt.year
        df_contratos['mes'] = df_contratos['dt_pag_cliente_datetime'].dt.month      
        df_contratos['nome_mes'] = df_contratos['dt_pag_cliente_datetime'].dt.strftime('%B')
        df_contratos['ano_mes_contratos'] = df_contratos['ano'].astype(str) + "-" +  df_contratos['mes'].astype(str).str.zfill(2) 
       
        ano_mes_contratos = df_contratos.groupby(['ano_mes_contratos'], as_index=False)['vl_comissao'].agg(['count','sum']).rename(columns={'count': 'qtd_comissao', 'sum': 'vlr_total_comissao'}).sort_values(by=['qtd_comissao'], ascending=False).reset_index()
        df_merged = pd.merge(ano_mes_despesas, ano_mes_contratos, left_on='ano_mes_despesas', right_on='ano_mes_contratos', how='outer')       

        replace_values = {'vlr_total_despesas': 0, 'qtd_despesas': 0, 'vlr_total_comissao': 0, 'qtd_comissao': 0}
        df_merged.fillna(value=replace_values, inplace=True)
        df_merged = df_merged.drop(columns=['index_x', 'index_y'])

        #df_merged['lucro_despesa_total_mensal'] = df_merged['vlr_total_comissao'] - df_merged['vlr_total_despesas']

        #df_merged_despesas = df_merged.groupby(['ano_mes_despesas'], as_index=False)['lucro_despesa_total_mensal'].agg(['sum']).rename(columns={'sum': 'vlr_total'}).sort_values(by=['vlr_total'], ascending=False).reset_index()
        #df_merged_contratos = df_merged.groupby(['ano_mes_contratos'], as_index=False)['lucro_despesa_total_mensal'].agg(['sum']).rename(columns={'sum': 'vlr_total'}).sort_values(by=['vlr_total'], ascending=False).reset_index()
        df_merged_despesas = df_merged.groupby(['ano_mes_despesas'], as_index=False)['vlr_total_despesas'].sum().rename(columns={'vlr_total_despesas': 'vlr_total_despesas'}).sort_values(by=['ano_mes_despesas'])
        df_merged_contratos = df_merged.groupby(['ano_mes_contratos'], as_index=False)['vlr_total_comissao'].sum().rename(columns={'vlr_total_comissao': 'vlr_total_comissao'}).sort_values(by=['ano_mes_contratos'])

        df_merged_despesas.rename(columns={'ano_mes_despesas': 'ano_mes'}, inplace=True)
        df_merged_contratos.rename(columns={'ano_mes_contratos': 'ano_mes'}, inplace=True)

        # Concatenar os DataFrames
        df_final = pd.concat([df_merged_despesas[['ano_mes', 'vlr_total_despesas']], df_merged_contratos[['ano_mes', 'vlr_total_comissao']]])        
        df_final.rename(columns={'ano_mes_despesas': 'ano_mes'}, inplace=True)
        df_final = df_final.groupby('ano_mes').agg({'vlr_total_despesas':'sum', 'vlr_total_comissao':'sum'}).reset_index()
        df_final = df_final.sort_values(by='ano_mes')
        df_final['vlr_total_despesas'].fillna(0, inplace=True)
        df_final['vlr_total_comissao'].fillna(0, inplace=True)


        meses_ptbr = {
            1: 'Janeiro',
            2: 'Fevereiro',
            3: 'Março',
            4: 'Abril',
            5: 'Maio',
            6: 'Junho',
            7: 'Julho',
            8: 'Agosto',
            9: 'Setembro',
            10: 'Outubro',
            11: 'Novembro',
            12: 'Dezembro'
        }

        df_final['nome_mes_ano'] = pd.to_datetime(df_final['ano_mes']).dt.month.map(meses_ptbr) + ' ' + pd.to_datetime(df_final['ano_mes']).dt.year.astype(str)

        df_completo = pd.merge(range_meses, df_final, on='ano_mes', how='left')        
        df_completo['vlr_total_despesas'].fillna(0, inplace=True)
        df_completo['vlr_total_comissao'].fillna(0, inplace=True) 
        df_completo['vlr_total_lucro'] = df_completo['vlr_total_comissao'] - df_completo['vlr_total_despesas']
        df_completo['nome_mes_ano'] = pd.to_datetime(df_completo['ano_mes']).dt.month.map(meses_ptbr) + ' ' + pd.to_datetime(df_completo['ano_mes']).dt.year.astype(str)
       
        #breakpoint()

        return {
            'despesas': df_completo.to_dict('records'),
        }

if __name__ == '__main__':
    from integration.core.usecases.despesas import DashboardDespesas
    etl = DashboardDespesas()    
    #etl.execute(data) #Popular o execute com o data
    etl.execute()


