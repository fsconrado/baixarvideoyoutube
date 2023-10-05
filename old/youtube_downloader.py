import json
import re
import requests
from pytube import YouTube
import os


class YouTubeDownloader:
    def __init__(self, modo, url_playlist=''):
        self.modo = modo
        self.url_playlist = url_playlist
        self.nome_arquivo = 'source_code.txt'
        self.caminho_raiz = os.path.dirname(os.path.abspath(__file__))
        self.pasta_music = os.path.join(self.caminho_raiz, 'music')
        if not os.path.exists(self.pasta_music):
            os.makedirs(self.pasta_music)
        self.caminho_arquivo = f'{self.caminho_raiz}/{self.nome_arquivo}'
        self.chave_busca = 'videoIds'
        self.titulo = self.encontra_titulo_da_playlist(self.caminho_arquivo)
        self.caminho_para_salvar_videos = f"{self.titulo}/"
        print('Caminho para salvar vídeos', self.caminho_para_salvar_videos)

    def baixar_codigo_fonte(self, url, nome_arquivo):
        response = requests.get(url)
        conteudo = response.text

        with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
            arquivo.write(conteudo)

    def encontra_titulo_da_playlist(self, arquivo_texto):
        with open(arquivo_texto, 'r', encoding='utf-8') as f:
            texto = f.read()

        pattern = r'<meta property="og:title" content="(.*?)">'
        match = re.search(pattern, texto, re.I | re.S)

        if match:
            return match.group(1)
        else:
            raise Exception("A tag <meta property='og:title' não foi encontrada no arquivo de texto.")

    def buscar_video_ids(self, caminho_arquivo):
        itens_encontrados = []

        with open(caminho_arquivo, 'r') as arquivo:
            conteudo = arquivo.read()
            padroes_json = re.findall(r'{.*?}', conteudo)

            for padrao in padroes_json:
                try:
                    objeto_json = json.loads(padrao)
                    if self.chave_busca in objeto_json.keys():
                        if objeto_json[self.chave_busca] not in itens_encontrados:
                            itens_encontrados.append(objeto_json[self.chave_busca][0])
                except json.JSONDecodeError:
                    pass

        return itens_encontrados

    def baixar_url_playlist(self):
        self.baixar_codigo_fonte(self.url_playlist, self.nome_arquivo)
        itens_encontrados = self.buscar_video_ids(self.caminho_arquivo)

        for item in itens_encontrados:
            link_playlist = f'https://www.youtube.com/watch?v={item}'
            print('LINK_VIDEO', link_playlist)
            yt = YouTube(link_playlist)
            yt.from_id(item).streams.filter(progressive=True, file_extension='mp4').order_by(
                'resolution').desc().first().download(output_path=self.caminho_para_salvar_videos)

        self.apagar_arquivo_temp_source_code()

    def baixar_url_individual(self, link: str):
        link_video = link
        yt = YouTube(link_video)
        ys = yt.streams.get_highest_resolution()
        ys.download(self.pasta_music)

    def apagar_arquivo_temp_source_code(self):
        if os.path.exists(self.caminho_arquivo):
            os.remove(self.caminho_arquivo)
