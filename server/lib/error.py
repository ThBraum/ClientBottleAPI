from enum import Enum, unique
from typing import List

from fastapi import status
from fastapi.responses import JSONResponse


@unique
class CodigoErro(Enum):
    EMAIL_JA_CADASTRADO = (452, "Email já cadastrado.")
    ACESSO_NAO_PERMITIDO = (401, "Acesso não permitido.")
    CREDENCIAIS_INVALIDAS = (401, "Credenciais inválidas.")
    DS_LOGIN_NAO_ENCONTRADO = (401, "Login não encontrado.")
    DS_CHAVE_BUSCA_NAO_ENCONTRADO = (456, "Chave de busca não encontrada.")
    USUARIO_NAO_VINCULADO = (401, "Usuário não vinculado.")
    DS_LOGIN_JA_CADASTRADO = (458, "Login já cadastrado.")
    USUARIO_INATIVO = (401, "Conta inativa.")
    


class ClientBottleException(Exception):
    def __init__(self, errors: List[CodigoErro], status_code=status.HTTP_400_BAD_REQUEST):
        self.errors = errors
        self.status_code = status_code

    def to_json_response(self):
        errors_response = [
            {"code": error.value[0], "message": error.value[1]} for error in self.errors
        ]
        return JSONResponse(status_code=self.status_code, content={"errors": errors_response})
