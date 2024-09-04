from dotenv import load_dotenv
# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

import os
import multiprocessing as mp
import random
import logging
from typing import List, Optional
from processo import Processo
from time import sleep

# Configuração do logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def executar_processo(id: int, total_processos: int, valor_proposta: Optional[int] = None):
    processo = Processo(id, total_processos)
    if valor_proposta is not None:
        sleep(2)
        resultado = None
        rodadas_count = 0
        while resultado is None:
            rodadas_count += 1
            resultado = processo.propor(valor_proposta)
        processo.logger.info(f"Resultado final = {resultado}")
    
    # Caso contrário, executa como um aceitador
    else:
        processo.executar()

if __name__ == "__main__":
    TOTAL_PROCESSOS_NUM = int(os.getenv('TOTAL_PROCESSOS_NUM'))
    PROPOSITORES_ATIVOS_NUM = int(os.getenv('PROPOSITORES_ATIVOS_NUM'))
    processos: List[mp.Process] = []

    # Inicia múltiplos processos
    for i in range(TOTAL_PROCESSOS_NUM):
        # Os N (PROPOSITORES_ATIVOS_NUM) primeiros processos propõem um valor aleatório, os outros são aceitadores
        valor_proposta = random.randint(1, 100) if i < PROPOSITORES_ATIVOS_NUM else None
        p = mp.Process(target=executar_processo, args=(i, TOTAL_PROCESSOS_NUM, valor_proposta))
        processos.append(p)

    # Garante a inicialização dos processos aceitadores antes dos propositores
    for p in reversed(processos):
        p.start()

    # Aguarda todos os processos terminarem
    for p in processos:
        p.join()