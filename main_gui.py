"""
======================================================
FRONTEND - INTERFACE GRÁFICA (GUI) DO DOWNLOADER
======================================================

Este arquivo é responsável por criar e gerenciar a interface gráfica do usuário (GUI)
para a aplicação de download de imagens. Ele utiliza a biblioteca Tkinter.

Sua função é apresentar os controles ao usuário (campos de texto, botão) e
delegar todo o trabalho de lógica para o módulo 'backend.py'.

Dependências:
- backend.py (deve estar na mesma pasta)
"""

# --- Importações necessárias para o front-end ---
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
# Importamos nosso outro arquivo, tratando-o como uma biblioteca de ferramentas
import backend

class App:
    """
    A classe principal que encapsula todos os elementos e comportamentos
    da nossa janela gráfica.
    """
    def __init__(self, root):
        """
        O construtor da nossa aplicação. É executado quando a App é criada
        e é responsável por montar a janela inicial.
        """
        self.root = root
        self.root.title("Downloader de Imagens - Mercado Livre")
        self.root.geometry("500x200")  # Define o tamanho inicial da janela

        # Usamos 'ttk' para dar um visual um pouco mais moderno aos widgets
        style = ttk.Style()
        style.configure("TLabel", padding=5, font=('Helvetica', 10))
        style.configure("TEntry", padding=5, font=('Helvetica', 10))
        style.configure("TButton", padding=5, font=('Helvetica', 10, 'bold'))

        # O 'Frame' é como um container para organizar os outros elementos dentro da janela
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Criação dos Widgets (elementos da tela) ---

        # Rótulo e campo de entrada para a URL
        ttk.Label(main_frame, text="Link do Anúncio:").grid(row=0, column=0, sticky=tk.W)
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=0, column=1, sticky=tk.EW)

        # Rótulo e campo de entrada para o Nome da Pasta
        ttk.Label(main_frame, text="Nome da Pasta:").grid(row=1, column=0, sticky=tk.W)
        self.pasta_entry = ttk.Entry(main_frame, width=50)
        self.pasta_entry.grid(row=1, column=1, sticky=tk.EW)
        
        # Botão que o usuário clica para iniciar o download
        # O 'command' especifica qual função será chamada quando o botão for pressionado
        self.download_button = ttk.Button(main_frame, text="Baixar Imagens", command=self.iniciar_thread_download)
        self.download_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Rótulo de texto que usaremos para mostrar o progresso
        self.status_label = ttk.Label(main_frame, text="Status: Aguardando início...")
        self.status_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Faz com que a coluna das caixas de texto se expanda se a janela for redimensionada
        main_frame.columnconfigure(1, weight=1)

    def atualizar_status(self, texto):
        """
        Atualiza de forma segura o texto da label de status.
        Esta função é essencial para que a thread do backend possa se comunicar
        com a janela do front-end sem causar erros.
        """
        self.status_label.config(text=f"Status: {texto}")

    def iniciar_thread_download(self):
        """
        Esta função é chamada pelo clique do botão. Ela pega os dados da tela
        e inicia a lógica de download em uma nova thread para não travar a interface.
        """
        url = self.url_entry.get()
        nome_pasta = self.pasta_entry.get()

        # Validação simples para garantir que os campos não estão vazios
        if not url or not nome_pasta:
            messagebox.showerror("Erro de Entrada", "Por favor, preencha todos os campos antes de continuar.")
            return

        # Desabilita o botão para que o usuário não possa clicar de novo enquanto um download está em andamento
        self.download_button.config(state=tk.DISABLED)
        
        # Cria a thread secundária, dizendo a ela para executar a função 'self.executar_download'
        thread = threading.Thread(target=self.executar_download, args=(url, nome_pasta))
        thread.start() # Inicia a execução da thread em segundo plano

    def executar_download(self, url, nome_pasta):
        """
        Esta função é executada na thread secundária. Ela chama as funções do
        módulo 'backend' para fazer todo o trabalho pesado.
        """
        try:
            FATOR_DE_AUMENTO = 2
            
            # Chama a função do backend, passando 'self.atualizar_status' como o callback
            links = backend.obter_links_de_imagens(url, self.atualizar_status)
            
            if not links:
                self.atualizar_status("Nenhuma imagem encontrada ou erro na análise.")
                messagebox.showinfo("Concluído", "Nenhuma imagem válida foi encontrada no anúncio.")
                return

            self.atualizar_status(f"Encontrei {len(links)} imagens. Iniciando download...")
            
            caminho_final = os.path.join("img", nome_pasta)
            
            # Chama a segunda função do backend para baixar e processar as imagens
            imagens_salvas = backend.baixar_redimensionar_e_salvar(links, caminho_final, FATOR_DE_AUMENTO, self.atualizar_status)
            
            mensagem_final = f"{imagens_salvas} imagens salvas em '{caminho_final}'"
            self.atualizar_status(f"Concluído! {mensagem_final}")
            messagebox.showinfo("Sucesso", f"Download concluído!\n\n{mensagem_final}")

        except Exception as e:
            # Captura qualquer erro inesperado e exibe uma mensagem
            mensagem_erro = f"Ocorreu um erro inesperado: {e}"
            self.atualizar_status(mensagem_erro)
            messagebox.showerror("Erro Fatal", f"Ocorreu um erro durante o processo:\n\n{e}")
        finally:
            # O bloco 'finally' sempre é executado, independentemente de ter dado sucesso ou erro.
            # Usamos isso para garantir que o botão seja reabilitado no final.
            self.download_button.config(state=tk.NORMAL)


# --- BLOCO DE EXECUÇÃO PRINCIPAL ---
# Este código só roda quando executamos este arquivo diretamente.
if __name__ == "__main__":
    root = tk.Tk()      # 1. Cria a janela principal em branco
    app = App(root)     # 2. Cria uma instância da nossa classe App, passando a janela para ela montar os widgets
    root.mainloop()     # 3. Inicia o loop da aplicação, que mantém a janela aberta e esperando por ações do usuário