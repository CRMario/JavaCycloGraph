import networkx as nx
from Classes import *
from Scope import Scope

class CFGBuilder:
    def __init__(self):
        self.graphs = {} # graph per methods
        self.scope = Scope()

    def build(self, program):
        # iterate through the methods of the classes of the program
        # each method is a graph, we will have as many graphs as methods
        for classp in program.classes:
            for method in classp.methods:
                self.build_method(classp.name, method)
        return self.graphs
    
    def build_method(self, class_name, method):
        self.graph = nx.DiGraph
        self.nodes = 0 # keep track of all nodes
        self.scope.push() #method created so new scope

        start = self.create_cfg_node("START")
        self.current = start # we are at the start node

        # add all the possible intermediate nodes found in each statement of the method
        for statement in method.body:
            self.handle_statement(statement)

        # we finished looking at the method, create end node
        end = self.create_cfg_node("END")
        self.graph.add_edge(self.current, end)

        # go back to previous scope
        self.scope.pop()

        # save the graph in our program methods dict
        self.graphs[f'{class_name}.{method.name}'] = self.graph
    
    def create_cfg_node(self, node_name):
        node_id = self.nodes
        self.graph.add_node(node_id, label=node_name)
        self.nodes += 1
        return node_id
    
    def handle_statement(self, stmt):
        """Handle the possible statements that can add execution paths in the code
        and that add up to cyclomatic complexity. """
        if isinstance(stmt, If):
            self.handle_if(stmt)
        elif isinstance(stmt, While):
            self.handle_while(stmt)
        elif isinstance(stmt, For):
            self.handle_for(stmt)
        elif isinstance(stmt, DoWhile):
            self.handle_do_while(stmt)
        elif isinstance(stmt, Switch):
            self.handle_switch(stmt)
        elif isinstance(stmt, Try):
            self.handle_try(stmt)
        elif isinstance(stmt, Return):
            self.handle_return(stmt)
        else:
            # just a normal statement (ex. int x = 5;)
            # these will not count for cyclomatic complexity, the ones that will do will
            # have two edges (paths they can craete in the code)
            node = self.new_node(str(stmt))
            self.graph.add_edge(self.current, node)
            self.current = node