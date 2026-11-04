"""Contrato HTTP da migração React, sem usar dados reais."""
import io
import json

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from api.main import app, sessions


@pytest.fixture
def client():
    sessions.clear()
    with TestClient(app) as client:
        yield client
    sessions.clear()


def auth(client):
    session = client.post('/api/demo').json()
    return {'Authorization': 'Bearer ' + session['token']}, session


def test_demo_dashboard_and_filter(client):
    headers, session = auth(client)
    result = client.post('/api/dashboard', headers=headers, json={})
    assert result.status_code == 200
    data = result.json()
    assert not data['blocked'] and data['total'] == session['total']
    assert 'ID_Egresso' not in result.text
    course = session['options']['Curso_de_Graduacao'][0]
    result = client.post('/api/dashboard', headers=headers,
                         json={'filters': {'Curso_de_Graduacao': [course]}}).json()
    assert 10 <= result['total'] < session['total']
    assert [row['label'] for row in result['distributions']['Curso_de_Graduacao']['rows']] == [course]


def test_empty_filter_blocks_and_export_refuses(client):
    headers, _ = auth(client)
    query = {'filters': {'Curso_de_Graduacao': []}}
    data = client.post('/api/dashboard', headers=headers, json=query).json()
    assert data['blocked'] and 'distributions' not in data and 'total' not in data
    assert client.post('/api/export/json', headers=headers, json=query).status_code == 422


def test_invalid_session_filter_and_logout(client):
    assert client.post('/api/dashboard', json={}).status_code == 401
    headers, _ = auth(client)
    assert client.post('/api/dashboard', headers=headers, json={'filters': {'Nome': ['x']}}).status_code == 422
    assert client.post('/api/dashboard', headers=headers, json={'years': [2025, 2010]}).status_code == 422
    assert client.delete('/api/session', headers=headers).status_code == 200
    assert client.post('/api/dashboard', headers=headers, json={}).status_code == 401


def upload(client, df, **fields):
    return client.post('/api/import', files={'file': ('base.csv', df.to_csv(index=False, sep=';').encode('utf-8-sig'), 'text/csv')}, data=fields)


def test_import_other_course_one_year_and_population(client, df_exemplo):
    df = df_exemplo.copy()
    df['Curso_de_Graduacao'] = 'Pedagogia'
    df['Ano_de_Conclusao'] = 2026
    df['Tempo_desde_Conclusao'] = 0
    df['Periodo_Conclusao'] = '2026–2030'
    result = upload(client, df, institution='Teste', population=json.dumps({'Pedagogia': 2 * len(df)}))
    assert result.status_code == 200, result.text
    session = result.json()
    assert session['years'] == [2026, 2026]
    headers = {'Authorization': 'Bearer ' + session['token']}
    data = client.post('/api/dashboard', headers=headers, json={}).json()
    assert data['coverage'][0]['value'] == 50
    assert data['distributions']['Curso_de_Graduacao']['rows'][0]['label'] == 'Pedagogia'
    exported = client.post('/api/export/json', headers=headers, json={})
    assert exported.status_code == 200 and 'Pedagogia' in exported.text
    assert 'Engenharia de Software' not in exported.text


@pytest.mark.parametrize('change', ['identifier', 'missing', 'duplicate', 'indicator', 'empty', 'population'])
def test_import_rejects_invalid_data(client, df_exemplo, change):
    df = df_exemplo.copy()
    fields = {}
    if change == 'identifier': df['Nome'] = 'Pessoa identificável'
    if change == 'missing': df = df.drop(columns=['Categoria_Cargo'])
    if change == 'duplicate': df.loc[1, 'ID_Egresso'] = df.loc[0, 'ID_Egresso']
    if change == 'indicator': df.loc[0, 'Indicador_Lideranca'] = 2
    if change == 'empty': df.loc[0, 'Curso_de_Graduacao'] = None
    if change == 'population': fields['population'] = '{"Ciência da Computação": 1}'
    assert upload(client, df, **fields).status_code == 422
    assert not sessions


@pytest.mark.parametrize('fmt,signature', [('pdf', b'%PDF'), ('html', b'<!doctype html>'), ('md', b'# '), ('csv', b'PK'), ('json', b'{')])
def test_all_export_formats(client, fmt, signature):
    headers, _ = auth(client)
    result = client.post('/api/export/' + fmt, headers=headers, json={})
    assert result.status_code == 200
    assert result.content.startswith(signature)
    assert 'attachment' in result.headers['content-disposition']


