"""
================================================
AUTOMAÇÃO PARA DOWNLOAD DE IMAGENS DO MERCADO LIVRE
================================================

Descrição:
Este script Python permite ao usuário baixar todas as imagens de um anúncio
do Mercado Livre de forma interativa. Ele extrai as imagens na maior
resolução disponível, filtra as que são muito pequenas (miniaturas/ícones)
e as redimensiona (upscaling) para um tamanho maior antes de salvar.

Funcionalidades:
- Interface interativa via terminal.
- Extrai URLs de imagem da versão de mais alta qualidade (-O.jpg).
- Filtra e ignora imagens com dimensões menores que 200x200 pixels.
- Redimensiona as imagens por um fator configurável (ex: 2x, 3x).
- Salva as imagens em uma subpasta nomeada pelo usuário, dentro de uma pasta 'img'.

Dependências:
- requests
- beautifulsoup4
- Pillow

Autor: Pedro Baffa
Versão: 1.0
Data: 07/09/2025
"""

import requests
from bs4 import BeautifulSoup
import os
from PIL import Image
from io import BytesIO

def obter_links_de_imagens(url_anuncio):
    """
    Analisa um anúncio do Mercado Livre e retorna uma lista de URLs
    de imagens em alta resolução.
    """
    print("Analisando o anúncio, por favor aguarde...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url_anuncio, headers=headers)
        response.raise_for_status() # Lança um erro se a requisição falhar

        soup = BeautifulSoup(response.text, 'html.parser')
        tags_de_imagem = soup.find_all('img', class_='ui-pdp-image')

        if not tags_de_imagem:
            return []

        urls_alta_resolucao = []
        for img_tag in tags_de_imagem:
            url_imagem = img_tag.get('data-src') or img_tag.get('src')
            if url_imagem:
                # Transforma a URL para a versão de alta resolução (Original)
                url_alta = url_imagem.replace('-F.webp', '-O.jpg').replace('-W.webp', '-O.jpg')
                urls_alta_resolucao.append(url_alta)
        
        return urls_alta_resolucao

    except requests.exceptions.RequestException as e:
        print(f"\nOcorreu um erro de conexão: {e}")
        return []
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")
        return []

def baixar_redimensionar_e_salvar(lista_urls, caminho_da_pasta, fator_aumento):
    """
    Baixa, filtra por tamanho, redimensiona e salva as imagens de uma lista de URLs.
    """
    if not os.path.exists(caminho_da_pasta):
        os.makedirs(caminho_da_pasta)
        print(f"Pasta '{caminho_da_pasta}' criada com sucesso.")

    headers = {'User-Agent': 'Mozilla/5.0 ...'}
    
    imagens_salvas = 0
    total_imagens_encontradas = len(lista_urls)
    
    for i, url in enumerate(lista_urls):
        print(f"Processando imagem {i + 1} de {total_imagens_encontradas}...")
        try:
            imagem_response = requests.get(url, headers=headers)
            if imagem_response.status_code == 200:
                
                img_original = Image.open(BytesIO(imagem_response.content))
                largura_original, altura_original = img_original.size
                
                # Filtro de tamanho mínimo para ignorar miniaturas
                if largura_original < 200 or altura_original < 200:
                    print(f"  - Ignorando imagem pequena ({largura_original}x{altura_original}px).")
                    continue # Pula para a próxima imagem
                
                # Calcula as novas dimensões e faz o upscale
                nova_largura = int(largura_original * fator_aumento)
                nova_altura = int(altura_original * fator_aumento)
                print(f"  - Redimensionando de {largura_original}x{altura_original} para {nova_largura}x{nova_altura}")
                img_redimensionada = img_original.resize((nova_largura, nova_altura), Image.Resampling.LANCZOS)

                if img_redimensionada.mode != 'RGB':
                    img_redimensionada = img_redimensionada.convert('RGB')
                
                # Salva a imagem processada
                imagens_salvas += 1
                nome_arquivo = f"imagem_{imagens_salvas}.jpg"
                caminho_completo_arquivo = os.path.join(caminho_da_pasta, nome_arquivo)
                img_redimensionada.save(caminho_completo_arquivo, 'jpeg', quality=95)
                
            else:
                print(f"  - Falha ao baixar a imagem {i + 1}. Código: {imagem_response.status_code}")
        except Exception as e:
            print(f"  - Ocorreu um erro ao processar a imagem {i+1}: {e}")
    
    print(f"\nProcesso concluído! Foram salvas {imagens_salvas} de {total_imagens_encontradas} imagens encontradas.")
    print(f"Os arquivos estão em '{caminho_da_pasta}'")


# --- BLOCO DE EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    # Fator de aumento para o tamanho das imagens (2 = dobrar o tamanho)
    FATOR_DE_AUMENTO = 2

    # Interação com o usuário
    url = input("Cole aqui o link do anúncio do Mercado Livre: ")
    links_das_imagens = obter_links_de_imagens(url)

    if links_das_imagens:
        num_imagens = len(links_das_imagens)
        
        prompt_nome_pasta = f"Encontrei {num_imagens} imagens. Escreva o nome da pasta para salvá-las: "
        nome_subpasta = input(prompt_nome_pasta)
        
        pasta_principal = "img"
        caminho_final = os.path.join(pasta_principal, nome_subpasta)
        
        baixar_redimensionar_e_salvar(links_das_imagens, caminho_final, FATOR_DE_AUMENTO)
    else:
        print("\nNão foi possível encontrar imagens no anúncio fornecido.")