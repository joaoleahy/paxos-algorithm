import socket
import pickle
from typing import Optional
from mensagem import Mensagem

PORTA_BASE = 5000  # Porta base para comunicação
TIMEOUT = 2.0      # Timeout para operações de socket

class Comunicador:
    def __init__(self, id: int):
        self.id = id
        # Configuração do socket para comunicação via UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('localhost', PORTA_BASE + self.id))
        self.socket.settimeout(TIMEOUT)

    def enviar_mensagem(self, destino: int, mensagem: Mensagem):
        try:
            # Serializa e envia a mensagem para o processo de destino
            self.socket.sendto(pickle.dumps(mensagem), ('localhost', PORTA_BASE + destino))
            return True
        except Exception:
            return False

    def receber_mensagem(self) -> Optional[Mensagem]:
        try:
            # Recebe e desserializa uma mensagem
            data, _ = self.socket.recvfrom(1024)
            return pickle.loads(data)
        except socket.timeout:
            # Retorna None se ocorrer timeout
            return None
        except Exception:
            # Retorna None em caso de erro
            return None