from enum import Enum


class UserRole(str, Enum):
    ADMINISTRATOR = "ADMINISTRATOR"
    USER = "USER"
