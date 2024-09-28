from pyvis.network import Network
import networkx as nx
import json
from typing import Tuple, List, Dict
import os

class GraphHandler:

    def __init__(self) -> None:
        self.edges_colors = ['red', 'green', 'blue']
        pass

    def read_group_dict_from_file(self, group_dict_path: str) -> Dict[str, str]:
        group_dict: Dict[str, str] = {}
        if not os.path.exists(group_dict_path):
            return group_dict
        with open(group_dict_path, "r") as group_list_file:
            group_dict = json.load(group_list_file)
        return group_dict
    
    def load_tree_from_file(self, path: str):
        with open(path, "r") as friends_tree_file:
            tree = json.load(friends_tree_file)
        if not isinstance(tree, dict):
            return {}
        return tree if tree else {}
    
    def get_array_of_edges(self, prev_value: str, tree: dict, level: int = 0, names_dict: Dict[str, str] = {}) -> List[Tuple[str, str, Dict[str, str]]]:
        result_array: List[Tuple[str, str, Dict[str, str]]] = []

        if prev_value != "":
            if isinstance(tree, Dict):
                subkeys_list = tree.keys()
                for sub_key in subkeys_list:
                    result_array.append((prev_value, sub_key, {"color": self.edges_colors[level if level < 2 else -1]}))
                    result_array += self.get_array_of_edges(prev_value=sub_key, tree=tree[sub_key], level=level + 1)
            elif isinstance(tree, List):
                for element in tree:
                    result_array.append((prev_value, element, {"color": self.edges_colors[level if level < 2 else -1]}))
        else:
            for key in tree:
                if isinstance(tree[key], Dict):
                    subkeys_list = tree[key].keys()
                    for sub_key in subkeys_list:
                        result_array.append((names_dict[key], sub_key, {"color": self.edges_colors[level if level < 2 else -1]}))
                        result_array += self.get_array_of_edges(prev_value=sub_key, tree=tree[key][sub_key], level=level+1)
                elif isinstance(tree[key], List):
                    for element in tree[key]:
                        result_array.append((names_dict[key], element, {"color": self.edges_colors[level if level < 2 else -1]}))
        return result_array
    

    def trim_graph(self, edges_list: List[Tuple[str, str, Dict[str, str]]]):
        passed_notes: Dict[str, int] = {}
        trimmed_list = []
        for i in edges_list:
            if i[0] in passed_notes:
                if passed_notes[i[0]] < 30:
                    trimmed_list.append(i)
                    passed_notes[i[0]] += 1
            else:
                trimmed_list.append(i)
                passed_notes[i[0]] = 1
        return trimmed_list
class Graph():

    def __init__(self) -> None:
        self.G = nx.Graph()

    def add_edges(self, edges_list: List[Tuple[str, str, Dict[str, str]]]) -> None:
        for i in edges_list:
            self.G.add_node(i[0], **i[2])
        self.G.add_edges_from(edges_list)

    def visualise(self, save_path: str, options: dict = {}):
        net = Network(notebook=False)
        json_options = json.dumps(options)
        net_options = f"var options = {json_options}"
        net.set_options(net_options)
        net.from_nx(self.G)
        net.show(save_path, notebook=False)



if __name__=="__main__":
    info_path = "info.json"
    if not os.path.exists(info_path):
        print("Ошибка. В директории отсутствует info файл")
        exit()
    with open(info_path, "r") as info_file:
        info_dict = json.load(info_file)
    if not info_dict: 
        print("Info пуст")
        exit()
    options = info_dict["options"] if "options" in info_dict else {}
    group_dict_path = str(info_dict["group_dict_path"] if "group_dict_path" in info_dict else (print("group_dict_path not in info"), exit()))
    group_tree_path = str(info_dict["group_tree_path"] if "group_tree_path" in info_dict else (print("group_tree_path not in info"), exit()))

    graphHandler = GraphHandler()
    names_dict = graphHandler.read_group_dict_from_file(group_dict_path=group_dict_path)
    friends_tree: Dict = graphHandler.load_tree_from_file(path=group_tree_path)
    edges_list = graphHandler.get_array_of_edges(prev_value="", tree=friends_tree, names_dict=names_dict)
    trimmed_list = graphHandler.trim_graph(edges_list=edges_list)
    GFull = Graph()
    GFull.add_edges(edges_list=edges_list)
    GFull.visualise("graph.html", options=options)
    G = Graph()
    G.add_edges(edges_list=trimmed_list)
    G.visualise("graph_trimmed.html", options=options)
    