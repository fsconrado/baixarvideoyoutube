import json
import re
from pytube import YouTube
import requests

url_playlist = 'https://www.youtube.com/playlist?list=PLsSJYwgcH6SNeDYsic6lyjLQbZHXUcghP'
url_unica = ''

MODO = 'PLAYLIST' #UNICA OU PLAYLIST

def baixar_codigo_fonte(url, nome_arquivo):
    response = requests.get(url)
    conteudo = response.text

    with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
        arquivo.write(conteudo)


def encontra_titulo_da_playlist(arquivo_texto):
    with open(arquivo_texto, 'r', encoding='utf-8') as f:
        texto = f.read()

    pattern = r'<meta property="og:title" content="(.*?)">'
    match = re.search(pattern, texto, re.I | re.S)

    if match:
        return match.group(1)
    else:
        raise "A tag <meta property='og:title' não foi encontrada no arquivo de texto."


def buscar_video_ids(caminho_arquivo, chave):
    # Lista para armazenar os itens encontrados
    itens_encontrados = []

    with open(caminho_arquivo, 'r') as arquivo:
        # Lê o conteúdo do arquivo
        conteudo = arquivo.read()

        # Procura por padrões de estruturas JSON no conteúdo do arquivo
        padroes_json = re.findall(r'{.*?}', conteudo)

        # Busca pela chave nos padrões de estruturas JSON encontrados
        for padrao in padroes_json:
            try:
                objeto_json = json.loads(padrao)
                if chave in objeto_json.keys():
                    # Verifica se o valor da chave já está na lista de itens encontrados
                    if objeto_json[chave] not in itens_encontrados:
                        # Adiciona o valor da chave à lista de itens encontrados
                        itens_encontrados.append(objeto_json[chave][0])
            except json.JSONDecodeError:
                pass

    # Retorna a lista de itens encontrados
    return itens_encontrados


NOME_ARQUIVO = 'source_code.txt'
CAMINHO_RAIZ = '/Users/fsconrado/PycharmProjects/baixarvideoyoutube'
CAMINHO_ARQUIVO = '{}/{}'.format(CAMINHO_RAIZ, NOME_ARQUIVO)
titulo = encontra_titulo_da_playlist(CAMINHO_ARQUIVO)
print('titulo', titulo)
CAMINHO_PARA_SALVAR_VIDEOS = "{}/".format(titulo)
print('CAMINHO_PARA_SALVAR_VIDEOS ', CAMINHO_PARA_SALVAR_VIDEOS)
CHAVE_BUSCA = 'videoIds'

baixar_codigo_fonte(url_playlist, 'source_code.txt')

itens_encontrados = buscar_video_ids(CAMINHO_ARQUIVO, CHAVE_BUSCA)

for item in itens_encontrados:
    link_video = 'https://www.youtube.com/watch?v={}'.format(item)
    print('LINK_VIDEO', link_video)
    yt = YouTube(link_video)
    yt.from_id(item)\
        .streams.\
        filter(progressive=True, file_extension='mp4')\
        .order_by('resolution')\
        .desc()\
        .first().\
        download(output_path=CAMINHO_PARA_SALVAR_VIDEOS)

