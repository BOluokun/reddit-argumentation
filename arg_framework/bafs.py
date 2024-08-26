import networkx as nx
import matplotlib.pyplot as plt
import matplotlib

# matplotlib.use('TkAgg')

def reverse_bfs_layout(graph, source_node):
  """
  Performs a BFS layout on a directed graph in reverse order using predecessors.

  Args:
      graph: The NetworkX DiGraph object.
      source_node: The starting node for the BFS traversal.

  Returns:
      A dictionary containing the BFS layout with node keys and positions (levels).
  """
  predecessors = nx.algorithms.traversal.breadth_first_search.bfs_predecessors(graph, source_node)
  predecessors_dict = dict(predecessors)
  layout = {source_node: 0}  # Initialize layout with source node at level 0
  level = 1
  for node, pred_list in predecessors_dict.items():
    if not pred_list:
      continue  # Skip nodes without predecessors
    layout[node] = level
    level += 1
  return layout


class BAF:

    def __init__(self, explanandum: dict, arguments: list[tuple], attacks: list[tuple] = None, supports: list[tuple] = None):
        self._graph = nx.DiGraph()
        # Populate the BAF graph with given arguments and support/attack edges
        self._graph.add_node(0, **explanandum)
        self.add_arguments(arguments)
        self.attackers = {i: [] for i in self._graph.nodes()}
        self.supporters = {i: [] for i in self._graph.nodes()}
        if attacks:
            self.add_attacks(attacks)
        if supports:
            self.add_supports(supports)

    def add_arguments(self, args: list[tuple]):
        for arg in args:
            self._graph.add_node(arg[0], **arg[1])

    def add_attacks(self, atts: list[tuple]):
        for (s, e) in atts:
            assert s != 0
            assert s in self._graph.nodes() and e in self._graph.nodes()
            self._graph.add_edge(s, e, edge_type='attack')
            self.attackers[e].append(s)

    def add_supports(self, sups):
        for (s, e) in sups:
            assert s != 0
            assert s in self._graph.nodes() and e in self._graph.nodes()
            self._graph.add_edge(s, e, edge_type='support')
            self.supporters[e].append(s)

    def get_arguments(self):
        return self._graph.nodes(data=True)

    def get_argument(self, a: int):
        return a, self._graph.nodes[a]

    def get_supporters(self, a):
        # supporters = [b for b, attrs in self._graph.pred[a].items() if attrs['edge_type'] == 'support']
        supporters = self.supporters[a]
        return supporters

    def get_attackers(self, a):
        # attackers = [b for b, attrs in self._graph.pred[a].items() if attrs['edge_type'] == 'attack']
        attackers = self.attackers[a]
        return attackers

    def get_paths(self, source, target):
        return list(nx.all_simple_paths(self._graph, source, target))

    def get_pros(self):
        # pros are the arguments that have a path to the explanandum that has an even number of attack edges
        pros = []
        for node in self._graph.nodes():
            paths = self.get_paths(node, 0)
            for path in paths:
                attacks = [
                    i for i in range(len(path) - 1)
                    if self._graph.edges[path[i], path[i + 1]]['edge_type'] == 'attack'
                ]
                if len(attacks) % 2 == 0:
                    pros.append(node)
                    break
        return pros

    def get_cons(self):
        # cons are the arguments that have a path to the explanandum that has an odd number of attack edges
        cons = []
        for node in self._graph.nodes():
            paths = self.get_paths(node, 0)
            for path in paths:
                attacks = [
                    i for i in range(len(path) - 1)
                    if self._graph.edges[path[i], path[i + 1]]['edge_type'] == 'attack'
                ]
                if len(attacks) % 2 == 1:
                    cons.append(node)
                    break
        return cons

    def display_graph(self, layout='planar'):
        if layout == 'planar':
            pos = nx.planar_layout(self._graph)
        elif layout == 'bfs':
            pos = reverse_bfs_layout(self._graph, 0)
        elif layout == 'kamada':
            pos = nx.kamada_kawai_layout(self._graph)
        edge_colours = ['red' if d['edge_type'] == 'attack' else 'green' for (_, _, d) in self._graph.edges(data=True)]
        nx.draw_networkx(self._graph, pos=pos, edge_color=edge_colours)
        limits = plt.axis("off")
        plt.show()


if __name__ == '__main__':
    e = {'text': 'this is a correct BAF'}
    args = [(1, {'text': 'hi'}), (2, {'text': 'this'}), (3, {'text': 'is'}), (4, {'text': 'a'}), (5, {'text': 'test'})]
    supports = [(1, 0), (2, 1)]
    attacks = [(3, 0), (2, 3)]
    baf = BAF(e, args, attacks, supports)
    # print(baf.get_arguments())
    # print(baf.get_argument(0))
    # print(f'Supporters of 0 are {baf.get_supporters(0)}')
    # print(f'Attackers of 3 are {baf.get_attackers(3)}')
    print(f'Pros are {baf.get_pros()}')
    print(f'Cons are {baf.get_cons()}')
    baf.display_graph()
