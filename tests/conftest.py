import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import DADOS_EXEMPLO, DADOS_PUBLICOS  # noqa: E402
from app.core.data import ler_dados  # noqa: E402

TEM_BASE_REAL = DADOS_PUBLICOS.exists()
requer_base_real = pytest.mark.skipif(
    not TEM_BASE_REAL, reason="base real ausente (esperado no repositório público)"
)


@pytest.fixture(scope="session")
def df_exemplo():
    return ler_dados(DADOS_EXEMPLO)


@pytest.fixture(scope="session")
def df_real():
    if not TEM_BASE_REAL:
        pytest.skip("base real ausente")
    return ler_dados(DADOS_PUBLICOS)
