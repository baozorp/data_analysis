from pyvis.network import Network
import networkx as nx
import json
from typing import Tuple, List, Dict


class GraphViz:

    def __init__(self) -> None:
        pass

    def load_tree_from_file(self, path: str):
        with open(path, "r") as friends_tree_file:
            tree = json.load(friends_tree_file)
        if not isinstance(tree, dict):
            return {}
        return tree if tree else {}
    
    def get_array_of_edges(self, prev_value: str, tree: dict) -> List[Tuple[str, str]]:
        result_array: List[Tuple[str, str]] = []

        if prev_value != "":
            if isinstance(tree, Dict):
                subkeys_list = tree.keys()
                for sub_key in subkeys_list:
                    result_array.append((prev_value, sub_key))
                    result_array += self.get_array_of_edges(prev_value=sub_key, tree=tree[sub_key])
            elif isinstance(tree, List):
                for i in tree:
                    result_array.append((prev_value, i))
        else:
            for key in tree:
                if isinstance(tree[key], Dict):
                    subkeys_list = tree[key].keys()
                    for sub_key in subkeys_list:
                        result_array.append((key, sub_key))
                        result_array += self.get_array_of_edges(prev_value=sub_key, tree=tree[key][sub_key])
                elif isinstance(tree[key], List):
                    for i in tree[key]:
                        result_array.append((key, i))
        return result_array

if __name__=="__main__":
    graphViz = GraphViz()
    friends_tree: Dict = graphViz.load_tree_from_file(path="group_tree.json")
    edges_array = graphViz.get_array_of_edges(prev_value="", tree=friends_tree)
    G = nx.Graph()
    G.add_edges_from(edges_array)
    net = Network(notebook=False)
    # Отключаем анимацию
    options = """
    var options = {
      "physics": {
        "enabled": true,
        "stabilization": {
          "enabled": true,
          "iterations": 24
        },
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": {
          "gravitationalConstant": -10,
          "centralGravity": 0.005,
          "springLength": 100,
          "springConstant": 0.08,
          "damping": 0.4
        },
        "timestep": 0.5,
        "adaptiveTimestep": true
      }
    }
    """
    net.set_options(options)
    
    net.from_nx(G)
    net.show("graph.html", notebook=False)