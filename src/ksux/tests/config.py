import pathlib

from pydantic import BaseSettings


class Settings(BaseSettings):
    PARENT = pathlib.Path(__file__).parent.resolve()


settings = Settings()
