import logging
from typing import Optional
from mensagem import TipoMensagem, Mensagem
from comunicacao import Comunicador

class Processo:
    def __init__(self, id: int, total_processos: int, processo_com_erro: int = -1):
        self.id = id
        self.total_processos = total_processos
        self.numero_proposta = 0
        self.numero_prometido = 0
        self.valor_aceito = None
        self.numero_aceito = 0
        self.decidido = False
        self.logger = logging.getLogger(f"Processo-{self.id}")
        self.comunicador = Comunicador(id, processo_com_erro)

    def propor(self, valor: int):
        self.numero_proposta = max(self.numero_proposta, self.numero_aceito) + 1
        self.logger.info(f"Iniciando proposta com número {self.numero_proposta} e valor {valor}")

        # Fase 1: Prepare
        contagem_promessas, maior_numero_aceito, valor_maior_proposta_aceita = self._fase_prepare()

        # Fase 2: Accept
        if contagem_promessas > self.total_processos // 2:
            valor_proposta = valor_maior_proposta_aceita if valor_maior_proposta_aceita is not None else valor
            contagem_aceites = self._fase_accept(valor_proposta)

            if contagem_aceites > self.total_processos // 2:
                return self._anunciar_decisao(valor_proposta)

        self.logger.warning(f"Falha ao alcançar consenso com número de proposta {self.numero_proposta}")
        return None

    def _fase_prepare(self):
        contagem_promessas = 0
        maior_numero_aceito = 0
        valor_maior_numero_aceito = None

        # Envia mensagens PREPARE para todos os outros processos
        for i in range(self.total_processos):
            if i != self.id:
                sucesso = self.comunicador.enviar_mensagem(i, Mensagem(TipoMensagem.PREPARE, self.id, self.numero_proposta))
                if sucesso:
                    self.logger.debug(f"Mensagem PREPARE de número {self.numero_proposta} enviada com sucesso para processo {i}")


        # Aguarda promessas dos outros processos
        while contagem_promessas <= self.total_processos // 2:
            mensagem = self.comunicador.receber_mensagem()
            if mensagem and mensagem.tipo == TipoMensagem.PROMISE:
                contagem_promessas += 1
                if mensagem.proposta_aceita and mensagem.numero > maior_numero_aceito:
                    maior_numero_aceito = mensagem.numero
                    valor_maior_numero_aceito = mensagem.valor
        
        return contagem_promessas, maior_numero_aceito, valor_maior_numero_aceito

    def _fase_accept(self, valor_proposta):
        contagem_aceites = 0

        # Envia mensagens ACCEPT para todos os outros processos
        for i in range(self.total_processos):
            if i != self.id:
                sucesso = self.comunicador.enviar_mensagem(i, Mensagem(TipoMensagem.ACCEPT, self.id, self.numero_proposta, valor_proposta))
                if sucesso:
                    self.logger.debug(f"Mensagem ACCEPT de número {self.numero_proposta} e valor {valor_proposta} enviada com sucesso para processo {i}")

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
                sucesso = self.comunicador.enviar_mensagem(i, Mensagem(TipoMensagem.DECIDE, self.id, self.numero_proposta, valor_proposta))
                if sucesso:
                    self.logger.debug(f"Mensagem DECIDE de número {self.numero_proposta} e valor {valor_proposta} enviada com sucesso para processo {i}")
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
        if mensagem.numero > self.numero_prometido:
            self.numero_prometido = mensagem.numero
            if self.valor_aceito is not None:
                sucesso = self.comunicador.enviar_mensagem(mensagem.remetente, Mensagem(TipoMensagem.PROMISE, self.id, self.numero_aceito, self.valor_aceito, True))
            else:
                sucesso = self.comunicador.enviar_mensagem(mensagem.remetente, Mensagem(TipoMensagem.PROMISE, self.id, self.numero_prometido, self.valor_aceito, False))

            if sucesso:
                self.logger.debug(f"Mensagem PROMISE enviada para processo {mensagem.remetente}. Prometido número {self.numero_prometido}")

    def _lidar_com_accept(self, mensagem):
        if mensagem.numero >= self.numero_prometido:
            self.numero_aceito = mensagem.numero
            self.valor_aceito = mensagem.valor
            sucesso = self.comunicador.enviar_mensagem(mensagem.remetente, Mensagem(TipoMensagem.ACCEPTED, self.id, self.numero_aceito))

            if sucesso:
                self.logger.debug(f"Mensagem ACCEPTED enviada para processo {mensagem.remetente}. Aceito número {self.numero_aceito} com valor {self.valor_aceito}")

    def _lidar_com_decide(self, mensagem):
        self.decidido = True
        self.numero_aceito = mensagem.numero
        self.valor_aceito = mensagem.valor
        self.logger.debug(f"Decisão recebida: proposta {self.numero_aceito} com valor {self.valor_aceito}")