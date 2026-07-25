from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()  # локально подхватывает .env; в контейнере, переменные уже в os.environ от docker-compose


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")


class DataBaseConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_", extra="ignore")

    user: str
    password: str
    db: str
    host: str = "localhost"
    port: int = 5432

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class JWTConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="JWT_", extra="ignore")

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


class Config(BaseSettings):
    db: DataBaseConfig = Field(default_factory=DataBaseConfig)
    jwt: JWTConfig = Field(default_factory=JWTConfig)


settings = Config()