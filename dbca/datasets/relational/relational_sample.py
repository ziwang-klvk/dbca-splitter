from typing import List, Set, Tuple, Iterable
import networkx as nx
from networkx import is_weakly_connected, to_nested_tuple, lexicographical_topological_sort
from collections import defaultdict
from itertools import product, combinations

from dbca.base import Compound
from dbca.sample import Sample

class RelationalCompound(Compound):
    """
    Compound representation for RelationalSample. 
    # TODO Currently supporting linear sub-graphs, need some graph to string 
    # linearization for more general sub-graphs.

    UPDATE: Supporting compounds with tree structure
    """
    def __init__(self, sub_graph: nx.DiGraph, sample_graph: nx.DiGraph = None, 
                 sid: str = None):
        super(RelationalCompound, self).__init__(sub_graph, sample_graph, sid)
        self.G = sub_graph
        self.sample_G = sample_graph if sample_graph else sub_graph

        # create unique ordering for atoms
        # UPDATE: represent the compound as a string of topological ordering + tree structure.
        tree_structure = str(to_nested_tuple(self.G.to_undirected(), root = min(self.G.nodes())))
        self._repr = '_'.join([self.G.nodes.data()[i]['rule'] for i in list(lexicographical_topological_sort(self.G))]+[tree_structure])
        
    def __repr__(self):
        return self._repr
    
    def __str__(self):
        return self._repr
    
    def __hash__(self):
        return hash(self.__repr__())
    
    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.__hash__() == other.__hash__()
            )
    
    @classmethod
    def from_edges(cls, edges: Iterable[Tuple[str, str]]):
        g = nx.DiGraph()
        g.add_edges_from(edges)
        return cls(g)
        
        

        

class RelationalSample(Sample):
    """
    Toy sample type, graph representing relations between unique entities.
    """
    def __init__(self, graph: nx.DiGraph, c_max_n_nodes: int = 4, c_max_n_branch: int = 2, name: str = ""):
        super(RelationalSample, self).__init__(graph, name)
        self.G = graph
        self.compounds_by_type = defaultdict(list)
        # consider subgraph with nodes more than 2
        self.c_max_n_nodes = c_max_n_nodes
        self.c_max_n_branch = c_max_n_branch
        
    @property
    def atoms(self) -> List[str]:
        """
        Return list of atoms. 
        Assuming atoms are simply strings.

        UPDATE: Represent atoms with rules
        """
        return list(dict(self.G.nodes(data = 'rule')).values())

    @property
    def compounds(self) -> List[str]:
        """
        For this example, we define compounds as linear sub-graphs (paths) of any length.

            
        UPDATE: add method for generating non-linear subgraphs, new parameters required for determining subgraph size.
        """

        if hasattr(self, "_compounds"):
            return self._compounds
        else:
            self._compounds = []

            new_linear_compounds = self.gen_linear_compound()

            self._compounds += new_linear_compounds

            # new_nonlinear_compounds = self.gen_nonlinear_compound()

            # self._compounds += new_nonlinear_compounds
            
            # otherwise we will double count subgraphs
            self._compounds = set(self._compounds)
            for c in self._compounds:
                self.compounds_by_type[str(c)].append(c)
            return self._compounds
        
        
    def get_occurrences(self, compound_type: str) -> Iterable[Compound]:
        """
        Return all occurences of compounds of type `compound_type`.

        """
        return self.compounds_by_type[compound_type]
    
    def compounds_types(self) -> List[str]:
        return list(self.compounds_by_type.keys())
    

    def gen_nonlinear_compound(self):
        G = self.G
        id = self.id
        c_max_n_branch = self.c_max_n_branch
        new_compounds = []
        for n_nodes in range(2, self.c_max_n_nodes+1):
            for combs in combinations(G.nodes, n_nodes):
                compound = G.subgraph(combs)
                if is_weakly_connected(compound) and max_degree(compound) <= c_max_n_branch:
                    r_compound = RelationalCompound(compound, G, id)
                    new_compounds.append(r_compound)
        return new_compounds

    def gen_linear_compound(self):
        G = self.G
        id = self.id
        new_compounds = []
        for a1, a2 in product(G.nodes(), G.nodes()):
            new_compounds += [RelationalCompound(G.edge_subgraph(p), G, id)
                             for p in list(nx.all_simple_edge_paths(G, source=a1, target=a2)) if p]

        return new_compounds


def max_degree(G: nx.DiGraph):
    return max(dict(G.degree()).values())
        
        
    
    