from enum  import Enum


class Role(str, Enum):
    ROLE_ADMIN = 'ROLE_ADMIN'
    ROLE_USER = 'ROLE_USER'