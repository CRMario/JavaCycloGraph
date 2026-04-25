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
        self.global_execution = True
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
        elif isinstance(statement, Return):
            self.handle_return(statement,labelling,execute)
        else:
            # just a normal statement (ex. int x = 5;)
            # these will not count for cyclomatic complexity, the ones that will do will
            # have two edges (paths they can craete in the code)
            statement.Type(self.scope)
            node = self.create_cfg_node(str(statement))
            self.graph.add_edge(self.current, node, label=labelling)
            if execute and self.global_execution:
                self.execution_path.append(node)
            self.current = node

    def handle_if(self, statement, labelling=None,execute=True):
        # verify boolean condition and recursively obtain computed_value
        statement.Type(self.scope)

        condition_node = self.create_cfg_node(f"IF: {statement.condition}")
        self.graph.add_edge(self.current,condition_node,label=labelling)
        if execute and self.global_execution:
            self.execution_path.append(condition_node)

        condition_value = self._eval_bool(statement.condition)

        before_if_execution = self.global_execution

        # if condition_value is None, both paths "execute". this is intended
        # because if we have something like a method call which will have the value
        # 'unknown' due to the limitations of the project scope, any of the paths
        # could have been taken.
        exec_true = execute and (condition_value is not False) and self.global_execution
        exec_false = execute and (condition_value is not True) and self.global_execution

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

        # in case there was a for or while inside the if which killed the execution flow of
        # the branch actually taken, go back to old global_execution
        after_true_execution = self.global_execution
        self.global_execution = before_if_execution
   
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

        if execute and self.global_execution:
            self.execution_path.append(join)

        self.current = join

        self.global_execution = after_true_execution or self.global_execution

    def handle_while(self, statement, labelling=None, execute=True):
        statement.Type(self.scope)

        condition_node = self.create_cfg_node(f"WHILE: {statement.condition}")
        self.graph.add_edge(self.current,condition_node,label=labelling)
        if execute and self.global_execution:
            self.execution_path.append(condition_node)

        # The problem with a CFG trying to simulate a partial execution is that
        # we can not check all the iterations and/or know if the loop finishes.
        # Also all variables changed during the execution of the loop become unreliable
        # for future statements or blocks of code. Consequently, the moment
        # we find a while or for loop I am just going to stop trying to figure out
        # where the execution is going and just continue with the normal CFG.

        if statement.body:
            self.scope.push()
            self.current = condition_node
            self._run_branch(statement.body,'True',execute=False)
            self.scope.pop()
            end_body = self.current
        else:
            end_body = condition_node

        join = self.create_cfg_node("END_WHILE")
        self.graph.add_edge(condition_node, join,label='False')

        if not statement.body:
            self.graph.add_edge(end_body, condition_node, label='True')
        else:
            self.graph.add_edge(end_body, condition_node)

        self.current = join
        self.global_execution = False

    def handle_for(self, statement, labelling=None, execute=True):
        statement.Type(self.scope)
        # similar to handling while but with an initialization and an update
        init_node = self.create_cfg_node(f"FOR_INIT: {statement.initialization}")
        self.graph.add_edge(self.current,init_node,label=labelling)
        if execute and self.global_execution:
            self.execution_path.append(init_node)
        condition_node = self.create_cfg_node(f"FOR: {statement.condition}")
        self.graph.add_edge(init_node,condition_node)
        if execute and self.global_execution:
            self.execution_path.append(condition_node)

        if statement.body:
            self.scope.push()
            self.current = condition_node
            self._run_branch(statement.body,'True',execute=False)
            self.scope.pop()
            end_body = self.current
            # if it had a body we make an update node at the end
            update_node = self.create_cfg_node(f"FOR_UPDATE: {statement.update}")
            self.graph.add_edge(end_body, update_node, label='True')
            end_body = update_node
        else:
            end_body = condition_node
        
        join = self.create_cfg_node("END_FOR")
        self.graph.add_edge(condition_node, join,label='False')

        if not statement.body:
            self.graph.add_edge(end_body, condition_node, label='True')
        else:
            self.graph.add_edge(end_body, condition_node)

        self.current = join
        self.global_execution = False

    def handle_do_while(self, statement, labelling=None, execute=True):
        statement.Type(self.scope)
        self.scope.push()
        first_body_node = self.nodes
        self._run_branch(statement.body, labelling, execute=execute)
        self.scope.pop()

        end_body = self.current

        condition_node = self.create_cfg_node(f"DO_WHILE: {statement.condition}")
        self.graph.add_edge(end_body, condition_node)
        if execute and self.global_execution:
            self.execution_path.append(condition_node)

        join = self.create_cfg_node("END_DO_WHILE")
        self.graph.add_edge(condition_node, first_body_node, label='True')
        self.graph.add_edge(condition_node, join, label='False')

        self.current = join
        self.global_execution = False

    def handle_switch(self, statement, labelling=None, execute=True):
        # verify boolean condition and recursively obtain computed_value
        statement.Type(self.scope)

        switch_node = self.create_cfg_node(f"SWITCH: {statement.expr}")
        self.graph.add_edge(self.current, switch_node, label=labelling)

        if execute and self.global_execution:
            self.execution_path.append(switch_node)

        join = self.create_cfg_node("END_SWITCH")

        before_switch_execution = self.global_execution

        # which case execs
        switch_value = statement.expr.computed_value

        # create all case nodes
        case_nodes = {}
        for case in statement.cases:
            case_node = self.create_cfg_node(f"CASE {case.value}")
            self.graph.add_edge(switch_node, case_node, label=str(case.value))
            case_nodes[id(case)] = case_node

        def _case_matches(case):
            if case.value == 'default':
                return True  # default as last if it exists
            if switch_value is None:
                return None  # unknown value in the switch
            val = case.value
            # compare case value to switch value
            if hasattr(val, 'computed_value'):
                return val.computed_value == switch_value
            return None

        # find which case is the path taken
        matched = None
        has_default = any(c.value == 'default' for c in statement.cases)
        for case in statement.cases:
            m = _case_matches(case)
            # if case matches we found the path
            if m is True:
                matched = case
                break
            elif m is None: # unknown value in the switch we can't know the case
                matched = None
                break

        any_branch_alive = False # are there any branches that allow execution?

        for case in statement.cases:
            case_node = case_nodes[id(case)]

            if matched is None:
                # if we don't know we say that the switch "executes all" (it doesnt but we cant know)
                exec_this = execute and before_switch_execution
            else: # False or True, we know theres a execution path, is it this one? (case is matched)
                exec_this = execute and before_switch_execution and (case is matched)
            
            #restore global execution in case a previous non-executing branch had a loop inside and disabled it
            self.global_execution = before_switch_execution
            self.current = case_node

            self.scope.push()
            for stmt in case.body:
                self.handle_statement(stmt, execute=exec_this)
            self.scope.pop()

            # keep track if theres any branch alive
            any_branch_alive = any_branch_alive or self.global_execution

            self.graph.add_edge(self.current, join)

        if not has_default:
            self.graph.add_edge(switch_node, join, label='default')

        if execute and before_switch_execution:
            self.execution_path.append(join)

        self.global_execution = any_branch_alive
        self.current = join

    def handle_try(self, statement, labelling=None, execute=True):
        statement.Type(self.scope)

        try_node = self.create_cfg_node("TRY")
        self.graph.add_edge(self.current, try_node, label=labelling)
        if execute and self.global_execution:
            self.execution_path.append(try_node)

        before_try_execution = self.global_execution

        # try body
        self.scope.push()
        self.current = try_node
        self._run_branch(statement.body, None, execute=execute)
        self.scope.pop()
        end_try = self.current
        after_try_execution = self.global_execution

        join = self.create_cfg_node("END_TRY")

        # normal path with no exception
        self.graph.add_edge(end_try, join)

        # mark all catches as potentially executing
        any_catch_alive = False

        for catch in statement.catch:
            self.global_execution = before_try_execution
            catch_node = self.create_cfg_node(f"CATCH: {catch.exception} {catch.variable}")
            self.graph.add_edge(try_node, catch_node, label='exception')

            self.scope.push()
            self.scope.add_variable(catch.variable, catch.exception)
            self.current = catch_node
            for stmt in catch.body:
                self.handle_statement(stmt, execute=execute)
            self.scope.pop()

            any_catch_alive = any_catch_alive or self.global_execution
            self.graph.add_edge(self.current, join)

        # finally always executes if it exists
        if statement.finally_do:
            self.global_execution = before_try_execution
            finally_node = self.create_cfg_node("FINALLY")
            # finally connects from join (runs after try or catch)
            self.graph.add_edge(join, finally_node)

            real_join = self.create_cfg_node("END_FINALLY")

            self.current = finally_node
            self.scope.push()
            self._run_branch(statement.finally_do, None, execute=execute)
            self.scope.pop()

            self.graph.add_edge(self.current, real_join)

            if execute and self.global_execution:
                self.execution_path.append(finally_node)
                self.execution_path.append(real_join)

            self.global_execution = after_try_execution or any_catch_alive
            self.current = real_join
        else:
            if execute and self.global_execution:
                self.execution_path.append(join)
            self.global_execution = after_try_execution or any_catch_alive
            self.current = join

    def handle_return(self, statement, labelling=None, execute=True):
        statement.Type(self.scope)

        label = f"RETURN: {statement.value}" if statement.value is not None else "RETURN"
        node = self.create_cfg_node(label)
        self.graph.add_edge(self.current, node, label=labelling)

        if execute and self.global_execution:
            self.execution_path.append(node)

        self.current = node

        # return kills execution tracking — nothing after this in the method runs
        self.global_execution = False
        self.returned = True

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