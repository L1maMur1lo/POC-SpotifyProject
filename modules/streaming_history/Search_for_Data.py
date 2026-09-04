import logging

from modules.shared.api.SpotifyAPI import SpotifyAPI
from modules.shared.defaults.Validator import ArtistVal, MusicVal


class Search_for_Data:
    CHUNCK_SIZE = 50

    def __init__(self):
        self.spotify_api = SpotifyAPI()

    def execute(self):

        # Só tracks onde o tempo de execução supere 30seg.
        missing_ids = []

        if missing_ids in None:
            return Exception('Não há ids para executar')

        # Loop (50 em 50, maximo de id's que da para consultar de uma só vez)
        for index in range(0, len(missing_ids), self.CHUNCK_SIZE):
            limit = index + self.CHUNCK_SIZE
            batch = missing_ids[index:limit]

            # Resposta da API
            response = self.spotify_api.get_several_tracks(batch)
            # Looop para cada musica
            for item in response['tracks']:
                artists_ids = []
                # Loop para cada artista
                for artist in item['artists']:
                    artist_id = artist['id']
                    artist_name = artist['name']

                    # "Validando as informações"
                    artist_data = ArtistVal(reference=artist_id, name=artist_name)

                artists_ids += [artist_data.reference]

                # Imagem do album
                album_img_url = item['album']['images'][0]['url']

                # "Validando as informações"
                music = MusicVal(
                    reference=item['id'],
                    title=item['name'],
                    artists=artists_ids,
                    duration_ms=item['duration_ms'],
                    album_img_url=album_img_url,
                )

                # CONTINUAR adicionando os dados da musica e do artista no banco
                print(music)


if __name__ == '__main__':
    logFileName = 'Search_for_Data.log'

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s | %(module)s: %(message)s',
        encoding='utf-8',
        handlers=[logging.FileHandler(logFileName), logging.StreamHandler()],
    )

    main = Search_for_Data()
    main.execute()
