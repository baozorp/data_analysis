import requests
from dotenv import load_dotenv
import os
import time
import random
import json
from typing import List, Dict

class JSONReader:

    @staticmethod
    def read_group_list_from_file(group_dict_path: str) -> List[str]:
        group_list: List[str] = []
        if not os.path.exists(group_dict_path):
            return group_list
        with open(group_dict_path, "r") as group_list_file:
            group_dict = json.load(group_list_file)
            if isinstance(group_dict, dict):
                for person_id in group_dict:
                    group_list.append(str(person_id))
        return group_list

class FriendsParser:

    def __init__(self, api_url: str, api_key: str) -> None:
        api_key = api_key
        self.api_url = api_url
        self.body_request_template = {
            "user_id": 0,
            "access_token": api_key,
            "v": 5.199
        }
    
    def get_tree_friends(self, group_ids: list):
        group_tree: Dict[str, Dict[str, List[str]]] = {groupmate_id: {} for groupmate_id in group_ids}
        for groupmate_id in group_tree:
            print(groupmate_id)
            list_of_friends = self.__get_list_of_friends(user_id=groupmate_id)
            group_tree[groupmate_id] = {friend_id_groupmate: [] for friend_id_groupmate in list_of_friends}   
            for friend_id_groupmate in group_tree[groupmate_id]:
                list_of_friend_of_friends = self.__get_list_of_friends(user_id=friend_id_groupmate)
                group_tree[groupmate_id][friend_id_groupmate] = list_of_friend_of_friends
        return group_tree

    def __get_list_of_friends(self, user_id: str) -> List[str]:
        self.body_request_template["user_id"] = user_id
        response: requests.models.Response = requests.post(self.api_url, data=self.body_request_template)
        try:
            json_response = response.json()
        except ValueError:
            return []
        if response.status_code != 200 or "response" not in json_response or "items" not in json_response["response"]:
            return []
        list_of_friend_groupmate = json_response["response"]["items"][:100]
        str_list_of_friend_groupmate = list(map(str, list_of_friend_groupmate))
        return str_list_of_friend_groupmate

if __name__=="__main__":
    load_dotenv()

    api_key =  os.getenv("API_KEY")
    if not api_key:
        print("Отсутствует ключ токена в environment")
        exit()
        
    info_path = "info.json"
    if not os.path.exists(info_path):
        print("Ошибка. В директории отсутствует info файл")
        exit()
    with open(info_path, "r") as info_file:
        info_dict = json.load(info_file)
    if "group_dict_path" not in info_dict or "group_tree_path" not in info_dict: 
        print("В info файле нет параметра пути к group_dict_path или group_tree_path")
        exit()

    group_dict_path = str(info_dict["group_dict_path"])
    group_tree_path = str(info_dict["group_tree_path"])
    api_url = str(info_dict["api_url"])
    friendParser = FriendsParser(api_url=api_url, api_key=api_key)
    group_ids = JSONReader.read_group_list_from_file(group_dict_path=group_dict_path)
    group_tree = friendParser.get_tree_friends(group_ids=group_ids)
    with open(group_tree_path, "w") as group_tree_file:
        json.dump(group_tree, group_tree_file)