def test_tiny_indicator_is_not_revealed(client, df_exemplo):
    df = df_exemplo.copy()
    df['Indicador_Lideranca'] = 0
    df.loc[0, 'Indicador_Lideranca'] = 1
    response = upload(client, df)
    headers = {'Authorization': 'Bearer ' + response.json()['token']}
    data = client.post('/api/dashboard', headers=headers, json={}).json()
    leader = next(i for i in data['indicators'] if i['key'] == 'Indicador_Lideranca')
    assert leader['value'] is None and leader['count'] is None and all(row['count'] == 0 or row['count'] >= 5 for row in leader['by_course'])
    assert client.post('/api/explanations/Indicador_Lideranca', headers=headers).status_code == 422


def test_template_and_payload_size(client):
    assert 'ID_Egresso' in client.get('/api/template').text
    result = client.post('/api/import', files={'file': ('big.csv', b'x' * (5 * 1024 * 1024 + 1))})
    assert result.status_code == 413


def test_explanations_http_and_cache(client):
    headers, _ = auth(client)
    result = client.post('/api/explanations/Indicador_Lideranca', headers=headers)
    assert result.status_code == 200
    data = result.json()
    assert set(data['auc']) == {'Regressão logística', 'Random forest'}
    assert {r['Fator'] for r in data['importance']} == {'Curso', 'Anos de formado', 'Origem', 'Tipo de instituição'}
    assert 'ID_Egresso' not in result.text
    again = client.post('/api/explanations/Indicador_Lideranca', headers=headers)
    assert again.json() == data


def test_static_frontend_served_after_build(client):
    from api.main import DIST
    if not DIST.exists():
        pytest.skip('compile o React para verificar a entrega dos arquivos estáticos')
    response = client.get('/')
    assert response.status_code == 200
    assert 'Alumni View' in response.text


def test_sem_rotas_busca_ou_streamlit(client):
    schema=client.get('/openapi.json').json()
    assert not any('search' in p or 'busca' in p or 'linkedin' in p for p in schema['paths'])
    assert schema['info']['version'] == '3.0.0'


def test_import_rejeita_ano_referencia_inconsistente(client, df_exemplo):
    df=df_exemplo.copy()
    df.loc[0,'Tempo_desde_Conclusao'] += 1
    response=upload(client,df)
    assert response.status_code == 422
    assert 'referência' in response.text


def test_xai_export_requer_calculo_e_sessao(client):
    headers,_=auth(client)
    assert client.get('/api/explanations/Indicador_Lideranca/export').status_code==401
    assert client.get('/api/explanations/Indicador_Lideranca/export',headers=headers).status_code==409


def test_xai_sessoes_isoladas_e_cache(client,monkeypatch):
    from app.core import xai
    calls=[]
    def fake(*args,**kwargs):
        calls.append(1)
        return {'n':len(args[0]),'protocol':{'seed':2026},'importance':[]}
    monkeypatch.setattr(xai,'explicar_validado',fake)
    first,_=auth(client)
    second,_=auth(client)
    a=client.post('/api/explanations/Indicador_Lideranca',headers=first).json()
    assert a['source']=='exemplo'
    assert client.post('/api/explanations/Indicador_Lideranca',headers=first).json()==a
    assert len(calls)==1
    assert client.get('/api/explanations/Indicador_Lideranca/export',headers=second).status_code==409
    exported=client.get('/api/explanations/Indicador_Lideranca/export',headers=first)
    assert exported.status_code==200 and 'data' not in exported.json()


def test_export_mesma_protecao_de_taxas_do_painel(client,df_exemplo):
    df=df_exemplo.copy()
    df['Indicador_Lideranca']=0
    df.loc[0,'Indicador_Lideranca']=1
    response=upload(client,df)
    headers={'Authorization':'Bearer '+response.json()['token']}
    exported=client.post('/api/export/json',headers=headers,json={}).json()
    rows=exported['secoes'][0]['tabelas'][0]['linhas']
    row=next(r for r in rows if r['Indicador']=='Liderança ou gerência')
    assert row['Valor']=='Suprimido'
