# Configuração do Ambiente - Projeto Shamann

## Requisitos do Sistema
- Python 3.12 (instalado via pyenv)
- Kate IDE
- Terminal ZSH

## Passo a Passo para Configuração

### 1. Criar o Ambiente Virtual
No terminal, navegue até a pasta do projeto e execute:
```bash
# Criar o ambiente virtual
python -m venv venv

# Ativar o ambiente virtual
source venv/bin/activate
```

### 2. Instalar Dependências
Com o ambiente virtual ativado, instale as dependências:
```bash
# Atualizar pip para a última versão
pip install --upgrade pip

# Instalar todas as dependências
pip install -r requirements.txt
```

### 3. Verificar a Instalação
Para confirmar que tudo foi instalado corretamente:
```bash
# Verificar os pacotes instalados
pip list

# Rodar os testes
python -m pytest tests/
```

### 4. Estrutura do Projeto
Depois da instalação, você terá a seguinte estrutura:
```
.
├── venv/                  # Ambiente virtual
├── config/                # Configurações do projeto
├── core/                  # Funcionalidades principais
├── modules/               # Módulos do projeto
│   └── whois_guardian.py  # Módulo principal
├── tests/                 # Testes automatizados
├── logs/                  # Arquivos de log
├── output/               # Arquivos de saída
└── shamann.py            # Ponto de entrada do programa
```

### 5. Comandos Úteis
```bash
# Ativar o ambiente virtual (sempre necessário ao iniciar)
source venv/bin/activate

# Executar o programa
python shamann.py

# Executar os testes
python -m pytest tests/

# Desativar o ambiente virtual (quando terminar)
deactivate
```

### Observações
- Sempre ative o ambiente virtual antes de executar o projeto
- Mantenha o requirements.txt atualizado caso adicione novas dependências
- Os logs serão salvos automaticamente na pasta 'logs'
- Os resultados serão salvos na pasta 'output'
