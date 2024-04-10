import pathlib


class Settings:
    PARENT = pathlib.Path(__file__).parent.resolve()


settings = Settings()
