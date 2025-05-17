# 🌐 Gerenciador de Traduções de Mods Minecraft

[![Versão Python](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)
[![Licença](https://img.shields.io/badge/licença-MIT-green)](LICENSE)

Uma ferramenta automatizada para gerenciar e acompanhar traduções de mods do Minecraft, com foco na localização em português brasileiro (pt_BR).

## ✨ Funcionalidades

- 🔄 Rastreamento automático de atualizações de traduções
- 🔍 Comparação inteligente entre traduções em inglês e português
- 📊 Monitoramento em tempo real
- 📝 Geração detalhada de registro de alterações
- 🤖 Fluxo de trabalho automatizado no GitHub

## 📋 Status Atual

| Mod | Status | Última Atualização |
|-----|--------|-------------|
| **Just Enough Items** | 🟢 Atualizado | 11/05/2025 |
| **Vinery** | 🔴 Desatualizado | 11/05/2025 |

## 🚀 Como Começar

### Pré-requisitos

- Python 3.6 ou superior
- Gerenciador de pacotes `pip`

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seunome/traducoes-minecraft-mods.git
cd traducoes-minecraft-mods
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure seus mods no arquivo `mods.json`:
```json
{
    "Nome do Mod": "id-modrinth"
}
```

### Uso

Execute o gerenciador de traduções:
```bash
python gerenciador_traducoes.py
```

## 📁 Estrutura do Projeto

```
.
├── mods.json                 # Arquivo de configuração dos mods
├── gerenciador_traducoes.py  # Script principal
├── mods_langs/              # Arquivos de tradução
│   └── NomeMod/
│       ├── lang/
│       │   ├── en_us.json
│       │   └── pt_br.json
│       └── README.md        # Registro de alterações do mod
└── README.md               # Documentação principal
```

## 🤝 Como Contribuir

1. Faça um fork do repositório
2. Crie sua branch de feature (`git checkout -b feature/NovaFuncionalidade`)
3. Faça commit das alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Faça push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- Todos os criadores e mantenedores de mods
- A comunidade de modding do Minecraft
- Contribuidores deste projeto