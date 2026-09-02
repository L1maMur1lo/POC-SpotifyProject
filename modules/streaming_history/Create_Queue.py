import logging
import os

import numpy as np
import pandas as pd

from modules.shared.database.services import add_queue_item
from modules.shared.defaults.Queue import Item_Queue
from modules.shared.settings import settings


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
            if 'processado' in file:
                continue

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

            # Variaveis de "controle"
            rows_sucess = 0
            rows_existing = 0
            rows_total = len(dataframe)

            # Percorendo cada linha do arquivo
            for index, item in dataframe.iterrows():
                try:
                    # Validando dados com pydantic
                    valid_item = Item_Queue(
                        track_uri=item[cl_track_uri],
                        ms_played=item[cl_ms_played],
                        ts=item[cl_timestamp],
                        offline=item[cl_offline],
                        offline_ts=item[cl_offline_ts],
                        source_file=file,
                        source_file_row=index + 1,
                    )
                except Exception:
                    raise Exception('Falha na validação do item')

                # logging.debug(valid_item)

                try:
                    if add_queue_item(valid_item):
                        # Log's de controle
                        logging.debug('Novo item adicionado a fila')
                        logging.debug(f'File:{file} Row: {index}, Total: {rows_total}')
                        rows_sucess += 1

                    else:
                        # Log's de controle
                        logging.debug('Item já existe na fila')
                        logging.debug(f'File:{file} Row: {index}, Total: {rows_total}')
                        rows_existing += 1

                except Exception:
                    logging.info('Não foi criar o item no banco')
                    logging.debug(f'File:{file} Row: {index}, Total: {rows_total}')

            # Log's de controle
            logging.info(f'{"-" * 100}')
            logging.info(f'Já existente: {rows_existing}')
            logging.info(f'Sucesso: {rows_sucess}')
            logging.info(f'Total: {rows_total}')

            # Renomeia o arquivo para em caso de falha, não processa-lo novamente
            os.rename(
                f'{self.data_path}/{file}',
                f'{self.data_path}/{file.replace(".json", "")}_processado.json',
            )

            logging.info(f'Arquivo: {file} processado!')
            logging.info(f'{"-" * 100}')


if __name__ == '__main__':
    logFileName = 'Create_Queue.log'

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s | %(module)s: %(message)s',
        encoding='utf-8',
        handlers=[logging.FileHandler(logFileName), logging.StreamHandler()],
    )

    main = Create_Queue()
    main.execute()
