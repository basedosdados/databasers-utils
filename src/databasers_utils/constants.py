from enum import Enum


class constants(Enum):
    API_URL = {
        "staging": "https://staging.backend.basedosdados.org/api/v1/graphql",
        "prod": "https://backend.basedosdados.org/api/v1/graphql",
    }
    ENV = {
        "email": "DB_DJANGO_EMAIL",
        "password": "DB_DJANGO_PASSWORD",
    }
