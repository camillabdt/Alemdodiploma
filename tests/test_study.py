"""Carregamento automático e exportação, usando apenas dados fictícios."""
import base64

import pytest
from fastapi.testclient import TestClient

from api.main import app, sessions, study_dataframe


@pytest.fixture
def client(monkeypatch, df_exemplo):
    study_dataframe.cache_clear()
    sessions.clear()
    encoded = base64.b64encode(df_exemplo.to_csv(index=False).encode("utf-8-sig")).decode()
    monkeypatch.setenv("ALUMNI_STUDY_CSV_BASE64", encoded)
    with TestClient(app) as c:
        yield c
    sessions.clear()
    study_dataframe.cache_clear()


def test_study_opens_without_upload_and_reuses_session(client, df_exemplo):
    response = client.post('/api/study')
    assert response.status_code == 200
    study = response.json()
    assert study['source'] == 'estudo' and study['total'] == len(df_exemplo)
    assert study['population'] == {}  # Não inventa cobertura institucional.
    assert 'ID_Egresso' not in response.text and 'records' not in study
    headers = {'Authorization': 'Bearer ' + study['token']}
    assert client.post('/api/study', headers=headers).json()['token'] == study['token']
    assert len(sessions) == 1
    dashboard = client.post('/api/dashboard', headers=headers, json={})
    assert dashboard.status_code == 200 and dashboard.json()['total'] == len(df_exemplo)
    assert 'ID_Egresso' not in dashboard.text
    for fmt, signature in [('pdf', b'%PDF'), ('json', b'{')]:
        exported = client.post('/api/export/' + fmt, headers=headers, json={})
        assert exported.status_code == 200 and exported.content.startswith(signature)


@pytest.mark.parametrize('config', ['ausente', 'base64_invalido', 'coluna_identificavel'])
def test_study_configuration_failure_is_explicit(client, monkeypatch, tmp_path, df_exemplo, config):
    study_dataframe.cache_clear()
    if config == 'ausente':
        monkeypatch.delenv('ALUMNI_STUDY_CSV_BASE64')
        monkeypatch.setenv('ALUMNI_STUDY_CSV_PATH', str(tmp_path/'ausente.csv'))
    elif config == 'base64_invalido':
        monkeypatch.setenv('ALUMNI_STUDY_CSV_BASE64', 'conteudo-invalido!')
    else:
        bad = df_exemplo.copy()
        bad['Nome'] = 'Não publicar'
        monkeypatch.setenv('ALUMNI_STUDY_CSV_BASE64', base64.b64encode(bad.to_csv(index=False).encode()).decode())
    result = client.post('/api/study')
    assert result.status_code == 503
    assert result.json()['detail'].startswith('A base do estudo está indisponível')
    assert 'Nome' not in result.text and 'ausente.csv' not in result.text
    assert not sessions
