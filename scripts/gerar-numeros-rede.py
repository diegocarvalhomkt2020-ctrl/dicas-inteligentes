"""Gera src/data/rede-numeros.json a partir dos dados reais dos sites da rede.

Roda com: python scripts/gerar-numeros-rede.py
Lê os arquivos produtos*.json de cada site-irmão (pastas ao lado deste repositório)
e receitas.json do Bela Receita. Não inventa nada: só soma, conta e tira média
do que já está publicado. Rodar de novo sempre que um site ganhar produto novo.
"""
import glob
import json
import os
from datetime import date

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SITES = [
    ('casa-pratica', 'Casa Prática', 'https://casapratica.dicasinteligentes.com'),
    ('amigo-pet', 'Amigo Pet', 'https://amigopet.dicasinteligentes.com'),
    ('cafe-ideal', 'Café Ideal', 'https://cafe.dicasinteligentes.com'),
    ('mundo-bebe', 'Mundo Bebê', 'https://mundobebe.dicasinteligentes.com'),
]


def produtos_de(obj, achados):
    if isinstance(obj, dict):
        if 'precoMin' in obj and 'nota' in obj:
            achados.append(obj)
            return
        for v in obj.values():
            produtos_de(v, achados)
    elif isinstance(obj, list):
        for v in obj:
            produtos_de(v, achados)


por_site = []
todos = []
for pasta, nome, url in SITES:
    lista = []
    for arq in sorted(glob.glob(os.path.join(RAIZ, pasta, 'src', 'data', 'produtos*.json'))):
        with open(arq, encoding='utf-8') as f:
            produtos_de(json.load(f), lista)
    ids = set()
    unicos = []
    for p in lista:
        chave = p.get('id') or p.get('nome')
        if chave in ids:
            continue
        ids.add(chave)
        unicos.append(p)
    notas = [p['nota'] for p in unicos if p.get('nota')]
    com_contra = sum(1 for p in unicos if p.get('contra'))
    por_site.append({
        'nome': nome,
        'url': url,
        'produtos': len(unicos),
        'comDefeitoDeclarado': com_contra,
        'precoMenor': min(p['precoMin'] for p in unicos),
        'precoMaior': max(p['precoMax'] for p in unicos),
        'notaMedia': round(sum(notas) / len(notas), 2),
        'notaMenor': min(notas),
        'notaMaior': max(notas),
        'avaliacoes': sum(p.get('avaliacoes') or 0 for p in unicos),
    })
    todos.extend(unicos)

with open(os.path.join(RAIZ, 'bela-receita', 'src', 'data', 'receitas.json'), encoding='utf-8') as f:
    receitas = len(json.load(f)['receitas'])

notas_todas = [p['nota'] for p in todos if p.get('nota')]
saida = {
    'geradoEm': date.today().isoformat(),
    'receitas': receitas,
    'produtos': len(todos),
    'comDefeitoDeclarado': sum(1 for p in todos if p.get('contra')),
    'notaMedia': round(sum(notas_todas) / len(notas_todas), 2),
    'notaMenor': min(notas_todas),
    'abaixoDe4': sum(1 for n in notas_todas if n < 4),
    'de45ouMais': sum(1 for n in notas_todas if n >= 4.5),
    'avaliacoes': sum(p.get('avaliacoes') or 0 for p in todos),
    'sites': por_site,
}
destino = os.path.join(RAIZ, 'dicas-inteligentes', 'src', 'data', 'rede-numeros.json')
with open(destino, 'w', encoding='utf-8') as f:
    json.dump(saida, f, ensure_ascii=False, indent=2)
print(json.dumps(saida, ensure_ascii=False, indent=2))
