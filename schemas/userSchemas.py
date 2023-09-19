from datetime import datetime
from pydantic import BaseModel, EmailStr, constr


class SocialSignupSchema(BaseModel):
    provider: str
    email: EmailStr | None = None
    username: str | None = None
    name: str


class UserSignupSchema(BaseModel):
    name: str
    email: EmailStr
    password: constr(min_length=8)
    passwordConfirm: str


class UserSigninSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
