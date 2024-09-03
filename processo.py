import logging
from typing import Optional
from mensagem import TipoMensagem, Mensagem
from comunicacao import Comunicador

class Processo:
    def __init__(self, id: int, total_processos: int):
        self.id = id
        self.total_processos = total_processos
        self.numero_proposta = 0
        self.valor_aceito = None
        self.numero_aceito = 0
        self.decidido = False
        self.logger = logging.getLogger(f"Processo-{self.id}")
        self.comunicador = Comunicador(id)

    def propor(self, valor: int):
        self.numero_proposta = max(self.numero_proposta, self.numero_aceito) + 1
        self.logger.info(f"Iniciando proposta com número {self.numero_proposta} e valor {valor}")

        # Fase 1: Prepare
        contagem_promessas, maior_numero_aceito, valor_maior_numero = self._fase_prepare()

        # Fase 2: Accept
        if contagem_promessas > self.total_processos // 2:
            valor_proposta = valor_maior_numero if valor_maior_numero else valor
            contagem_aceites = self._fase_accept(valor_proposta)

            if contagem_aceites > self.total_processos // 2:
                return self._anunciar_decisao(valor_proposta)

        self.logger.warning("Falha ao alcançar consenso")
        return None

    def _fase_prepare(self):
        contagem_promessas = 0
        maior_numero_aceito = 0
        valor_maior_numero = None

        # Envia mensagens PREPARE para todos os outros processos
        for i in range(self.total_processos):
            if i != self.id:
                self.comunicador.enviar_mensagem(i, Mensagem(TipoMensagem.PREPARE, self.id, self.numero_proposta))

        # Aguarda promessas dos outros processos
        while contagem_promessas <= self.total_processos // 2:
            mensagem = self.comunicador.receber_mensagem()
            if mensagem and mensagem.tipo == TipoMensagem.PROMISE:
                contagem_promessas += 1
                if mensagem.numero > maior_numero_aceito:
                    maior_numero_aceito = mensagem.numero
                    valor_maior_numero = mensagem.valor

        return contagem_promessas, maior_numero_aceito, valor_maior_numero

    def _fase_accept(self, valor_proposta):
        contagem_aceites = 0

        # Envia mensagens ACCEPT para todos os outros processos
        for i in range(self.total_processos):
            if i != self.id:
                self.comunicador.enviar_mensagem(i, Mensagem(TipoMensagem.ACCEPT, self.id, self.numero_proposta, valor_proposta))

        # Aguarda aceitações dos outros processos
        while contagem_aceites <= self.total_processos // 2:
            mensagem = self.comunicador.receber_mensagem()
            if mensagem and mensagem.tipo == TipoMensagem.ACCEPTED:
                contagem_aceites += 1

        return contagem_aceites

    def _anunciar_decisao(self, valor_proposta):
        self.decidido = True
        self.valor_aceito = valor_proposta
        self.logger.info(f"Consenso alcançado com valor {valor_proposta}")
        # Anuncia a decisão para todos os outros processos
        for i in range(self.total_processos):
            if i != self.id:
                self.comunicador.enviar_mensagem(i, Mensagem(TipoMensagem.DECIDE, self.id, self.numero_proposta, valor_proposta))
        return valor_proposta

    def executar(self):
        while not self.decidido:
            mensagem = self.comunicador.receber_mensagem()
            if not mensagem:
                continue

            # Lida com diferentes tipos de mensagens
            if mensagem.tipo == TipoMensagem.PREPARE:
                self._lidar_com_prepare(mensagem)
            elif mensagem.tipo == TipoMensagem.ACCEPT:
                self._lidar_com_accept(mensagem)
            elif mensagem.tipo == TipoMensagem.DECIDE:
                self._lidar_com_decide(mensagem)

    def _lidar_com_prepare(self, mensagem):
        if mensagem.numero > self.numero_aceito:
            self.numero_aceito = mensagem.numero
            self.comunicador.enviar_mensagem(mensagem.remetente, Mensagem(TipoMensagem.PROMISE, self.id, self.numero_aceito, self.valor_aceito))

    def _lidar_com_accept(self, mensagem):
        if mensagem.numero >= self.numero_aceito:
            self.numero_aceito = mensagem.numero
            self.valor_aceito = mensagem.valor
            self.comunicador.enviar_mensagem(mensagem.remetente, Mensagem(TipoMensagem.ACCEPTED, self.id, self.numero_aceito))

    def _lidar_com_decide(self, mensagem):
        self.decidido = True
        self.valor_aceito = mensagem.valor
        self.logger.info(f"Decisão recebida: {self.valor_aceito}")