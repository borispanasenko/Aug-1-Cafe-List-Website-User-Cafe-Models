from app.app_configs import Configs
from fastapi_users import FastAPIUsers
from app.app_core.domain.models.user_model import UserModel
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from app.app_core.domain.services.user_manager import get_user_manager
from uuid import UUID

SECRET_KEY = Configs.SECRET_KEY


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_KEY, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=BearerTransport(tokenUrl="/auth/jwt/login"),
    get_strategy=get_jwt_strategy,
)


fastapi_users = FastAPIUsers[UserModel, UUID](
    get_user_manager,
    [auth_backend]
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
