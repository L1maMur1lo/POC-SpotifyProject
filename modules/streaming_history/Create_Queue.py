import logging
import os

import numpy as np
import pandas as pd

from modules.shared.settings import settings
from modules.shared.defaults.Queue import Check_Item_Queue

class Create_Queue:

    def __init__(self):

        self.data_path = settings.DATA_PATH

    def execute(self):
        """
        Extrai as informações das musicas do historico
        do Spotify e cria uma fila para a verificação,
        tratamento e inserção dos dados.
        """

        cl_timestamp = 'ts'
        cl_track_uri = 'spotify_track_uri'
        cl_ms_played = 'ms_played'
        cl_offline = 'offline'
        cl_offline_ts = 'offline_timestamp'

        logging.info('Iniciando criação da fila')

        # Criando uma lista com todos arquivos da pasta
        files = [file for file in os.listdir(self.data_path) if file.endswith('.json')]

        # Percorrendo cada arquivo da pasta
        for file in files:
            dataframe = pd.read_json(f'{self.data_path}/{file}')

            # Selecionando somente as colunas desejadas
            columns = dataframe[
                [
                    cl_timestamp,
                    cl_track_uri,
                    cl_ms_played,
                    cl_offline,
                    cl_offline_ts,
                ]
            ]

            # Transformando valores nulos em 0 na coluna
            columns[cl_offline_ts] = columns[cl_offline_ts].replace(np.nan, 0)

            # Descartando linhas com valores vazios na coluna
            dataframe = columns.dropna(subset=[cl_track_uri])

            # Percorendo cada linha do arquivo
            for index, item in dataframe.iterrows():
                try:
                    # Validando dados com pydantic
                    valid_item = Check_Item_Queue(
                        track_uri=item[cl_track_uri],
                        ms_played=item[cl_ms_played],
                        ts=item[cl_timestamp],
                        offline=item[cl_offline],
                        offline_ts=item[cl_offline_ts],
                        source_file=file,
                        source_file_row=index
                    )

                    # Transformando dados em modelo
                    new_item = valid_item.model_dump()
                    print(new_item)

                    # CONTINUAR APARTIR DAQUI...
                    # OBS: Inserir os dados no banco

                except Exception:
                    raise Exception('Falha na criação do item')

if __name__ == '__main__':
    main = Create_Queue()
    main.execute()
