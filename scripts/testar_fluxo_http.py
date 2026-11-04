"""Teste técnico via servidor HTTP real, exclusivamente com a base fictícia."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import httpx

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://camillabdt.github.io'
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
env = {**os.environ, 'ALUMNI_ALLOWED_ORIGINS': ORIGIN}
server = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'api.main:app',
    '--host', '127.0.0.1', '--port', str(port)], cwd=ROOT, env=env,
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    with httpx.Client(base_url=f'http://127.0.0.1:{port}', timeout=90, trust_env=False) as client:
        for _ in range(100):
            if server.poll() is not None:
                raise RuntimeError('O servidor encerrou antes do teste.')
            try:
                ready = client.get('/api/health')
                if ready.status_code == 200:
                    break
            except httpx.ConnectError:
                pass
            time.sleep(0.1)
        else:
            raise RuntimeError('O servidor não iniciou em dez segundos.')
        assert ready.json()['application'] == 'Alumni View'
        html = client.get('/')
        assert html.status_code == 200 and 'Alumni View' in html.text
        preflight = {'Origin': ORIGIN, 'Access-Control-Request-Method': 'POST',
                     'Access-Control-Request-Headers': 'authorization,content-type'}
        result = client.options('/api/dashboard', headers=preflight)
        assert result.status_code == 200
        assert result.headers['access-control-allow-origin'] == ORIGIN
        result = client.options('/api/dashboard', headers={**preflight, 'Origin': 'https://outro.example'})
        assert result.status_code == 400 and 'access-control-allow-origin' not in result.headers
        # Exercita importação, não o endpoint de demonstração; a origem continua fictícia.
        csv = (ROOT / 'data/exemplo/dataset_exemplo.csv').read_bytes()
        response = client.post('/api/import', files={'file': ('teste-ficticio.csv', csv, 'text/csv')})
        assert response.status_code == 200, response.text
        session = response.json()
        headers = {'Authorization': 'Bearer ' + session['token'], 'Origin': ORIGIN}
        query = {'filters': {'Curso_de_Graduacao': ['Engenharia de Software']}, 'years': [2020, 2025]}
        response = client.post('/api/dashboard', headers=headers, json=query)
        assert response.status_code == 200
        data = response.json()
        assert not data['blocked'] and data['total'] < session['total']
        for fmt in ['pdf', 'html', 'md', 'json', 'csv']:
            result = client.post('/api/export/' + fmt, headers=headers, json=query)
            assert result.status_code == 200, (fmt, result.text[:100])
            assert 'attachment' in result.headers['content-disposition']
        response = client.post('/api/explanations/Indicador_Lideranca', headers=headers)
        assert response.status_code == 200, response.text
        xai = response.json()
        assert set(xai['auc']) == {'Regressão logística', 'Random forest'}
        assert max(xai['additivity_error'].values()) < 1e-7
        result = client.get('/api/explanations/Indicador_Lideranca/export', headers=headers)
        assert result.status_code == 200 and result.json() == xai
        assert 'ID_Egresso' not in result.text
        assert client.delete('/api/session', headers=headers).status_code == 200
        assert client.post('/api/dashboard', headers=headers, json={}).status_code == 401
        print(json.dumps({'status': 'ok', 'base': 'fictícia; não é o CSV da pesquisa',
            'importacao': True, 'filtros': True, 'exportacoes': ['pdf', 'html', 'md', 'json', 'csv/zip'],
            'xai_dois_modelos': True, 'aditividade': True, 'exportacao_xai': True,
            'encerramento': True, 'cors_origem_permitida_e_bloqueada': True}, ensure_ascii=False))
finally:
    server.terminate()
    try:
        server.wait(timeout=10)
    except subprocess.TimeoutExpired:
        server.kill()
        server.wait()
