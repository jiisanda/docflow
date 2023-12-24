from app.schemas.auth.bands import UserOut


class SystemUser(UserOut):
    password: str
