# Variable_______________________________________________________________________________

# Database_______________________________________________________________________________

class Database:
    def __init__(self):
        self._database:list[Rule] = []
        self._callmap:dict[str, callable] = {}
        self._str_output = ""
        self._int_output = 0
        self._bool_output = False
    
    def __str__(self):
        return "\n".join(str(rule) for rule in self._database)

    def add_callmap(self, callmap:dict[str, callable]):
        self._callmap = self._callmap | callmap

    def set_str(self, s:str):
        self._str_output = s

    def set_int(self, i:int):
        self._int_output = i

    def set_bool(self, b:bool):
        self._bool_output = b

    def get_str(self):
        return self._str_output

    def get_int(self):
        return self._int_output

    def get_bool(self):
        return self._bool_output

    @property
    def callmap(self):
        return self._callmap

    def run(self, rule:"Rule"):
        index = self.find_rule(rule)
        if index != -1:
            return self._database[index].run()
        return False

    def find_rule(self, rule:"Rule"):
        for i in range(len(self._database)):
            if self._database[i] == rule:
                return i
        return -1

    def assert_rule(self, rule:"Rule"):
        if self.find_rule(rule) == -1:
            self._database.append(rule)
            return True
        return False

    def retract_rule(self, rule:"Rule"):
        indice = self.find_rule(rule)
        if indice != -1:
            self._database.pop(indice)
            return True
        return False

# Statements_____________________________________________________________________________

class Statement:
    def __init__(self, db:Database, name:str, args:list[str]):
        self._db = db
        self._name = name
        self._args = args
    
    def run(self) -> bool:
        pass

class AssertStatement(Statement):
    def __init__(self, db:Database, name:str, args:list[str]):
        super().__init__(db, name, args)
    
    def run(self) -> bool:
        return self._db.assert_rule(Rule(self._name, self._args))

class RetractStatement(Statement):
    def __init__(self, db:Database, name:str, args:list[str]):
        super().__init__(db, name, args)
    
    def run(self) -> bool:
        return self._db.retract_rule(Rule(self._name, self._args))

class RunStatement(Statement):
    def __init__(self, db:Database, name:str, args:list[str]):
        super().__init__(db, name, args)
    
    def run(self) -> bool:
        return self._db.run(Rule(self._name, self._args))

class DefineStatement(Statement):
    def __init__(self, db:Database, name:str, args:list[str], statements:list[Statement]):
        super().__init__(db, name, args)
        self._statements = statements
    
    def run(self) -> bool:
        return self._db.assert_rule(Rule(self._name, self._args, self._statements))

class CallStatement(Statement):
    def __init__(self, db:Database, name:str, args:list[str]):
        super().__init__(db, name, args)
    
    def run(self) -> bool:
        if self._name in self._db.callmap:
            self._db.callmap[self._name](*self._args) 
            return True
        else:
            return False

class IfStatement(Statement):
    def __init__(self, db:Database, name:str, args:list[str], 
        antecedent:list[Statement], consequent:list[Statement], alternate:list[Statement]
    ):
        super().__init__(db, name, args)
        self._antecedent = antecedent
        self._consequent = consequent
        self._alternate = alternate

    def run(self) -> bool:
        if all(an.run() for an in self._antecedent):
            return all(co.run() for co in self._consequent)
        return all(al.run() for al in self._alternate)

class EitherStatement(Statement):
    def __init__(self, db:Database, name:str, args:list[str], statements:list[Statement]):
        super().__init__(db, name, args)
        self._statements = statements

    def run(self) -> bool:
        return any(s.run() for s in self._statements)
    
class AllStatement(Statement):
    def __init__(self, db:Database, name:str, args:list[str], statements:list[Statement]):
        super().__init__(db, name, args)
        self._statements = statements

    def run(self) -> bool:
        return all(s.run() for s in self._statements)

class NotStatement(Statement):
    def __init__(self, db:Database, name:str, args:list[str]):
        super().__init__(db, name, args)
    
    def run(self) -> bool:
        return not self._db.run(Rule(self._name, self._args))

class FindStatement(Statement):
    def __init__(self, db:Database, name:str, args:list[str]):
        super().__init__(db, name, args)
    
    def run(self) -> bool:
        pass

# Rule___________________________________________________________________________________

class Rule:
    def __init__(self, name:str, args:list[str], statements:list[Statement]=[]):
        self._name = name
        self._args = args
        self._statements = statements
    
    def __str__(self):
        return f"{self._name}({str(self._args).strip("[]")}) + {len(self._statements)}"

    def __eq__(self, other:"Rule"):
        return self._name == other._name and self._args == other._args
    
    def run(self) -> bool:
        if self._statements != []:
            return all(statement.run() for statement in self._statements)
        return True
