from enum import Enum
from typing import Optional

# Enumeração dos tipos de mensagens usadas no protocolo Paxos
class TipoMensagem(Enum):
    PREPARE = 1  # Fase 1a: Propositor solicita promessas
    PROMISE = 2  # Fase 1b: Aceitador promete considerar a proposta
    ACCEPT = 3   # Fase 2a: Propositor solicita aceitação
    ACCEPTED = 4 # Fase 2b: Aceitador aceita a proposta
    DECIDE = 5   # Fase 3: Propositor anuncia a decisão

# Classe para representar as mensagens trocadas entre os processos
class Mensagem:
    def __init__(self, tipo: TipoMensagem, remetente: int, numero: int, valor: Optional[int] = None, proposta_aceita: Optional[bool] = None):
        self.tipo = tipo          # Tipo da mensagem (PREPARE, PROMISE, etc.)
        self.remetente = remetente # ID do processo que enviou a mensagem
        self.numero = numero       # Número da proposta
        self.valor = valor         # Valor proposto (pode ser None em algumas mensagens)
        self.proposta_aceita = proposta_aceita # Proposta já aceita pelo aceitador (usado na mensagem PROMISE)