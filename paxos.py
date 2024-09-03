import multiprocessing as mp
import random
import time
import socket
import pickle
import logging
import sys
from enum import Enum
from typing import Optional, Tuple, List

# Configuração de logging para acompanhar o processo de consenso
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Constantes para configuração da rede
PORTA_BASE = 5000
TIMEOUT = 2.0

# Enumeração dos tipos de mensagens usadas no protocolo Paxos
class TipoMensagem(Enum):
    PREPARE = 1  # Fase 1a: Propositor solicita promessas
    PROMISE = 2  # Fase 1b: Aceitador promete considerar a proposta
    ACCEPT = 3   # Fase 2a: Propositor solicita aceitação
    ACCEPTED = 4 # Fase 2b: Aceitador aceita a proposta
    DECIDE = 5   # Fase 3: Propositor anuncia a decisão

# Classe para representar as mensagens trocadas entre os processos
class Mensagem:
    def __init__(self, tipo: TipoMensagem, remetente: int, numero: int, valor: Optional[int] = None):
        self.tipo = tipo
        self.remetente = remetente
        self.numero = numero
        self.valor = valor

# Classe principal que implementa o algoritmo Paxos
class Processo:
    def __init__(self, id: int, total_processos: int):
        self.id = id
        self.total_processos = total_processos
        self.numero_proposta = 0
        self.valor_aceito = None
        self.numero_aceito = 0
        self.decidido = False
        self.logger = logging.getLogger(f"Processo-{self.id}")
        
        # Configuração do socket para comunicação via rede
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('localhost', PORTA_BASE + self.id))
        self.socket.settimeout(TIMEOUT)

    # Método para enviar mensagens para outros processos
    def enviar_mensagem(self, destino: int, mensagem: Mensagem):
        try:
            self.socket.sendto(pickle.dumps(mensagem), ('localhost', PORTA_BASE + destino))
            self.logger.debug(f"Mensagem enviada para {destino}: {mensagem.tipo}")
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem para {destino}: {e}")

    # Método para receber mensagens de outros processos
    def receber_mensagem(self) -> Optional[Mensagem]:
        try:
            data, _ = self.socket.recvfrom(1024)
            mensagem = pickle.loads(data)
            self.logger.debug(f"Mensagem recebida: {mensagem.tipo} de {mensagem.remetente}")
            return mensagem
        except socket.timeout:
            return None
        except Exception as e:
            self.logger.error(f"Erro ao receber mensagem: {e}")
            return None

    # Método principal para propor um valor e iniciar o processo de consenso
    def propor(self, valor: int):
        self.numero_proposta = max(self.numero_proposta, self.numero_aceito) + 1
        self.logger.info(f"Iniciando proposta com número {self.numero_proposta} e valor {valor}")

        # Fase 1: Prepare
        contagem_promessas = 0
        maior_numero_aceito = 0
        valor_maior_numero = None

        # Envia mensagens PREPARE para todos os outros processos
        for i in range(self.total_processos):
            if i != self.id:
                self.enviar_mensagem(i, Mensagem(TipoMensagem.PREPARE, self.id, self.numero_proposta))

        # Aguarda promessas dos outros processos
        while contagem_promessas <= self.total_processos // 2:
            mensagem = self.receber_mensagem()
            if mensagem and mensagem.tipo == TipoMensagem.PROMISE:
                contagem_promessas += 1
                if mensagem.numero > maior_numero_aceito:
                    maior_numero_aceito = mensagem.numero
                    valor_maior_numero = mensagem.valor

        # Fase 2: Accept
        valor_proposta = valor_maior_numero if valor_maior_numero else valor
        contagem_aceites = 0

        # Envia mensagens ACCEPT para todos os outros processos
        for i in range(self.total_processos):
            if i != self.id:
                self.enviar_mensagem(i, Mensagem(TipoMensagem.ACCEPT, self.id, self.numero_proposta, valor_proposta))

        # Aguarda aceitações dos outros processos
        while contagem_aceites <= self.total_processos // 2:
            mensagem = self.receber_mensagem()
            if mensagem and mensagem.tipo == TipoMensagem.ACCEPTED:
                contagem_aceites += 1

        # Se a maioria aceitou, anuncia a decisão
        if contagem_aceites > self.total_processos // 2:
            self.decidido = True
            self.valor_aceito = valor_proposta
            self.logger.info(f"Consenso alcançado com valor {valor_proposta}")
            for i in range(self.total_processos):
                if i != self.id:
                    self.enviar_mensagem(i, Mensagem(TipoMensagem.DECIDE, self.id, self.numero_proposta, valor_proposta))
            return valor_proposta

        self.logger.warning("Falha ao alcançar consenso")
        return None

    # Método para executar o processo como aceitador
    def executar(self):
        while not self.decidido:
            mensagem = self.receber_mensagem()
            if not mensagem:
                continue

            # Lida com mensagens PREPARE
            if mensagem.tipo == TipoMensagem.PREPARE:
                if mensagem.numero > self.numero_aceito:
                    self.numero_aceito = mensagem.numero
                    self.enviar_mensagem(mensagem.remetente, Mensagem(TipoMensagem.PROMISE, self.id, self.numero_aceito, self.valor_aceito))

            # Lida com mensagens ACCEPT
            elif mensagem.tipo == TipoMensagem.ACCEPT:
                if mensagem.numero >= self.numero_aceito:
                    self.numero_aceito = mensagem.numero
                    self.valor_aceito = mensagem.valor
                    self.enviar_mensagem(mensagem.remetente, Mensagem(TipoMensagem.ACCEPTED, self.id, self.numero_aceito))

            # Lida com mensagens DECIDE
            elif mensagem.tipo == TipoMensagem.DECIDE:
                self.decidido = True
                self.valor_aceito = mensagem.valor
                self.logger.info(f"Decisão recebida: {self.valor_aceito}")

# Função para executar um processo individual
def executar_processo(id: int, total_processos: int, valor_proposta: Optional[int] = None):
    processo = Processo(id, total_processos)
    if valor_proposta is not None:
        resultado = processo.propor(valor_proposta)
        processo.logger.info(f"Resultado final = {resultado}")
    else:
        processo.executar()

# Ponto de entrada principal do programa
if __name__ == "__main__":
    total_processos = 5
    processos: List[mp.Process] = []

    # Inicia múltiplos processos
    for i in range(total_processos):
        valor_proposta = random.randint(1, 100) if i == 0 else None
        p = mp.Process(target=executar_processo, args=(i, total_processos, valor_proposta))
        processos.append(p)
        p.start()

    # Aguarda todos os processos terminarem
    for p in processos:
        p.join()