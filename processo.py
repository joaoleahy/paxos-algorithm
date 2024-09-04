import logging
import random
import time
from typing import Optional
from mensagem import TipoMensagem, Mensagem
from comunicacao import Comunicador

class Processo:
    def __init__(self, id: int, total_processos: int):
        self.id = id
        self.total_processos = total_processos
        self.numero_proposta = 0
        self.numero_prometido = 0
        self.valor_aceito = None
        self.numero_aceito = 0
        self.decidido = False
        self.logger = logging.getLogger(f"Processo-{self.id}")
        self.comunicador = Comunicador(id)

    def propor(self, valor: int):
        time.sleep(random.uniform(0.1, 0.5))
        
        self.numero_proposta = max(self.numero_proposta, self.numero_aceito) + 1
        self.logger.info(f"Iniciando proposta com número {self.numero_proposta} e valor {valor}")

        contagem_promessas, maior_numero_aceito, valor_maior_proposta_aceita = self._fase_prepare()

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
        timeout = time.time() + 2  # 2 segundos de timeout
        while contagem_promessas <= self.total_processos // 2 and time.time() < timeout:
            mensagem = self.comunicador.receber_mensagem()
            if mensagem:
                if mensagem.tipo == TipoMensagem.PROMISE:
                    contagem_promessas += 1
                    if mensagem.proposta_aceita and mensagem.numero > maior_numero_aceito:
                        maior_numero_aceito = mensagem.numero
                        valor_maior_numero_aceito = mensagem.valor
                elif mensagem.tipo == TipoMensagem.PREPARE:
                    self._lidar_com_prepare(mensagem)
        
        self.logger.info(f"Fase PREPARE concluída. Promessas recebidas: {contagem_promessas}")
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
        timeout = time.time() + 2  # 2 segundos de timeout
        while contagem_aceites <= self.total_processos // 2 and time.time() < timeout:
            mensagem = self.comunicador.receber_mensagem()
            if mensagem:
                if mensagem.tipo == TipoMensagem.ACCEPTED:
                    contagem_aceites += 1
                    if contagem_aceites > self.total_processos // 2:
                        self.logger.info(f"Maioria de aceitações recebida. Anunciando decisão.")
                        return self._anunciar_decisao(valor_proposta)
                elif mensagem.tipo == TipoMensagem.PREPARE:
                    self._lidar_com_prepare(mensagem)
                elif mensagem.tipo == TipoMensagem.ACCEPT:
                    self._lidar_com_accept(mensagem)

        self.logger.info(f"Fase ACCEPT concluída. Aceitações recebidas: {contagem_aceites}")
        return None

    def _anunciar_decisao(self, valor_proposta):
        self.decidido = True
        self.valor_aceito = valor_proposta
        self.logger.info(f"Anunciando decisão: valor {valor_proposta}")
        
        for i in range(self.total_processos * 2):
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
                self.logger.info(f"Mensagem ACCEPTED enviada para processo {mensagem.remetente}. Aceito número {self.numero_aceito} com valor {self.valor_aceito}")

    def _lidar_com_decide(self, mensagem):
        self.decidido = True
        self.numero_aceito = mensagem.numero
        self.valor_aceito = mensagem.valor
        self.logger.debug(f"Decisão recebida: proposta {self.numero_aceito} com valor {self.valor_aceito}")