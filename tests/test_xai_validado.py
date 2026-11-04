"""Verificação do método fora da amostra e do contrato agregado do laboratório."""
import numpy as np
import pandas as pd
import pytest
from app.core import xai


def test_xai_fora_amostra_metrica_referencia_e_aditividade(df_exemplo):
    result = xai.explicar_validado(df_exemplo, 'Indicador_Lideranca', repeticoes=1, tamanho_fundo=6)
    assert result['protocol']['explanation_folds'] == 5
    assert result['protocol']['scope'] == 'base completa'
    assert result['metrics']['Referência (prevalência)']['auc']['mean'] == 0.5
    assert len(result['protocol']['data_sha256']) == 64
    for name in result['auc']:
        assert result['additivity_error'][name] < 1e-7
        assert 0 <= result['metrics'][name]['ap']['mean'] <= 1
        assert 0 <= result['metrics'][name]['brier']['mean'] <= 1
        for rows in result['effects'][name].values():
            assert all(row['n'] >= 5 for row in rows)
    assert 'ID_Egresso' not in str(result) and 'predictions' not in result


def test_fatores_ausentes_sao_identificados_sem_alegar_irrelevancia(df_exemplo):
    df = df_exemplo.copy()
    df['UF_Nascimento'] = 'Sem Informação'
    df['Tipo_Instituicao'] = 'Sem Informação'
    result = xai.explicar_validado(df, 'Indicador_Lideranca', repeticoes=1, tamanho_fundo=6)
    qualidade = {q['factor']: q['status'] for q in result['factor_quality']}
    assert qualidade['Origem'] == qualidade['Tipo de instituição'] == 'sem informação'
    assert any('não demonstra irrelevância' in w for w in result['warnings'])
    for row in result['importance']:
        if row['Fator'] in ['Origem', 'Tipo de instituição']:
            assert all(abs(row[nome]) < 1e-10 for nome in result['auc'])


@pytest.mark.parametrize('kind', ['pequena','uma_classe','minoria_rara','alvo_invalido'])
def test_xai_recusa_bases_sem_condicao(df_exemplo, kind):
    df = df_exemplo.copy()
    alvo = 'Indicador_Lideranca'
    if kind == 'pequena': df = df.head(20)
    if kind == 'uma_classe': df[alvo] = 0
    if kind == 'minoria_rara':
        df[alvo] = 0
        df.loc[df.index[:5],alvo] = 1
    if kind == 'alvo_invalido': alvo = 'Indicador_Mudanca_Area'
    with pytest.raises(ValueError):xai.explicar_validado(df, alvo)
