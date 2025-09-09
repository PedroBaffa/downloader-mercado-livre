# Downloader de imagens do Mercado Livre
# Feito em: 09/09/2025

# --- Importações ---
# ttkbootstrap pra deixar a janela bonita
# threading pra fazer o download sem travar a tela
# messagebox pra mostrar as caixinhas de erro/sucesso
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import threading
import os
# aqui eu puxo as funções do outro arquivo, o backend
import backend

class App:
    # A classe principal que organiza a janela inteira
    def __init__(self, root):
        self.root = root
        self.root.title("Downloader de Imagens - Mercado Livre")

        # um frame é tipo um container pra organizar as coisas dentro da janela
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=BOTH, expand=True) # fill=BOTH faz ele ocupar todo o espaço

        # --- Elementos da Tela (Widgets) ---

        # Campo pra colar a URL
        ttk.Label(main_frame, text="Link do Anúncio:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=0, column=1, sticky=EW, padx=5, pady=5)

        # Campo pra dar nome pra pasta
        ttk.Label(main_frame, text="Nome da Pasta:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.pasta_entry = ttk.Entry(main_frame, width=50)
        self.pasta_entry.grid(row=1, column=1, sticky=EW, padx=5, pady=5)
        
        # O botão principal. O 'command=' chama a função que eu defini pra começar o download
        self.download_button = ttk.Button(main_frame, text="Baixar Imagens", command=self.iniciar_thread_download, bootstyle="primary")
        self.download_button.grid(row=2, column=0, columnspan=2, pady=10, padx=5, sticky=EW)
        
        # O texto que vai mudando pra mostrar o que tá acontecendo
        self.status_label = ttk.Label(main_frame, text="Status: Aguardando início...")
        self.status_label.grid(row=3, column=0, columnspan=2, sticky=W, padx=5, pady=5)
        
        # macete pra coluna 1 (onde estão as caixas de texto) esticar junto com a janela
        main_frame.columnconfigure(1, weight=1)

    def atualizar_status(self, texto):
        # função pra conseguir mudar o texto de status lá de dentro da thread de download
        self.status_label.config(text=f"Status: {texto}")

    def iniciar_thread_download(self):
        # Essa função é a que o botão chama. Ela só prepara as coisas e inicia a thread.
        url = self.url_entry.get()
        nome_pasta = self.pasta_entry.get()

        # uma checagem simples pra ver se o usuário preencheu tudo
        if not url or not nome_pasta:
            messagebox.showerror("Opa!", "Precisa preencher os dois campos, amigo.")
            return

        # desabilito o botao pra evitar que o usuário clique de novo e bugue tudo
        self.download_button.config(state=DISABLED)
        
        # AQUI A MÁGICA PRA NÃO TRAVAR A JANELA!
        # Crio uma thread nova que vai rodar a função de download em segundo plano.
        thread = threading.Thread(target=self.executar_download, args=(url, nome_pasta))
        thread.start() # aqui a thread começa a rodar

    def executar_download(self, url, nome_pasta):
        # Essa função roda "por trás dos panos", na thread secundária.
        try:
            FATOR_DE_AUMENTO = 2 # define o quanto a imagem vai ser aumentada
            
            # aqui eu chamo as funções que fazem o trabalho sujo, lá no backend.py
            links = backend.obter_links_de_imagens(url, self.atualizar_status)
            
            if not links: # se a lista de links vier vazia, deu ruim
                self.atualizar_status("Não achei nenhuma imagem nesse link.")
                messagebox.showinfo("Hmm...", "Não encontrei imagens válidas nesse anúncio.")
                return

            self.atualizar_status(f"Beleza, achei {len(links)} imagens. Baixando...")
            
            caminho_final = os.path.join("img", nome_pasta)
            
            imagens_salvas = backend.baixar_redimensionar_e_salvar(links, caminho_final, FATOR_DE_AUMENTO, self.atualizar_status)
            
            mensagem_final = f"{imagens_salvas} imagens salvas na pasta '{caminho_final}'"
            self.atualizar_status(f"Prontinho! {mensagem_final}")
            messagebox.showinfo("Sucesso!", f"Download terminado!\n\n{mensagem_final}")

        except Exception as e:
            # se der um erro muito feio, mostra essa mensagem
            mensagem_erro = f"Deu um erro cabuloso: {e}"
            self.atualizar_status(mensagem_erro)
            messagebox.showerror("Vish...", f"Deu um erro inesperado no processo:\n\n{e}")
        finally:
            # o 'finally' é legal pq ele SEMPRE executa, dando certo ou errado.
            # isso garante que o botão vai ser reativado no final.
            self.download_button.config(state=NORMAL)

# --- Ponto de Partida do Programa ---
if __name__ == "__main__":
    # é aqui que o programa começa a rodar de verdade
    
    # LEMBRETE: É AQUI QUE EU ESCOLHO O TEMA! 
    # 'litera' é legal, 'darkly' também é show.
    root = ttk.Window(themename="litera")
    app = App(root)
    # o mainloop deixa a janela aberta, esperando a gente fazer alguma coisa
    root.mainloop()