from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from modules.users.role import Role


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: Role
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

