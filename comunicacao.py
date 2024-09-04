import os
import socket
import pickle
import time
from typing import Optional
from mensagem import Mensagem

PORTA_BASE = int(os.getenv('PORTA_BASE')) 
TIMEOUT = float(os.getenv('TIMEOUT'))     

class Comunicador:
    def __init__(self, id: int, processo_com_erro: int = -1):
        self.id = id
        self.processo_com_erro = processo_com_erro
        # Configuração do socket para comunicação via UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('localhost', PORTA_BASE + self.id))
        self.socket.settimeout(TIMEOUT)

    def enviar_mensagem(self, destino: int, mensagem: Mensagem):
        try:
            if self.id == self.processo_com_erro:
                print(f"\033[91mErro forçado: Processo {self.id} dormindo por {TIMEOUT * 2} segundos\033[0m")
                time.sleep(TIMEOUT + 2)  # Dorme por um tempo maior que o timeout
            # Serializa e envia a mensagem para o processo de destino
            self.socket.sendto(pickle.dumps(mensagem), ('localhost', PORTA_BASE + destino))
            return True
        except Exception as e:
            print(f"\033[91mErro ao enviar a mensagem: {e}\033[0m")
            return False

    def receber_mensagem(self) -> Optional[Mensagem]:
        try:
            # Recebe e desserializa uma mensagem
            data, _ = self.socket.recvfrom(1024)
            return pickle.loads(data)
        except socket.timeout:
            print(f"Timeout ao receber mensagem no processo {self.id}")
            # Retorna None se ocorrer timeout
            return None
        except Exception as e:
            print(f"Erro ao receber mensagem no processo {self.id}. Erro: {e}")
            # Retorna None em caso de erro
            return None