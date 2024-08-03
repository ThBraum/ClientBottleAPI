import logging
import os
import smtplib
import ssl
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import lru_cache
from string import Template
from urllib.parse import urljoin

import mjml
from fastapi import BackgroundTasks

from server.configuration.environment import SETTINGS
from server.utils.dependencies import ROOT_FOLDER_PATH

logger = logging.getLogger(__name__)


class ClienteEmailBase(ABC):
    @abstractmethod
    def send_email_invitation(self, bg: BackgroundTasks, email_destinatario: str, cd_token: str):
        pass

    @abstractmethod
    def send_email_recovery_password(
        self,
        bg: BackgroundTasks,
        email_destinatario: str,
        cd_token: str,
        nm_pessoa: str,
    ):
        pass


@lru_cache
def read_template(nome: str):
    try:
        caminho = ROOT_FOLDER_PATH / "templates" / "email" / f"{nome}.html"
        logger.info(f"Verificando caminho do template: {caminho}")
        if not os.path.exists(caminho):
            logger.error(f"Arquivo não encontrado: {caminho}")
        with open(caminho) as f:
            return Template(f.read())
    except Exception as e:
        logger.exception(f"Erro ao ler template {nome}. Caminho: {caminho}")
        raise e


class ClienteEmail(ClienteEmailBase):
    def __init__(
        self,
        server_smtp: str,
        port_server: int,
        email_sender: str,
        email_password: str,
    ):
        self.server_smtp = server_smtp
        self.port_server = port_server
        self.email_sender = email_sender
        self.email_password = email_password

    @staticmethod
    def gerar_link_convite(token: str):
        route = f"/user/confirm?token={token}"
        return urljoin(SETTINGS.frontend_url, route)

    @staticmethod
    def gerar_link_recuperacao_senha(token: str):
        route = f"user/recover_password?token={token}"
        return urljoin(SETTINGS.frontend_url, route)

    def enviar_email(self, recipient_email: str, titulo: str, content: str):
        message = MIMEMultipart("alternative")
        message["Subject"] = f"[ClientBottle] {titulo}"
        message["From"] = self.email_sender
        message["To"] = recipient_email
        message.attach(MIMEText(content, "html", "utf-8"))

        logger.info(f"Tentando enviar email para {recipient_email}")

        try:
            with self.criar_server_smtp() as server:
                server.login(self.email_sender, self.email_password)
                server.sendmail(self.email_sender, recipient_email, message.as_string())
        except Exception:
            logger.exception(f"Erro ao enviar email para {recipient_email}")
        else:
            logger.info(f"Email enviado para {recipient_email}")

    def criar_server_smtp(self):
        # Para desenvolvimento
        if "smtp4dev" in self.server_smtp:
            logger.info("Usando smtp4dev")
            return smtplib.SMTP(self.server_smtp, self.port_server)

        # Para uso real
        context = ssl.create_default_context()

        if self.port_server == 587:
            logger.info("Usando servidor SMTP com TLS")
            server = smtplib.SMTP(self.server_smtp, self.port_server)
            server.starttls(context=context)
            return server
        else:
            logger.info("Usando servidor SMTP com SSL")
            return smtplib.SMTP_SSL(self.server_smtp, self.port_server, context=context)

    def enviar_email_em_task(
        self, bg: BackgroundTasks, user_email: str, titulo: str, conteudo: str
    ):
        bg.add_task(self.enviar_email, user_email, titulo, conteudo)

    def send_email_invitation(self, bg: BackgroundTasks, user_email: str, token: str):
        link_botao = self.gerar_link_convite(token)
        conteudo = read_template("invite").substitute(link_botao=link_botao)
        self.enviar_email_em_task(bg, user_email, "Bem vindo ao ClientBottle", conteudo)

    def send_email_recovery_password(
        self,
        bg: BackgroundTasks,
        email: str,
        token: str,
        user: str,
    ):
        link_botao = self.gerar_link_recuperacao_senha(token)
        conteudo = read_template("recovery_password").substitute(link_botao=link_botao, user=user)
        self.enviar_email_em_task(bg, email, "Recuperação de Senha", conteudo)


@lru_cache
def get_cliente_email() -> ClienteEmailBase:
    return ClienteEmail(
        port_server=SETTINGS.smtp_port,
        server_smtp=SETTINGS.smtp_host,
        email_sender=SETTINGS.smtp_user,
        email_password=SETTINGS.smtp_password,
    )
