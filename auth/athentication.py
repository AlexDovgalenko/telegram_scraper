from dataclasses import dataclass
import json

CREDENTIALS_FILE_LOCATION = "auth/my_telegram_creds.json"


@dataclass
class AuthData:
    api_id: int
    api_hash: str
    phone_number: str
    app_short_name: str = None


def __get_auth_data_from_json(path_to_file):
    with open(path_to_file, "r") as creds_file:
        return json.load(creds_file)


def auth_init():
    auth_data = __get_auth_data_from_json(CREDENTIALS_FILE_LOCATION)
    return AuthData(api_id=auth_data.get("api_id"), api_hash=auth_data.get("api_hash"),
                    app_short_name=auth_data.get("app_short_name"), phone_number=auth_data.get("phone_number"))
