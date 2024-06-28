from pydantic import BaseModel


class UserLoginInput(BaseModel):
    email_or_username: str
    password: str
    
class UserLoginOutput(BaseModel):
    id_user: int
    full_name: str
    username: str
    email: str
    api_key: str
    created_at: str