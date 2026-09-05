import logging

from modules.shared.api.SpotifyAPI import SpotifyAPI
from modules.shared.database.models import ArtistsModel, MusicsModel
from modules.shared.database.services import add_data_music_artist, missing_tracks


class Search_for_Data:
    CHUNCK_SIZE = 50

    def __init__(self):
        self.spotify_api = SpotifyAPI()

    def execute(self):

        # Só tracks onde o tempo de execução supere 30seg.
        missing_ids = missing_tracks()

        if missing_ids is None:
            raise Exception('Não há ids para executar')

        # Loop (50 em 50, maximo de id's que da para consultar de uma só vez)
        for index in range(0, len(missing_ids), self.CHUNCK_SIZE):
            limit = index + self.CHUNCK_SIZE
            batch = missing_ids[index:limit]

            # Resposta da API
            response = self.spotify_api.get_several_tracks(batch)
            # Looop para cada musica
            for item in response['tracks']:
                artists = []
                artists_names = []
                # Loop para cada artista
                for artist in item['artists']:
                    artist_id = artist['id']
                    artist_name = artist['name']

                    # "Validando as informações"
                    artist_data = ArtistsModel(reference=artist_id, name=artist_name, profile_img_url='')

                    artists.append(artist_data)
                    artists_names.append(artist_name)

                # Imagem do album
                album_img_url = item['album']['images'][0]['url']

                duration = item['duration_ms']

                # "Validando as informações"
                music = MusicsModel(
                    reference=item['id'],
                    title=item['name'],
                    names=', '.join(artists_names),
                    duration_ms=duration,
                    album_img_url=album_img_url,
                )
                music.artists = artists

                if add_data_music_artist(music):
                    logging.info(f'{"-" * 100}')
                    logging.info(f'{item["name"]}')
                    logging.info('Nova musica adicionada a tabela')
                    logging.info(f'{"-" * 100}')

                else:
                    logging.info(f'{"-" * 100}')
                    logging.info(f'{item["name"]}')
                    logging.info('Não foi possivel adicionadr a musica na tabela')
                    logging.info(f'{"-" * 100}')


if __name__ == '__main__':
    logFileName = 'Search_for_Data.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s | %(module)s: %(message)s',
        encoding='utf-8',
        handlers=[logging.FileHandler(logFileName), logging.StreamHandler()],
    )

    main = Search_for_Data()
    main.execute()
