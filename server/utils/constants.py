import os

from fastapi.security import HTTPBearer, OAuth2PasswordBearer

if "SECRET_KEY" not in os.environ:
    raise ValueError("SECRET_KEY environment variable is not set.")
if "AUTH_API_ORIGIN" not in os.environ:
    raise ValueError("AUTH_API_ORIGIN environment variable is not set.")

AUTH_ALGORITHM = "HS256"

AUTH_SECRET_KEY = os.environ["SECRET_KEY"]
AUTH_API_ORIGIN = os.environ["AUTH_API_ORIGIN"]
AUTH_API_TOKEN_URL = os.path.join(AUTH_API_ORIGIN, "usuarios/login/")

HTTP_SCHEME = HTTPBearer(auto_error=False)
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl=AUTH_API_TOKEN_URL, auto_error=False)
