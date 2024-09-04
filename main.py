from dotenv import load_dotenv
# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

import os
import multiprocessing as mp
import random
import logging
import time
from typing import List, Optional
from processo import Processo
from aprendiz import Aprendiz

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def executar_processo(id: int, total_processos: int, valor_proposta: Optional[int] = None):
    processo = Processo(id, total_processos)
    if valor_proposta is not None:
        resultado = processo.propor(valor_proposta)
        if resultado is not None:
            processo.logger.info(f"Consenso alcançado. Resultado final = {resultado}")
        else:
            processo.logger.warning(f"Falha ao alcançar consenso")
    else:
        processo.executar()

def executar_aprendiz(id: int, total_processos: int):
    aprendiz = Aprendiz(id, total_processos)
    aprendiz.executar()

if __name__ == "__main__":
    TOTAL_PROCESSOS_NUM = int(os.getenv('TOTAL_PROCESSOS_NUM'))
    PROPOSITORES_ATIVOS_NUM = int(os.getenv('PROPOSITORES_ATIVOS_NUM'))
    APRENDIZES_NUM = int(os.getenv('APRENDIZES_NUM', TOTAL_PROCESSOS_NUM))
    processos: List[mp.Process] = []
    aprendizes: List[mp.Process] = []

    # Inicia múltiplos processos
    for i in range(TOTAL_PROCESSOS_NUM):
        # Apenas os primeiros PROPOSITORES_ATIVOS_NUM processos serão propositores
        valor_proposta = random.randint(1, 100) if i < PROPOSITORES_ATIVOS_NUM else None
        p = mp.Process(target=executar_processo, args=(i, TOTAL_PROCESSOS_NUM, valor_proposta))
        processos.append(p)

    # Inicia múltiplos aprendizes
    for i in range(APRENDIZES_NUM):
        a = mp.Process(target=executar_aprendiz, args=(TOTAL_PROCESSOS_NUM + i, TOTAL_PROCESSOS_NUM))
        aprendizes.append(a)

    # Inicia primeiro os processos aceitadores, depois os propositores
    for i in range(PROPOSITORES_ATIVOS_NUM, TOTAL_PROCESSOS_NUM):
        processos[i].start()

    # Inicia os aprendizes
    for a in aprendizes:
        a.start()

    # Pequeno atraso para garantir que os aceitadores estejam prontos
    time.sleep(0.5)

    # Inicia os propositores
    for i in range(PROPOSITORES_ATIVOS_NUM):
        processos[i].start()

    # Aguarda todos os processos terminarem
    for p in processos:
        p.join(timeout=60)  # Aumenta o timeout para 60 segundos

    for a in aprendizes:
        a.join(timeout=60)  # Aumenta o timeout para 60 segundos

    # Verifica se algum processo ainda está em execução
    running_processes = [p for p in processos + aprendizes if p.is_alive()]
    if running_processes:
        print(f"Alguns processos ainda estão em execução: {len(running_processes)}")
    else:
        print("Todos os processos concluíram com sucesso")

    # Verifica o valor decidido pelos aprendizes
    for i, a in enumerate(aprendizes):
        aprendiz_id = TOTAL_PROCESSOS_NUM + i
        print(f"Aprendiz {aprendiz_id} concluiu com status: {a.exitcode}")