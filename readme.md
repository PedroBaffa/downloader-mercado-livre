# 🤖 Automação para Download de Imagens do Mercado Livre

Este é um script em Python que automatiza o processo de baixar imagens de anúncios do Mercado Livre.

## ✨ Funcionalidades

- **Interface Interativa:** Basta rodar o script e seguir as instruções no terminal.
- **Alta Resolução:** O script busca automaticamente a versão com a maior qualidade de cada imagem disponível no anúncio.
- **Filtro Inteligente:** Imagens muito pequenas (menores que 200x200px), como ícones e miniaturas, são ignoradas.
- **Upscaling de Imagens:** Aumenta a resolução das imagens baixadas por um fator configurável, mantendo a proporção.
- **Organização Automática:** Salva tudo em uma pasta `img/` com um nome que você define na hora.

## 🚀 Como Usar

### 1. Pré-requisitos

- Python 3.x instalado.
- As bibliotecas `requests`, `beautifulsoup4` e `Pillow`.

### 2. Instalação das Dependências

Abra seu terminal e rode o seguinte comando:

```bash
py -m pip install requests beautifulsoup4 Pillow