# 🌐 Minecraft Mod Translation Manager

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

An automated tool to manage and track Minecraft mod translations, focusing on Brazilian Portuguese (pt_BR) localization.

## ✨ Features

- 🔄 Automatic tracking of mod translation updates
- 🔍 Smart comparison between English and Portuguese translations
- 📊 Real-time status monitoring
- 📝 Detailed changelog generation
- 🤖 Automated GitHub workflow

## 📋 Current Status

| Mod | Status | Last Update |
|-----|--------|-------------|
| **Just Enough Items** | 🟢 Updated | 11/05/2025 |
| **Vinery** | 🔴 Outdated | 11/05/2025 |

## 🚀 Getting Started

### Prerequisites

- Python 3.6 or higher
- `pip` package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/minecraft-mod-translations.git
cd minecraft-mod-translations
```

2. Install dependencies:
```bash
pip install requests
```

3. Configure your mods in `mods.json`:
```json
{
    "Mod Name": "modrinth-id"
}
```

### Usage

Run the translation manager:
```bash
python translation_manager.py
```

## 📁 Project Structure

```
.
├── mods.json              # Mod configuration file
├── translation_manager.py # Main script
├── mods_langs/           # Translation files
│   └── ModName/
│       ├── lang/
│       │   ├── en_us.json
│       │   └── pt_br.json
│       └── README.md     # Mod-specific changelog
└── README.md            # Main documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- All mod creators and maintainers
- The Minecraft modding community
- Contributors to this project