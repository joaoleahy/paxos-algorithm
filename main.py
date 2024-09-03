import multiprocessing as mp
import random
import logging
from typing import List, Optional
from processo import Processo

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def executar_processo(id: int, total_processos: int, valor_proposta: Optional[int] = None):
    processo = Processo(id, total_processos)
    if valor_proposta is not None:
        # Se um valor foi proposto, inicia o processo de consenso
        resultado = processo.propor(valor_proposta)
        processo.logger.info(f"Resultado final = {resultado}")
    else:
        # Caso contrário, executa como um aceitador
        processo.executar()

if __name__ == "__main__":
    total_processos = 5
    processos: List[mp.Process] = []

    # Inicia múltiplos processos
    for i in range(total_processos):
        # O primeiro processo (i=0) propõe um valor aleatório, os outros são aceitadores
        valor_proposta = random.randint(1, 100) if i == 0 else None
        p = mp.Process(target=executar_processo, args=(i, total_processos, valor_proposta))
        processos.append(p)
        p.start()

    # Aguarda todos os processos terminarem
    for p in processos:
        p.join()