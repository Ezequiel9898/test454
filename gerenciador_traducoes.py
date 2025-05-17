import json
import os
import zipfile
import requests
import hashlib
from datetime import datetime
import difflib
import re
import locale
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Configuração do locale para português
locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('traducoes.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Constantes
ARQUIVO_MODS = 'mods.json'
PASTA_SAIDA = 'mods_langs'
PASTA_BACKUP = 'backups'
MODRINTH_API = 'https://api.modrinth.com/v2'
README_PRINCIPAL = 'README.md'

# Variáveis globais
tabela_status = {}
mod_alterado = False
estatisticas_globais = {
    'total_mods': 0,
    'mods_atualizados': 0,
    'strings_traduzidas': 0,
    'ultima_atualizacao': None
}

class Estatisticas:
    def __init__(self):
        self.total_strings = 0
        self.strings_traduzidas = 0
        self.qualidade = 0.0
        self.ultima_atualizacao = None

    def calcular_progresso(self) -> float:
        if self.total_strings == 0:
            return 0.0
        return (self.strings_traduzidas / self.total_strings) * 100

def criar_backup():
    """Cria um backup dos arquivos de tradução."""
    data_atual = datetime.now().strftime('%Y%m%d_%H%M%S')
    pasta_backup = os.path.join(PASTA_BACKUP, data_atual)
    
    if os.path.exists(PASTA_SAIDA):
        shutil.copytree(PASTA_SAIDA, pasta_backup)
        logging.info(f"Backup criado em: {pasta_backup}")
        
        # Manter apenas os últimos 5 backups
        backups = sorted(os.listdir(PASTA_BACKUP))
        if len(backups) > 5:
            for backup_antigo in backups[:-5]:
                shutil.rmtree(os.path.join(PASTA_BACKUP, backup_antigo))

def verificar_qualidade_traducao(en_us: dict, pt_br: dict) -> Tuple[float, List[str]]:
    """Verifica a qualidade da tradução."""
    problemas = []
    pontuacao = 100.0
    
    # Verifica strings não traduzidas
    for chave, valor in pt_br.items():
        if chave in en_us and valor == en_us[chave]:
            problemas.append(f"Aviso: String não traduzida: {chave}")
            pontuacao -= 2

    # Verifica formatação
    for chave, valor in pt_br.items():
        if '%s' in en_us.get(chave, '') and '%s' not in valor:
            problemas.append(f"Erro: Formatação incorreta em: {chave}")
            pontuacao -= 5

    return max(0.0, pontuacao), problemas

def carregar_mods(caminho: str) -> Dict[str, str]:
    """Carrega a configuração dos mods do arquivo JSON."""
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Erro ao carregar mods: {e}")
        return {}

def obter_ultima_versao(mod_id: str) -> dict:
    """Obtém a última versão do mod do Modrinth."""
    try:
        url = f"{MODRINTH_API}/project/{mod_id}/version"
        resposta = requests.get(url)
        resposta.raise_for_status()
        versoes = resposta.json()
        return versoes[0]
    except Exception as e:
        logging.error(f"Erro ao obter versão do mod {mod_id}: {e}")
        raise

def baixar_jar(versao: dict) -> Tuple[str, bytes]:
    """Baixa o arquivo JAR do mod."""
    for arquivo in versao['files']:
        if arquivo['filename'].endswith('.jar'):
            try:
                url = arquivo['url']
                r = requests.get(url)
                r.raise_for_status()
                return arquivo['filename'], r.content
            except Exception as e:
                logging.error(f"Erro ao baixar JAR: {e}")
                raise
    return None, None

def hash_arquivo(conteudo: bytes) -> str:
    """Calcula o hash MD5 do conteúdo do arquivo."""
    return hashlib.md5(conteudo).hexdigest()

def diferenca_json(antigo: str, novo: str) -> str:
    """Gera um diff entre duas strings JSON."""
    try:
        antigo_linhas = antigo.splitlines()
        novo_linhas = novo.splitlines()

        diff = list(difflib.ndiff(antigo_linhas, novo_linhas))
        blocos = []
        bloco_atual = []
        linha_antigo = linha_novo = 1

        for linha in diff:
            tipo = linha[0]
            conteudo = linha[2:]

            if tipo == ' ':
                if bloco_atual:
                    blocos.append(bloco_atual)
                    bloco_atual = []
                linha_antigo += 1
                linha_novo += 1
                continue

            if tipo == '-':
                bloco_atual.append(f"- {linha_antigo:04d} {conteudo}")
                linha_antigo += 1
            elif tipo == '+':
                bloco_atual.append(f"+ {linha_novo:04d} {conteudo}")
                linha_novo += 1

        if bloco_atual:
            blocos.append(bloco_atual)

        return '\n'.join(f'```diff\n' + '\n'.join(bloco) + '\n```' for bloco in blocos)

    except Exception as e:
        logging.error(f"Erro ao gerar diff: {e}")
        return f"Erro ao gerar diff: {e}"

def substituir_valores_json(texto_original: str, dicionario_substituicao: dict) -> str:
    """Substitui valores em um texto JSON."""
    def substituir(match):
        chave = match.group(1)
        if chave in dicionario_substituicao:
            valor_novo = json.dumps(dicionario_substituicao[chave], ensure_ascii=False)[1:-1]
            return f'"{chave}": "{valor_novo}"'
        return match.group(0)

    padrao = r'"(.*?)":\s*"((?:\\"|\\\\|\\/|\\b|\\f|\\n|\\r|\\t|\\u[0-9a-fA-F]{4}|[^"\\])*)"'
    return re.sub(padrao, substituir, texto_original)

def extrair_arquivos_lang(conteudo_jar: bytes, caminho_saida: str, nome_mod: str):
    """Extrai e processa arquivos de tradução do JAR."""
    import io
    global mod_alterado

    estatisticas = Estatisticas()
    
    with zipfile.ZipFile(io.BytesIO(conteudo_jar)) as jar:
        arquivos_lang = [f for f in jar.namelist() if '/lang/pt_br.json' in f or '/lang/en_us.json' in f]
        os.makedirs(caminho_saida, exist_ok=True)

        atualizado = False
        changelog = []
        arquivos = {}

        for caminho_arquivo in arquivos_lang:
            nome_arquivo = os.path.basename(caminho_arquivo)
            with jar.open(caminho_arquivo) as f:
                arquivos[nome_arquivo] = f.read()

        if 'en_us.json' in arquivos:
            if 'pt_br.json' not in arquivos:
                arquivos['pt_br.json'] = arquivos['en_us.json']

        for nome_arquivo in ['en_us.json', 'pt_br.json']:
            if nome_arquivo not in arquivos:
                continue

            conteudo_novo = arquivos[nome_arquivo]
            caminho_arquivo = os.path.join(caminho_saida, nome_arquivo)
            novo_hash = hash_arquivo(conteudo_novo)

            acao = 'atualizado'
            diff = ''

            if os.path.exists(caminho_arquivo):
                with open(caminho_arquivo, 'rb') as existente:
                    conteudo_antigo = existente.read()
                    if hash_arquivo(conteudo_antigo) == novo_hash:
                        continue
                    diff = diferenca_json(conteudo_antigo.decode(), conteudo_novo.decode())
                    if not diff.strip():
                        continue
            else:
                acao = 'adicionado'
                diff = diferenca_json("{}", conteudo_novo.decode())
                if not diff.strip():
                    continue

            if nome_arquivo == 'pt_br.json' and 'en_us.json' in arquivos:
                try:
                    pt_br_texto = conteudo_novo.decode()
                    en_us_texto = arquivos['en_us.json'].decode()
                    pt_br_dict = json.loads(pt_br_texto)
                    en_us_dict = json.loads(en_us_texto)
                    
                    # Análise de qualidade
                    qualidade, problemas = verificar_qualidade_traducao(en_us_dict, pt_br_dict)
                    if problemas:
                        changelog.append("### Problemas Encontrados\n\n" + "\n".join(problemas))
                    
                    # Atualizar estatísticas
                    estatisticas.total_strings = len(en_us_dict)
                    estatisticas.strings_traduzidas = len(pt_br_dict)
                    estatisticas.qualidade = qualidade
                    estatisticas.ultima_atualizacao = datetime.now()
                    
                    mesclado = substituir_valores_json(en_us_texto, pt_br_dict)
                    conteudo_novo = mesclado.encode('utf-8')
                    diff = diferenca_json(
                        open(caminho_arquivo, 'r', encoding='utf-8').read() if os.path.exists(caminho_arquivo) else '{}',
                        mesclado
                    )
                    if not diff.strip():
                        continue
                except json.JSONDecodeError as e:
                    logging.error(f"Erro ao mesclar JSON de {nome_mod}: {e}")
                    continue

            with open(caminho_arquivo, 'wb') as saida:
                saida.write(conteudo_novo)

            data = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            changelog.insert(0, f"## {nome_arquivo} {acao} em {data}\n\n{diff}")
            atualizado = True
            mod_alterado = True

        # Atualizar estatísticas globais
        estatisticas_globais['total_mods'] += 1
        if atualizado:
            estatisticas_globais['mods_atualizados'] += 1
        estatisticas_globais['strings_traduzidas'] += estatisticas.strings_traduzidas
        estatisticas_globais['ultima_atualizacao'] = datetime.now()

        status = '🟢 Atualizado' if atualizado else '🔴 Desatualizado'
        progresso = f"{estatisticas.calcular_progresso():.1f}%"
        qualidade = f"{estatisticas.qualidade:.1f}%"
        
        tabela_status[nome_mod] = (
            status,
            datetime.now().strftime('%d/%m/%Y'),
            progresso,
            qualidade
        )

        if changelog:
            atualizar_readme_mod(caminho_saida, nome_mod, changelog, estatisticas)

def atualizar_readme_mod(caminho_mod: str, nome_mod: str, changelog: List[str], estatisticas: Estatisticas):
    """Atualiza o README do mod com as alterações e estatísticas."""
    caminho_readme = os.path.join(caminho_mod, '..', 'README.md')
    
    estatisticas_texto = f"""
### Estatísticas

- Total de Strings: {estatisticas.total_strings}
- Strings Traduzidas: {estatisticas.strings_traduzidas}
- Progresso: {estatisticas.calcular_progresso():.1f}%
- Qualidade da Tradução: {estatisticas.qualidade:.1f}%
- Última Atualização: {estatisticas.ultima_atualizacao.strftime('%d/%m/%Y %H:%M:%S')}
"""
    
    bloco = f"\n\n{estatisticas_texto}\n\n### Registro de Alterações\n\n" + '\n\n'.join(changelog)
    
    if os.path.exists(caminho_readme):
        with open(caminho_readme, 'r+', encoding='utf-8') as f:
            conteudo_antigo = f.read()
            f.seek(0)
            f.write(f"# Arquivos de Tradução: {nome_mod}\n{bloco}\n{conteudo_antigo}")
    else:
        with open(caminho_readme, 'w', encoding='utf-8') as f:
            f.write(f"# Arquivos de Tradução: {nome_mod}\n{bloco}")

def atualizar_readme_principal():
    """Atualiza o README principal com o status atual das traduções."""
    if not mod_alterado:
        logging.info("Nenhuma alteração detectada. README.md principal não será modificado.")
        return

    cabecalho = f"""# 🌐 Status de Tradução dos Mods

Este repositório contém traduções de mods para Minecraft. O status das traduções é monitorado automaticamente.

### 📊 Estatísticas Globais

- Total de Mods: {estatisticas_globais['total_mods']}
- Mods Atualizados: {estatisticas_globais['mods_atualizados']}
- Total de Strings Traduzidas: {estatisticas_globais['strings_traduzidas']}
- Última Verificação: {estatisticas_globais['ultima_atualizacao'].strftime('%d/%m/%Y %H:%M:%S')}

## 📜 Lista de Mods

| Mod | Status | Última Atualização | Progresso | Qualidade |
|-----|--------|-------------------|-----------|-----------|"""

    linhas = [
        f"| **{mod}** | {status} | {data} | {progresso} | {qualidade} |"
        for mod, (status, data, progresso, qualidade) in sorted(tabela_status.items())
    ]

    with open(README_PRINCIPAL, 'w', encoding='utf-8') as f:
        f.write(cabecalho + '\n' + '\n'.join(linhas))

def main():
    """Função principal do programa."""
    try:
        # Criar pasta de backup se não existir
        os.makedirs(PASTA_BACKUP, exist_ok=True)
        
        # Criar backup antes de iniciar
        criar_backup()
        
        mods = carregar_mods(ARQUIVO_MODS)
        os.makedirs(PASTA_SAIDA, exist_ok=True)

        for nome_mod, id_mod in mods.items():
            try:
                logging.info(f"Processando: {nome_mod} ({id_mod})")
                versao = obter_ultima_versao(id_mod)
                nome_arquivo, conteudo = baixar_jar(versao)
                if not conteudo:
                    logging.error(f"Erro ao baixar: {nome_mod}")
                    continue
                pasta_mod = os.path.join(PASTA_SAIDA, nome_mod, 'lang')
                extrair_arquivos_lang(conteudo, pasta_mod, nome_mod)
                logging.info(f"Verificado: {pasta_mod}")
            except Exception as e:
                logging.error(f"Erro ao processar {nome_mod}: {e}")

        atualizar_readme_principal()
        logging.info("Processo concluído com sucesso!")

    except Exception as e:
        logging.error(f"Erro crítico: {e}")
        raise

if __name__ == '__main__':
    main()