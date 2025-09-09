"""
================================================
AUTOMAÇÃO PARA DOWNLOAD DE IMAGENS DO MERCADO LIVRE (VERSÃO COM INTERFACE GRÁFICA)
================================================

Descrição:
Esta é uma aplicação de desktop com interface gráfica (GUI) que permite ao usuário
baixar e processar imagens de um anúncio do Mercado Livre.

Funcionalidades:
- Janela gráfica criada com Tkinter.
- Campos para inserir a URL do anúncio e o nome da pasta de destino.
- Botão para iniciar o processo.
- Label de status para feedback em tempo real.
- Uso de threading para evitar que a interface congele durante o download.

Dependências:
- requests
- beautifulsoup4
- Pillow
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
from bs4 import BeautifulSoup
import os
from PIL import Image
from io import BytesIO

# --- O "CÉREBRO" DO PROGRAMA (NOSSAS FUNÇÕES ANTIGAS, UM POUCO ADAPTADAS) ---

def obter_links_de_imagens(url_anuncio, status_callback):
    """Analisa o anúncio e retorna as URLs das imagens."""
    status_callback("Analisando o anúncio...")
    # (O restante da função é idêntico ao que tínhamos antes)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 ...'}
        response = requests.get(url_anuncio, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tags_de_imagem = soup.find_all('img', class_='ui-pdp-image')
        if not tags_de_imagem: return []
        urls = [tag.get('data-src') or tag.get('src') for tag in tags_de_imagem]
        urls_alta_resolucao = [url.replace('-F.webp', '-O.jpg').replace('-W.webp', '-O.jpg') for url in urls if url]
        return urls_alta_resolucao
    except Exception as e:
        status_callback(f"Erro ao analisar: {e}")
        return []

def baixar_redimensionar_e_salvar(lista_urls, caminho_da_pasta, fator_aumento, status_callback):
    """Baixa, filtra, redimensiona e salva as imagens."""
    if not os.path.exists(caminho_da_pasta):
        os.makedirs(caminho_da_pasta)

    imagens_salvas = 0
    total_a_processar = len(lista_urls)
    for i, url in enumerate(lista_urls):
        status_callback(f"Processando imagem {i + 1} de {total_a_processar}...")
        try:
            # (Lógica de download e processamento idêntica à anterior)
            headers = {'User-Agent': 'Mozilla/5.0 ...'}
            imagem_response = requests.get(url, headers=headers)
            if imagem_response.status_code == 200:
                img_original = Image.open(BytesIO(imagem_response.content))
                largura, altura = img_original.size
                if largura < 200 or altura < 200:
                    continue
                
                nova_largura = int(largura * fator_aumento)
                nova_altura = int(altura * fator_aumento)
                img_redimensionada = img_original.resize((nova_largura, nova_altura), Image.Resampling.LANCZOS)
                
                if img_redimensionada.mode != 'RGB':
                    img_redimensionada = img_redimensionada.convert('RGB')
                
                imagens_salvas += 1
                nome_arquivo = f"imagem_{imagens_salvas}.jpg"
                caminho_completo_arquivo = os.path.join(caminho_da_pasta, nome_arquivo)
                img_redimensionada.save(caminho_completo_arquivo, 'jpeg', quality=95)
        except Exception as e:
            print(f"Erro na imagem {i+1}: {e}") # Log de erro no terminal
    return imagens_salvas


# --- A INTERFACE GRÁFICA (O "ROSTO" DO PROGRAMA) ---

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Downloader de Imagens - Mercado Livre")
        self.root.geometry("500x200") # Largura x Altura da janela

        # Estilo dos widgets
        style = ttk.Style()
        style.configure("TLabel", padding=5, font=('Helvetica', 10))
        style.configure("TEntry", padding=5, font=('Helvetica', 10))
        style.configure("TButton", padding=5, font=('Helvetica', 10, 'bold'))

        # Frame principal para organizar os elementos
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Widgets (Botões, caixas de texto, etc.) ---

        # URL
        ttk.Label(main_frame, text="Link do Anúncio:").grid(row=0, column=0, sticky=tk.W)
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=0, column=1, sticky=tk.EW)

        # Nome da Pasta
        ttk.Label(main_frame, text="Nome da Pasta:").grid(row=1, column=0, sticky=tk.W)
        self.pasta_entry = ttk.Entry(main_frame, width=50)
        self.pasta_entry.grid(row=1, column=1, sticky=tk.EW)
        
        # Botão de Download
        self.download_button = ttk.Button(main_frame, text="Baixar Imagens", command=self.iniciar_thread_download)
        self.download_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Label de Status
        self.status_label = ttk.Label(main_frame, text="Status: Aguardando início...")
        self.status_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Configuração para a coluna da caixa de texto expandir com a janela
        main_frame.columnconfigure(1, weight=1)

    def atualizar_status(self, texto):
        """Função segura para atualizar o texto da label de status a partir de qualquer thread."""
        self.status_label.config(text=f"Status: {texto}")

    def iniciar_thread_download(self):
        """Pega os dados da interface e inicia a lógica de download em uma nova thread."""
        url = self.url_entry.get()
        nome_pasta = self.pasta_entry.get()

        if not url or not nome_pasta:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return

        # Desabilita o botão para evitar múltiplos cliques
        self.download_button.config(state=tk.DISABLED)
        
        # Cria e inicia a thread para não travar a janela
        thread = threading.Thread(target=self.executar_download, args=(url, nome_pasta))
        thread.start()

    def executar_download(self, url, nome_pasta):
        """Função que executa o trabalho pesado na thread secundária."""
        try:
            FATOR_DE_AUMENTO = 2
            
            links = obter_links_de_imagens(url, self.atualizar_status)
            
            if not links:
                self.atualizar_status("Nenhuma imagem encontrada ou erro na análise.")
                messagebox.showinfo("Concluído", "Nenhuma imagem válida foi encontrada no anúncio.")
                return

            self.atualizar_status(f"Encontrei {len(links)} imagens. Iniciando download...")
            
            caminho_final = os.path.join("img", nome_pasta)
            
            imagens_salvas = baixar_redimensionar_e_salvar(links, caminho_final, FATOR_DE_AUMENTO, self.atualizar_status)
            
            mensagem_final = f"{imagens_salvas} imagens salvas em '{caminho_final}'"
            self.atualizar_status(f"Concluído! {mensagem_final}")
            messagebox.showinfo("Sucesso", f"Download concluído!\n\n{mensagem_final}")

        except Exception as e:
            self.atualizar_status(f"Ocorreu um erro fatal: {e}")
            messagebox.showerror("Erro Fatal", f"Ocorreu um erro inesperado durante o processo:\n\n{e}")
        finally:
            # Reabilita o botão, não importa se deu sucesso ou erro
            self.download_button.config(state=tk.NORMAL)


# --- BLOCO DE EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    root = tk.Tk()  # Cria a janela principal
    app = App(root) # Cria a instância da nossa aplicação
    root.mainloop() # Inicia o loop da janela, que a mantém aberta e responsiva