import pandas as pd
from datetime import datetime

from integration.core.models import Cliente


class CargaClientes():

    def get_cliente(self):
        caminho_arquivo = "./integration/clientes.csv"

        dados = pd.read_csv(caminho_arquivo)
        dados.fillna("", inplace=True)

        for indice, linha in dados.iterrows():

            linha['cpf'] = linha['cpf'].replace('.', '').replace('-', '')
            date = datetime.strptime(linha.pop('d/n'), "%d/%m/%Y")
            linha['dt_nascimento'] = datetime.strftime(date, "%Y-%m-%d")

            telefones = linha.pop('telefone').split('/')
            for i in range(3):
                linha[f'telefone{i+1}'] = telefones[i].replace("(", "").replace(")", "").replace("-", "") if i < len(telefones) else ""

            self.add_cliente(linha)

    def add_cliente(self, data):

        try:
            new_cliente = Cliente(**data)
            new_cliente.save()
        
        except Exception as err:
            print("ERROR>>>", err)
            print('cliente>>', data)

if __name__ == '__main__':
    from integration.carga_cliente import CargaClientes

    carga = CargaClientes()
    carga.get_cliente()
