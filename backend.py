"""
==================================
BACKEND - LÓGICA DO DOWNLOADER
==================================

Este arquivo contém toda a lógica de negócios para a aplicação de download
de imagens do Mercado Livre. Ele é responsável por se comunicar com a web,
analisar o conteúdo HTML e processar os arquivos de imagem.

Este módulo foi projetado para ser independente da interface do usuário (UI),
podendo ser importado e utilizado por qualquer front-end (Tkinter, web, etc.).

Funções principais:
- obter_links_de_imagens: Extrai as URLs de imagem de um anúncio.
- baixar_redimensionar_e_salvar: Baixa, filtra, redimensiona e salva as imagens.
"""

# --- Importações necessárias para o funcionamento do backend ---
import requests
from bs4 import BeautifulSoup
import os
from PIL import Image
from io import BytesIO

def obter_links_de_imagens(url_anuncio, status_callback):
    """
    Analisa uma página de anúncio do Mercado Livre e retorna uma lista com as
    URLs de todas as imagens principais na maior resolução disponível.

    Args:
        url_anuncio (str): O link completo do anúncio a ser analisado.
        status_callback (function): Uma função chamada para enviar atualizações
                                    de status para o front-end.

    Returns:
        list: Uma lista de strings contendo as URLs das imagens, ou uma lista
              vazia em caso de erro ou se nenhuma imagem for encontrada.
    """
    # Informa ao front-end que a análise começou
    status_callback("Analisando o anúncio...")
    
    try:
        # Define um User-Agent para simular um navegador e evitar bloqueios
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Faz a requisição HTTP para obter o conteúdo da página
        response = requests.get(url_anuncio, headers=headers, timeout=10)
        response.raise_for_status()  # Gera um erro se a resposta não for '200 OK'

        # Usa o BeautifulSoup para analisar o conteúdo HTML da página
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontra todas as tags <img> com a classe específica das imagens do produto
        tags_de_imagem = soup.find_all('img', class_='ui-pdp-image')

        if not tags_de_imagem:
            return [] # Retorna lista vazia se não encontrar imagens

        # Extrai o link do atributo 'data-src' ou 'src' de cada tag
        urls_encontradas = [tag.get('data-src') or tag.get('src') for tag in tags_de_imagem]
        
        # Transforma as URLs para a versão de alta resolução (Original)
        # Ex: de "...-F.webp" para "...-O.jpg"
        urls_alta_resolucao = [url.replace('-F.webp', '-O.jpg').replace('-W.webp', '-O.jpg') for url in urls_encontradas if url]
        
        return urls_alta_resolucao

    except Exception as e:
        # Em caso de qualquer erro (conexão, página não encontrada, etc.), informa o front-end
        status_callback(f"Erro ao analisar o link: {e}")
        return []

def baixar_redimensionar_e_salvar(lista_urls, caminho_da_pasta, fator_aumento, status_callback):
    """
    Percorre uma lista de URLs, baixa cada imagem, filtra por tamanho,
    redimensiona e salva na pasta de destino.

    Args:
        lista_urls (list): A lista de URLs das imagens a serem processadas.
        caminho_da_pasta (str): O caminho completo da pasta onde as imagens serão salvas.
        fator_aumento (int or float): O multiplicador para o redimensionamento (ex: 2).
        status_callback (function): Função para enviar atualizações de status.

    Returns:
        int: O número total de imagens que foram efetivamente salvas.
    """
    # Cria a pasta de destino, se ela ainda não existir
    if not os.path.exists(caminho_da_pasta):
        os.makedirs(caminho_da_pasta)

    imagens_salvas = 0
    total_a_processar = len(lista_urls)
    
    # Itera sobre cada URL da lista para processar uma por uma
    for i, url in enumerate(lista_urls):
        status_callback(f"Processando imagem {i + 1} de {total_a_processar}...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0 ...'}
            imagem_response = requests.get(url, headers=headers, timeout=10)

            if imagem_response.status_code == 200:
                # Abre a imagem baixada em memória, sem precisar salvar no disco primeiro
                img_original = Image.open(BytesIO(imagem_response.content))
                largura, altura = img_original.size

                # Filtro: ignora imagens que forem muito pequenas (provavelmente miniaturas ou ícones)
                if largura < 200 or altura < 200:
                    continue  # A palavra 'continue' pula para a próxima iteração do loop

                # Calcula as novas dimensões baseadas no fator de aumento
                nova_largura = int(largura * fator_aumento)
                nova_altura = int(altura * fator_aumento)
                
                # Redimensiona a imagem usando um filtro de alta qualidade (LANCZOS)
                img_redimensionada = img_original.resize((nova_largura, nova_altura), Image.Resampling.LANCZOS)
                
                # Converte para o modo RGB para garantir compatibilidade ao salvar como JPEG
                if img_redimensionada.mode != 'RGB':
                    img_redimensionada = img_redimensionada.convert('RGB')
                
                # Incrementa o contador e define o nome do arquivo final
                imagens_salvas += 1
                nome_arquivo = f"imagem_{imagens_salvas}.jpg"
                caminho_completo_arquivo = os.path.join(caminho_da_pasta, nome_arquivo)
                
                # Salva a imagem processada no disco com alta qualidade
                img_redimensionada.save(caminho_completo_arquivo, 'jpeg', quality=95)

        except Exception as e:
            # Imprime o erro no terminal para fins de depuração, mas não para o programa
            print(f"Ocorreu um erro ao processar a imagem {url}: {e}")
            
    return imagens_salvas