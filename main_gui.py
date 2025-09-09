"""
======================================================
FRONTEND - INTERFACE GRÁFICA (GUI) DO DOWNLOADER
======================================================
Versão com processamento em lote a partir de uma planilha Excel.
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog # NOVO: filedialog para abrir a janela de seleção de arquivo
import threading
import os
import backend
import pandas as pd # NOVO: Importamos a biblioteca Pandas

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Downloader de Imagens em Lote - Mercado Livre")
        
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=BOTH, expand=True)

        # --- Widgets ---
        # ALTERADO: Removemos os campos de texto e criamos um botão principal
        
        instrucao_label = ttk.Label(main_frame, text="Clique no botão abaixo para selecionar sua planilha (.xlsx)", justify="center")
        instrucao_label.pack(pady=(10, 5))

        self.load_button = ttk.Button(main_frame, text="Carregar Planilha...", command=self.carregar_planilha, bootstyle="primary")
        self.load_button.pack(pady=10, padx=20, fill=X)
        
        self.status_label = ttk.Label(main_frame, text="Status: Aguardando planilha...")
        self.status_label.pack(pady=(5, 10), fill=X)

    # NOVO: Função chamada pelo botão "Carregar Planilha..."
    def carregar_planilha(self):
        """Abre uma janela para o usuário selecionar o arquivo da planilha."""
        # Abre a janela de diálogo para o usuário escolher um arquivo
        filepath = filedialog.askopenfilename(
            title="Selecione a planilha",
            filetypes=[("Arquivos Excel", "*.xlsx"), ("Todos os arquivos", "*.*")]
        )
        
        # Se o usuário selecionou um arquivo (não clicou em cancelar)
        if filepath:
            self.load_button.config(state=DISABLED) # Desabilita o botão
            # Inicia o processamento da planilha em uma nova thread
            thread = threading.Thread(target=self.processar_planilha, args=(filepath,))
            thread.start()

    # NOVO: A função que faz o trabalho pesado, rodando na thread
    def processar_planilha(self, filepath):
        """Lê a planilha e processa cada linha."""
        try:
            self.atualizar_status("Lendo a planilha...")
            # Usa o Pandas para ler o arquivo Excel. Espera que as colunas se chamem 'Link' e 'NomePasta'
            df = pd.read_excel(filepath)

            total_linhas = len(df)
            if total_linhas == 0:
                self.atualizar_status("Planilha vazia.")
                messagebox.showinfo("Aviso", "A planilha selecionada está vazia.")
                return

            # Itera sobre cada linha da planilha
            for index, row in df.iterrows():
                progresso_geral = f"Processando linha {index + 1} de {total_linhas}..."
                self.atualizar_status(progresso_geral)

                link_anuncio = row['Link']
                nome_pasta = row['NomePasta']

                # Verifica se a linha tem os dados necessários
                if pd.isna(link_anuncio) or pd.isna(nome_pasta):
                    print(f"Linha {index + 2} ignorada: dados incompletos.")
                    continue

                # Define um callback interno para atualizar o status com mais detalhes
                def status_callback_interno(texto):
                    self.atualizar_status(f"{progresso_geral} - {texto}")

                # --- REUTILIZA NOSSO BACKEND ---
                # A mágica acontece aqui: usamos as mesmas funções de antes para cada linha!
                caminho_final = os.path.join("img", str(nome_pasta))
                FATOR_DE_AUMENTO = 2
                
                links = backend.obter_links_de_imagens(link_anuncio, status_callback_interno)
                if links:
                    backend.baixar_redimensionar_e_salvar(links, caminho_final, FATOR_DE_AUMENTO, status_callback_interno)
            
            self.atualizar_status("Processamento da planilha concluído!")
            messagebox.showinfo("Sucesso", f"Todas as {total_linhas} linhas da planilha foram processadas.")

        except KeyError:
            # Erro comum se os nomes das colunas estiverem errados
            mensagem_erro = "Erro: A planilha deve ter as colunas 'Link' e 'NomePasta'."
            self.atualizar_status(mensagem_erro)
            messagebox.showerror("Erro de Formato", mensagem_erro)
        except Exception as e:
            # Captura outros erros
            mensagem_erro = f"Ocorreu um erro: {e}"
            self.atualizar_status(mensagem_erro)
            messagebox.showerror("Erro Fatal", mensagem_erro)
        finally:
            # Reabilita o botão no final, independentemente de sucesso ou erro
            self.load_button.config(state=NORMAL)

    def atualizar_status(self, texto):
        self.status_label.config(text=f"Status: {texto}")


if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    app = App(root)
    root.mainloop()