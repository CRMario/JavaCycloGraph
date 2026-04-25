import networkx as nx
from Classes import *
from Scope import Scope

class CFGBuilder:
    def __init__(self):
        self.graphs = {} # graph per methods
        self.scope = Scope()
        self.errors = []

    def build(self, program):
        # iterate through the methods of the classes of the program
        # each method is a graph, we will have as many graphs as methods
        for classp in program.classes:
            self.scope.current_class = classp.name
            for method in classp.methods:
                self.build_method(classp.name, method)
        return self.graphs
    
    def build_method(self, class_name, method):
        self.graph = nx.DiGraph()
        self.nodes = 0 # keep track of all nodes
        self.execution_path = []
        self.error_node = None
        self.returned = False
        self.scope.push() #method created so new scope

        for param_type, param_name in method.params:
            self.scope.add_variable(param_name, param_type)

        start = self.create_cfg_node("START")
        self.current = start # we are at the start node
        self.execution_path.append(start)

        # add all the possible intermediate nodes found in each statement of the method
        try:
            for statement in method.body:
                self.handle_statement(statement)
        except SemanticException as e:
            self.errors.append(str(e))
            self.error_node = self.current

        # we finished looking at the method, create end node
        end = self.create_cfg_node("END")
        if self.current is not None:
            self.graph.add_edge(self.current, end)
            self.execution_path.append(end)

        # go back to previous scope
        self.scope.pop()

        # save the graph
        self.graphs[f'{class_name}.{method.name}'] = {
            'graph': self.graph,
            'execution_path': self.execution_path,
            'error_node': self.error_node,
        }
    
    def create_cfg_node(self, node_name):
        node_id = self.nodes
        self.graph.add_node(node_id, label=node_name)
        self.nodes += 1
        return node_id
    
    def handle_statement(self, statement,labelling=None, execute=True):
        """Handle the possible statements that can add execution paths in the code
        and that add up to cyclomatic complexity. """
        if isinstance(statement, If):
            self.handle_if(statement,labelling,execute)
        elif isinstance(statement, While):
            self.handle_while(statement,labelling,execute)
        elif isinstance(statement, For):
            self.handle_for(statement,labelling,execute)
        elif isinstance(statement, DoWhile):
            self.handle_do_while(statement,labelling,execute)
        elif isinstance(statement, Switch):
            self.handle_switch(statement,labelling,execute)
        elif isinstance(statement, Try):
            self.handle_try(statement,labelling,execute)
        #elif isinstance(statement, Return):
        #    self.handle_return(statement,labelling,execute)
        else:
            # just a normal statement (ex. int x = 5;)
            # these will not count for cyclomatic complexity, the ones that will do will
            # have two edges (paths they can craete in the code)
            statement.Type(self.scope)
            node = self.create_cfg_node(str(statement))
            self.graph.add_edge(self.current, node, label=labelling)
            if execute:
                self.execution_path.append(node)
            self.current = node

    def handle_if(self, statement, labelling=None,execute=True):
        # verify boolean condition and recursively obtain computed_value
        statement.Type(self.scope)

        condition_node = self.create_cfg_node(f"IF: {statement.condition}")
        self.graph.add_edge(self.current,condition_node,label=labelling)
        if execute:
            self.execution_path.append(condition_node)

        condition_value = self._eval_bool(statement.condition)

        # if condition_value is None, both paths "execute". this is intended
        # because if we have something like a method call which will have the value
        # 'unknown' due to the limitations of the project scope, any of the paths
        # could have been taken.
        exec_true = execute and (condition_value is not False)
        exec_false = execute and (condition_value is not True)

        # we have to handle the first case in order to add the label "true" or
        # "false" in each edge
        # true branch
        if statement.true:
            self.scope.push()
            self.current = condition_node
            self._run_branch(statement.true,'True',execute=exec_true)
            self.scope.pop()
            end_true = self.current # where the true branch ended
        else:
            end_true = condition_node #empty true branch which is probably unlikely
   
        # false branch
        if statement.false:
            self.scope.push()
            self.current = condition_node
            self._run_branch(statement.false,'False',execute=exec_false)
            self.scope.pop()
            end_false = self.current
        else:
            # no false branch
            end_false = condition_node
   
        join = self.create_cfg_node("END_IF")
        if not statement.true: # if there's no true statement
            self.graph.add_edge(end_true, join, label='True')
        else:
            self.graph.add_edge(end_true, join)
        # if there was no code for false, then we still have no false edge
        # add an edge from the start of the condition to the end
        if not statement.false:
            self.graph.add_edge(end_false,join,label='False')
        else: # there was code for false and we have an edge labeled 'false'
            # we just join in this case like with the true path
            self.graph.add_edge(end_false,join)

        if execute:
            self.execution_path.append(join)

        self.current = join

    def handle_while(self, statement, labelling=None, execute=True):
        statement.Type(self.scope)

        condition_node = self.create_cfg_node(f"WHILE: {statement.condition}")
        self.graph.add_edge(self.current,condition_node,label=labelling)
        if execute:
            self.execution_path.append(condition_node)

        condition_value = self._eval_bool(statement.condition)

        exec = execute and (condition_value is not False)

        self.current = condition_node

        # TODO
        if statement.body:
            first_statement = statement.body[0]
            self.handle_statement(first_statement,label='True')
            for stmt in statement.body[1:]:
                self.handle_statement(stmt)
            end_body = self.current
        else:
            end_body = condition_node

        join = self.create_cfg_node("END_WHILE")

        self.graph.add_edge(condition_node, join,label='False')
        if not statement.body:
            self.graph.add_edge(end_body, condition_node, label='True')
        else:
            self.graph.add_edge(end_body, condition_node)

    def handle_for(self, statement, labelling=None):
        # similar to handling while but with an initialization and an update
        init_node = self.create_cfg_node(f"FOR_INIT: {statement.initialization}")
        self.graph.add_edge(self.current,init_node,label=labelling)
        
    # helpers
    def _run_branch(self, statements, labelling, execute=True):
        # i need this to put the first edge in a bifurcation with the label True or
        # False and also to indicate if the nodes belong to the execution path

        if not statements:
            return
        
        self.handle_statement(statements[0], labelling, execute)
        for stmt in statements[1:]:
            self.handle_statement(stmt, execute=execute)
            if self.returned:
                break

    def _eval_bool(self, condition):
        # if its a bool return it directly
        if hasattr(condition, 'value') and isinstance(condition.value, bool):
            return condition.value
        
        # if it was an expression check if the value it computed is a bool
        val = getattr(condition, 'computed_value', None)
        
        if isinstance(val, bool):
            return val
        
        # return none otherwise
        return None