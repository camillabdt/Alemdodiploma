"""A preparação não transforma dados ausentes em evidência negativa."""
import csv
import hashlib

from scripts.preparar_csv_coleta import preparar


def test_preparacao_preserva_original_e_separa_ausencia_de_nao(tmp_path):
    entrada, saida = tmp_path / 'coleta.csv', tmp_path / 'restrito.csv'
    campos = ['Nome', 'Curso de Graduação', 'Ano de Conclusão', 'Cargo Atual',
              'Local de Trabalho', 'Liderança ou Gerência', 'Progressão Interna', 'Empreendeu', 'Mudança de Área']
    original = dict(zip(campos, ['Pessoa fictícia', 'Curso de teste', '2020', 'Desenvolvedor',
                                'Empresa fictícia', 'Sim', 'Não', 'Não', 'Não']))
    with entrada.open('w', newline='') as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows([original, {**original, 'Liderança ou Gerência': 'Não informado'},
                            {**original, 'Ano de Conclusão': ''}])
    antes = hashlib.sha256(entrada.read_bytes()).hexdigest()
    resultado = preparar(entrada, saida, 2026)
    assert resultado['linhas_originais'] == 3 and resultado['casos_completos'] == 1
    assert resultado['linhas_excluidas'] == 2
    assert resultado['motivos_sobrepostos']['indicador_ausente:Liderança ou Gerência'] == 1
    assert resultado['motivos_sobrepostos']['ano_ausente_ou_invalido'] == 1
    assert hashlib.sha256(entrada.read_bytes()).hexdigest() == antes
    with saida.open(encoding='utf-8-sig') as arquivo:
        dados = list(csv.DictReader(arquivo))
    assert 'Nome' not in dados[0] and 'Local de Trabalho' not in dados[0]
    assert 'Pessoa fictícia' not in saida.read_text(encoding='utf-8-sig')
    assert dados[0]['Indicador_Lideranca'] == '1' and dados[0]['Indicador_Progressao'] == '0'
    assert dados[0]['Tempo_desde_Conclusao'] == '6'
    assert dados[0]['UF_Nascimento'] == dados[0]['Tipo_Instituicao'] == 'Sem Informação'
