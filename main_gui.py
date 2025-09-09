"""
======================================================
FRONTEND - INTERFACE GRÁFICA (GUI) DO DOWNLOADER
======================================================
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import threading
import os
import backend
import sys # NOVO: Para identificar o sistema operacional
import subprocess

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Downloader de Imagens - Mercado Livre")

        # NOVO: Variável para guardar o caminho do último download bem-sucedido
        self.ultimo_caminho_salvo = None

        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=BOTH, expand=True)

        # --- Widgets ---
        ttk.Label(main_frame, text="Link do Anúncio:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=0, column=1, sticky=EW, padx=5, pady=5)

        ttk.Label(main_frame, text="Nome da Pasta:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.pasta_entry = ttk.Entry(main_frame, width=50)
        self.pasta_entry.grid(row=1, column=1, sticky=EW, padx=5, pady=5)
        
        # NOVO: Frame para agrupar os botões lado a lado
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=5, sticky=EW)

        self.download_button = ttk.Button(botoes_frame, text="Baixar Imagens", command=self.iniciar_thread_download, bootstyle="primary")
        self.download_button.pack(side=LEFT, expand=True, fill=X, padx=(0, 5))
        
        # NOVO: Botão "Abrir Pasta"
        self.abrir_pasta_button = ttk.Button(botoes_frame, text="Abrir Pasta", command=self.abrir_pasta_destino, bootstyle="secondary", state=DISABLED)
        self.abrir_pasta_button.pack(side=LEFT, expand=True, fill=X, padx=(5, 0))
        
        self.status_label = ttk.Label(main_frame, text="Status: Aguardando início...")
        self.status_label.grid(row=3, column=0, columnspan=2, sticky=W, padx=5, pady=5)
        
        main_frame.columnconfigure(1, weight=1)
        botoes_frame.columnconfigure(0, weight=1)
        botoes_frame.columnconfigure(1, weight=1)

    # NOVO: Função para abrir a pasta de destino
    def abrir_pasta_destino(self):
        if self.ultimo_caminho_salvo:
            # Garante que o caminho é absoluto para evitar erros
            caminho_absoluto = os.path.abspath(self.ultimo_caminho_salvo)
            try:
                # Lógica para abrir a pasta dependendo do sistema operacional
                if sys.platform == "win32":
                    os.startfile(caminho_absoluto)
                elif sys.platform == "darwin": # macOS
                    subprocess.Popen(["open", caminho_absoluto])
                else: # Linux
                    subprocess.Popen(["xdg-open", caminho_absoluto])
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir a pasta.\nErro: {e}")

    def atualizar_status(self, texto):
        self.status_label.config(text=f"Status: {texto}")

    def iniciar_thread_download(self):
        url = self.url_entry.get()
        nome_pasta = self.pasta_entry.get()

        if not url or not nome_pasta:
            messagebox.showerror("Erro de Entrada", "Por favor, preencha todos os campos antes de continuar.")
            return

        self.download_button.config(state=DISABLED)
        # ALTERADO: Desabilita o botão "Abrir Pasta" no início de um novo download
        self.abrir_pasta_button.config(state=DISABLED) 
        thread = threading.Thread(target=self.executar_download, args=(url, nome_pasta))
        thread.start()

    def executar_download(self, url, nome_pasta):
        try:
            FATOR_DE_AUMENTO = 2
            links = backend.obter_links_de_imagens(url, self.atualizar_status)
            if not links:
                self.atualizar_status("Nenhuma imagem encontrada ou erro na análise.")
                messagebox.showinfo("Concluído", "Nenhuma imagem válida foi encontrada no anúncio.")
                return

            self.atualizar_status(f"Encontrei {len(links)} imagens. Iniciando download...")
            caminho_final = os.path.join("img", nome_pasta)
            imagens_salvas = backend.baixar_redimensionar_e_salvar(links, caminho_final, FATOR_DE_AUMENTO, self.atualizar_status)
            
            mensagem_final = f"{imagens_salvas} imagens salvas em '{caminho_final}'"
            self.atualizar_status(f"Concluído! {mensagem_final}")
            messagebox.showinfo("Sucesso", f"Download concluído!\n\n{mensagem_final}")
            
            # ALTERADO: Guarda o caminho e habilita o botão após sucesso
            if imagens_salvas > 0:
                self.ultimo_caminho_salvo = caminho_final
                self.abrir_pasta_button.config(state=NORMAL)

        except Exception as e:
            mensagem_erro = f"Ocorreu um erro inesperado: {e}"
            self.atualizar_status(mensagem_erro)
            messagebox.showerror("Erro Fatal", f"Ocorreu um erro durante o processo:\n\n{e}")
        finally:
            self.download_button.config(state=NORMAL)
            # ALTERADO: Limpa os campos de texto no final do processo
            self.url_entry.delete(0, END)
            self.pasta_entry.delete(0, END)
            self.atualizar_status("Pronto para o próximo download.")

if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    app = App(root)
    root.mainloop()