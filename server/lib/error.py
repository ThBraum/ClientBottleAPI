from enum import Enum, unique
from typing import List

from fastapi import status
from fastapi.responses import JSONResponse


@unique
class CodigoErro(Enum):
    EMAIL_JA_CADASTRADO = (409, "Email já cadastrado. Utilize um email diferente ou faça login.")
    ACESSO_NAO_PERMITIDO = (403, "Acesso não permitido. Entre em contato com o suporte.")
    CREDENCIAIS_INVALIDAS = (
        401,
        "Email e/ou senha incorretos. Verifique suas credenciais e tente novamente.",
    )
    DS_LOGIN_NAO_CADASTRADO = (
        401,
        "Conta não registrada. Verifique suas credenciais e tente novamente.",
    )
    DS_CHAVE_BUSCA_NAO_ENCONTRADO = (
        404,
        "Chave de busca não encontrada. Verifique a chave de busca e tente novamente.",
    )
    USUARIO_NAO_VINCULADO = (400, "Usuário não vinculado. Entre em contato com o suporte.")
    USUARIO_INATIVO = (403, "Conta inativa. Entre em contato com o suporte.")
    AUTENTICACAO_NECESSARIA = (401, "Autenticação necessária. Faça login para continuar.")
    SESSAO_EXPIRADA_OU_INVALIDA = (401, "Sua sessão expirou ou é inválida. Faça login novamente")
    SESSAO_EXPIRADA = (401, "Sua sessão expirou. Faça login novamente.")


class ClientBottleException(Exception):
    def __init__(self, errors: List[CodigoErro], status_code=status.HTTP_400_BAD_REQUEST):
        self.errors = errors
        self.status_code = status_code

    def to_json_response(self):
        errors_response = [
            {"code": error.value[0], "message": error.value[1]} for error in self.errors
        ]
        return JSONResponse(status_code=self.status_code, content={"errors": errors_response})
