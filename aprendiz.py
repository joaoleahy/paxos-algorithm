import logging
from typing import Optional
from mensagem import TipoMensagem, Mensagem
from comunicacao import Comunicador

class Aprendiz:
    def __init__(self, id: int, total_processos: int):
        self.id = id
        self.total_processos = total_processos
        self.valor_aprendido = None
        self.logger = logging.getLogger(f"Aprendiz-{self.id}")
        self.comunicador = Comunicador(id)

    def executar(self):
        self.logger.info(f"Aprendiz {self.id} aguardando decisão...")
        while self.valor_aprendido is None:
            mensagem = self.comunicador.receber_mensagem()
            if mensagem and mensagem.tipo == TipoMensagem.DECIDE:
                self.valor_aprendido = mensagem.valor
                self.logger.info(f"Aprendiz {self.id} aprendeu o valor: {self.valor_aprendido}")

    def obter_valor_aprendido(self):
        return self.valor_aprendido