"""Prepara um CSV de coleta para teste técnico restrito, sem imputar indicadores.

Uso: python -m scripts.preparar_csv_coleta --entrada /caminho/coleta.csv --ano-referencia 2026
O original é preservado. Os arquivos de saída contêm dados individuais e ficam fora do Git.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path

from pipeline.codebook import classificar_cargo, normalizar

ROOT = Path(__file__).resolve().parents[1]
ALVOS = {
    'Liderança ou Gerência': 'Indicador_Lideranca',
    'Progressão Interna': 'Indicador_Progressao',
    'Empreendeu': 'Indicador_Empreendedorismo',
    'Mudança de Área': 'Indicador_Mudanca_Area',
}
OBRIGATORIAS = ['Curso de Graduação', 'Ano de Conclusão', 'Cargo Atual', *ALVOS]
COLUNAS = ['ID_Egresso', 'Curso_de_Graduacao', 'Ano_de_Conclusao', 'Periodo_Conclusao',
           'Tempo_desde_Conclusao', 'Genero', 'Faixa_Etaria', 'UF_Nascimento',
           'Regiao_Nascimento', 'Categoria_Cargo', 'Tipo_Instituicao', *ALVOS.values()]


def preparar(entrada: Path, saida: Path, ano_referencia: int) -> dict:
    entrada, saida = entrada.resolve(), saida.resolve()
    if entrada == saida:
        raise ValueError('A saída deve ser diferente da coleta original.')
    if saida.is_relative_to(ROOT) and not saida.is_relative_to(ROOT / 'data' / 'privado'):
        raise ValueError('Dentro do repositório, salve somente em data/privado, que é ignorado pelo Git.')
    if not 1900 <= ano_referencia <= 2100:
        raise ValueError('Ano de referência inválido.')
    conteudo = entrada.read_bytes()
    texto = conteudo.decode('utf-8-sig')
    separador = csv.Sniffer().sniff(texto[:12000], delimiters=',;\t')
    leitor = csv.DictReader(io.StringIO(texto), dialect=separador)
    faltam = sorted(set(OBRIGATORIAS) - set(leitor.fieldnames or []))
    if faltam:
        raise ValueError('Colunas necessárias ausentes: ' + ', '.join(faltam))
    linhas, aceitas, excluidas = list(leitor), [], []
    motivos = Counter()
    for numero, linha in enumerate(linhas, start=2):
        erros = []
        curso = (linha.get('Curso de Graduação') or '').strip()
        if normalizar(curso) in ('', 'nao especificado', 'nao informado', 'sem informacao'):
            erros.append('curso_nao_especificado')
        try:
            ano = int((linha.get('Ano de Conclusão') or '').strip())
            if not 1900 <= ano <= ano_referencia:
                raise ValueError
        except ValueError:
            erros.append('ano_ausente_ou_invalido')
        indicadores = {}
        for origem, destino in ALVOS.items():
            valor = normalizar(linha.get(origem))
            if valor not in ('sim', 'nao'):
                erros.append('indicador_ausente:' + origem)
            else:
                indicadores[destino] = int(valor == 'sim')
        if erros:
            excluidas.append({'linha_csv': numero, 'motivos': erros})
            motivos.update(erros)
            continue
        inicio = (ano // 5) * 5
        periodo = f'{inicio}–{inicio + 4}'
        if 2010 <= ano <= 2014:
            periodo = '2010–2014'
        elif 2015 <= ano <= 2019:
            periodo = '2015–2019'
        elif 2020 <= ano <= 2025:
            periodo = '2020–2025'
        aceitas.append({
            'ID_Egresso': f'AV{numero - 1:06d}', 'Curso_de_Graduacao': curso,
            'Ano_de_Conclusao': ano, 'Periodo_Conclusao': periodo,
            'Tempo_desde_Conclusao': ano_referencia - ano,
            'Genero': (linha.get('Gênero') or '').strip() or 'Sem Informação',
            'Faixa_Etaria': 'Sem Informação', 'UF_Nascimento': 'Sem Informação',
            'Regiao_Nascimento': 'Sem Informação',
            'Categoria_Cargo': classificar_cargo(linha.get('Cargo Atual')),
            'Tipo_Instituicao': 'Sem Informação', **indicadores,
        })
    if not aceitas:
        raise ValueError('Nenhum caso completo; revise a coleta antes de usar o painel.')
    saida.parent.mkdir(parents=True, exist_ok=True)
    with saida.open('w', encoding='utf-8-sig', newline='') as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
        escritor.writeheader()
        escritor.writerows(aceitas)
    relatorio = {
        'finalidade': 'teste técnico exploratório; não substitui a base auditada da pesquisa',
        'sha256_original': hashlib.sha256(conteudo).hexdigest(),
        'sha256_preparada': hashlib.sha256(saida.read_bytes()).hexdigest(),
        'ano_referencia': ano_referencia, 'linhas_originais': len(linhas),
        'casos_completos': len(aceitas), 'linhas_excluidas': len(excluidas),
        'motivos_sobrepostos': dict(motivos), 'revisar_na_coleta_original': excluidas,
        'campos_sem_dados': ['Faixa_Etaria', 'UF_Nascimento', 'Regiao_Nascimento', 'Tipo_Instituicao'],
        'categoria_cargo': 'sugestão por regras do codebook; requer revisão manual',
        'indicadores': 'Sim e Não preservados; não informado não foi convertido em zero',
        'limite': 'seleção de casos completos pode introduzir viés; rever antes da aplicação principal',
    }
    saida.with_suffix('.auditoria.json').write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding='utf-8')
    return relatorio


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entrada', type=Path, required=True)
    parser.add_argument('--saida', type=Path, default=ROOT / 'data' / 'privado' / 'base_avaliacao.csv')
    parser.add_argument('--ano-referencia', type=int, required=True)
    args = parser.parse_args()
    relatorio = preparar(args.entrada, args.saida, args.ano_referencia)
    print(json.dumps({k: relatorio[k] for k in ['linhas_originais', 'casos_completos', 'linhas_excluidas', 'ano_referencia']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
