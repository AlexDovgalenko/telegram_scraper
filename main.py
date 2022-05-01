import datetime
import json
import logging
from enum import Enum
from typing import TYPE_CHECKING, Iterable, List, Dict
import csv
from pyrogram import Client
from pyrogram.enums.chat_type import ChatType

from auth.athentication import auth_init

if TYPE_CHECKING:
    from pyrogram.types import Dialog, Message, User, Chat

PARSED_DATA_LOCATION = "parsed_data/"
CSV_OUTPUT_LOCATION = "csv_output/"

auth_data = auth_init()
logging.basicConfig(level=logging.INFO)

client = Client(name="first_pyrogram_session", api_id=auth_data.api_id, api_hash=auth_data.api_hash)

json_base_template = {
    "group": [],
    "supergroup": [],
    "channel": [],
    "private": [],
    "bot": []
}


class DialogFields(Enum):
    ID = "id"
    TYPE = "type"
    TYTLE = "title"
    DESCRIPTION = "description"
    USERNAME = "username"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    INVITE_LINK = "invite_link"
    LINKED_CHAT = "linked_chat"
    MEMBERS_COUNT = "members_count"
    IS_VERIFIED = "is_verified"
    IS_RESTRICTED = "is_restricted"
    IS_SCAM = "is_scam"
    IS_FAKE = "is_fake"
    IS_CREATOR = "is_creator"
    HAS_PROTECTED_CONTENT = "has_protected_content"


def __write_parsed_data(file_name: str, data_json):
    with open(f"{PARSED_DATA_LOCATION}{file_name}.json", mode="w", encoding="utf-8") as data_file:
        json.dump(data_json, data_file, indent=4, ensure_ascii=False)


def get_all_dialogs():
    return client.get_dialogs()


def sort_dialogs_by_chat_type(dialogs: Iterable["Dialog"]):
    groups = []
    super_groups = []
    channels = []
    privates = []
    bots = []
    for item in dialogs:
        if item.chat.type == ChatType.GROUP:
            groups.append(item.chat)
        elif item.chat.type == ChatType.SUPERGROUP:
            super_groups.append(item.chat)
        if item.chat.type == ChatType.CHANNEL:
            channels.append(item.chat)
        if item.chat.type == ChatType.PRIVATE:
            privates.append(item.chat)
        if item.chat.type == ChatType.BOT:
            bots.append(item.chat)
    return groups, super_groups, channels, privates, bots


def generate_json_dialog_item(item):
    item_dict = {}
    dialog_fields_list = [item.value for item in DialogFields]
    for field in dialog_fields_list:
        if field == "type":
            item_dict[field] = item.__getattribute__(field).value
        else:
            item_dict[field] = item.__getattribute__(field)
    return item_dict


def create_json_file(dialog_list):
    filenames = ["groups", "super_groups", "channels", "private_groups", "bots"]
    for id, dialog_type in enumerate(dialog_list):
        file_dict = {}
        filename = filenames[id]
        file_dict[filename] = []
        for item in dialog_type:
            file_dict[filename].append(generate_json_dialog_item(item))
        __write_parsed_data(filename, file_dict)


def write_messages_to_csv(messages_list: List[Dict]):
    message_fields = ["Message ID", "Message Date", "Message Text", "Message Link", "User ID",
                      "User Name", "User Phone Number", "User First Name", "User Last Name", "User Is Contact",
                      "Chat ID" "Chat Title"]
    with open('messages_file.csv', 'w', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(message_fields)

    with open('messages_file.csv', 'a', encoding="utf-8") as f:
        writer = csv.writer(f)
        [writer.writerow(list(item.values())) for item in messages_list]


def get_messages_from_history_as_list(chat_history: Iterable["Message"]) -> List[Dict]:
    messages_list = []
    for message in chat_history:
        messages_list.append(get_message_data_dict(message))
    return messages_list


def get_user_data_dict(user_data: "User"):
    user_dict = {}
    user_dict["user_id"] = user_data.id if user_data else None,
    user_dict["user_name"] = user_data.username if user_data else None,
    user_dict["user_phone_number"] = user_data.phone_number if user_data else None,
    user_dict["user_first_name"] = user_data.first_name if user_data else None,
    user_dict["user_last_name"] = user_data.last_name if user_data else None,
    user_dict["user_is_contact"] = user_data.is_contact if user_data else None
    return user_dict


def get_chat_data_dict(chat_data: "Chat"):
    chat_dict = {"chat_id": chat_data.id, "chat_title": chat_data.title}
    return chat_dict


def get_message_data_dict(message: "Message"):
    message_dict = {"message_id": message.id, "message_date": message.date.strftime("%Y-%m-%d %H:%M:%S"),
                    "message_text": message.text, "message_link": message.link}

    if message.from_user:
        user_data_dict = get_user_data_dict(message.from_user)
        message_dict.update(user_data_dict)
    # if message.sender_chat:
    #     user_data_dict = get_user_data_dict(message.from_user)
    #     message_dict.update(user_data_dict)
    if message.chat:
        chat_data_dict = get_chat_data_dict(message.chat)
        message_dict.update(chat_data_dict)

    return message_dict


if __name__ == "__main__":
    client.start()
    # my_info = client.get_me()
    dialogs = get_all_dialogs()
    # all_dialogs = return_dialogs(dialogs)
    # groups, super_groups, channels, privates, bots = sort_dialogs_by_chat_type(dialogs)
    sorted_dialogs = sort_dialogs_by_chat_type(dialogs)
    ids_list = [list(map(lambda x: x.id, item)) for item in sorted_dialogs]
    # create_json_file(sorted_dialogs)
    group_id = ids_list[1][0]
    # group_history_obj = client.get_chat_history(chat_id=group_id, offset_date=datetime.datetime.fromtimestamp(1643666400.0))
    group_history_obj = client.get_chat_history(chat_id=group_id,
                                                offset_date=datetime.datetime.fromtimestamp(1650834000.0))
    group_history = list(group_history_obj)

    write_messages_to_csv(get_messages_from_history_as_list(group_history))

    print(group_history)
