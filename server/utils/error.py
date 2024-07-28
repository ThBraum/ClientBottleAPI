from enum import Enum, unique
from typing import List

from fastapi import status
from fastapi.responses import JSONResponse, PlainTextResponse


@unique
class CodigoErro(Enum):
    EMAIL_JA_CADASTRADO = 1001
    ACESSO_NAO_PERMITIDO = 1002
    CREDENCIAIS_INVALIDAS = 1003
    DS_LOGIN_NAO_CADASTRADO = 1004
    DS_CHAVE_BUSCA_NAO_ENCONTRADO = 1005
    USUARIO_NAO_VINCULADO = 1006
    USUARIO_INATIVO = 1007
    AUTENTICACAO_NECESSARIA = 1008
    TOKEN_INVALIDO = 1009
    SESSAO_EXPIRADA_OU_INVALIDA = 1010
    SESSAO_EXPIRADA = 1011


MAP_ERRO_PARA_HTTP_STATUS = {
    CodigoErro.EMAIL_JA_CADASTRADO: status.HTTP_409_CONFLICT,
    CodigoErro.ACESSO_NAO_PERMITIDO: status.HTTP_403_FORBIDDEN,
    CodigoErro.CREDENCIAIS_INVALIDAS: status.HTTP_401_UNAUTHORIZED,
    CodigoErro.DS_LOGIN_NAO_CADASTRADO: status.HTTP_401_UNAUTHORIZED,
    CodigoErro.DS_CHAVE_BUSCA_NAO_ENCONTRADO: status.HTTP_404_NOT_FOUND,
    CodigoErro.USUARIO_NAO_VINCULADO: status.HTTP_400_BAD_REQUEST,
    CodigoErro.USUARIO_INATIVO: status.HTTP_403_FORBIDDEN,
    CodigoErro.AUTENTICACAO_NECESSARIA: status.HTTP_401_UNAUTHORIZED,
    CodigoErro.TOKEN_INVALIDO: status.HTTP_401_UNAUTHORIZED,
    CodigoErro.SESSAO_EXPIRADA_OU_INVALIDA: status.HTTP_401_UNAUTHORIZED,
    CodigoErro.SESSAO_EXPIRADA: status.HTTP_401_UNAUTHORIZED,
}

MAP_ERRO_PARA_MENSAGEM = {
    CodigoErro.EMAIL_JA_CADASTRADO: "Email já cadastrado. Utilize um email diferente ou faça login.",
    CodigoErro.ACESSO_NAO_PERMITIDO: "Acesso não permitido. Entre em contato com o suporte.",
    CodigoErro.CREDENCIAIS_INVALIDAS: "Email e/ou senha incorretos. Verifique suas credenciais e tente novamente.",
    CodigoErro.DS_LOGIN_NAO_CADASTRADO: "Conta não registrada. Verifique suas credenciais e tente novamente.",
    CodigoErro.DS_CHAVE_BUSCA_NAO_ENCONTRADO: "Chave de busca não encontrada. Verifique a chave de busca e tente novamente.",
    CodigoErro.USUARIO_NAO_VINCULADO: "Usuário não vinculado. Entre em contato com o suporte.",
    CodigoErro.USUARIO_INATIVO: "Conta inativa. Entre em contato com o suporte.",
    CodigoErro.AUTENTICACAO_NECESSARIA: "Autenticação necessária. Faça login para continuar.",
    CodigoErro.TOKEN_INVALIDO: "Token inválido. Faça login novamente.",
    CodigoErro.SESSAO_EXPIRADA_OU_INVALIDA: "Sua sessão expirou ou é inválida. Faça login novamente",
    CodigoErro.SESSAO_EXPIRADA: "Sua sessão expirou. Faça login novamente.",
}


class ClientBottleException(Exception):
    def __init__(self, errors: List[CodigoErro], status_code: int | None = None):
        self.errors = errors
        self.status_code = self.__http_from_errors(errors) if status_code is None else status_code

    def to_json_response(self):
        return PlainTextResponse(
            status_code=self.status_code, content=MAP_ERRO_PARA_MENSAGEM[self.errors[0]]
        )

    @staticmethod
    def __http_from_errors(errors: List[CodigoErro]):
        status_set = {MAP_ERRO_PARA_HTTP_STATUS[error] for error in errors}
        if len(status_set) == 1:
            return status_set.pop()
        return status.HTTP_400_BAD_REQUEST
