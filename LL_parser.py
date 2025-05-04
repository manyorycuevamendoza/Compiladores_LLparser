import re
import json

class LLParser:
    def __init__(self, grammar_file="grammar.txt"):
        self.grammar_file = grammar_file
        self.variables = []
        self.terminales = []
        self.start = []
        self.grammar = {}
        self.tabla = {}
        self.reglas = {}
        self.epsilon = 'ε'
        
        self.load_grammar()
        self.process_grammar()
        self.calculate_first()
        self.calculate_follow()
        self.build_parse_table()
        
    def load_grammar(self):
        with open(self.grammar_file, "r") as archivo:
            sent = archivo.readlines()
        # Clean and process grammar lines
        rules = []
        for i in range(len(sent)):
            line = sent[i].strip()
            if not line or (not '->' in line and not '→' in line):
                continue
            if '->' in line:
                left, right = line.split('->', 1)
            else:
                left, right = line.split('→', 1)
            left = left.strip()
            rules.append((left, right.strip()))
        # Identify start symbol
        if rules:
            self.start = [rules[0][0]]
        else:
            self.start = []
        # Identify variables and terminals
        self.variables = []
        self.terminales = []
        for left, right in rules:
            if left not in self.variables and left not in self.start:
                self.variables.append(left)
            productions = [p.strip() for p in right.split('|')]
            for prod in productions:
                symbols = [s for s in prod.split(' ') if s] if prod != self.epsilon else [self.epsilon]
                for sym in symbols:
                    if sym == self.epsilon:
                        continue
                    if sym.isupper() or (len(sym) > 1 and sym[0].isupper()):
                        # Considera como variable si empieza con mayúscula
                        if sym not in self.variables and sym not in self.start:
                            self.variables.append(sym)
                    else:
                        if sym not in self.terminales:
                            self.terminales.append(sym)

    def process_grammar(self):
        # Initialize grammar structure
        for i in self.start + self.variables:
            self.grammar[i] = {"tipo": "V", "first": [], "follow": []}
        for j in self.terminales:
            self.grammar[j] = {"tipo": "T", "first": [j]}
        # Process rules
        rule_count = 1
        for line in open(self.grammar_file, "r"):
            line = line.strip()
            if not line or (not '->' in line and not '→' in line):
                continue
            try:
                if '->' in line:
                    left, right = line.split('->', 1)
                else:
                    left, right = line.split('→', 1)
                left = left.strip()
                productions = [p.strip() for p in right.split('|')]
                for prod in productions:
                    # Divide la producción en símbolos, ignorando espacios
                    symbols = [s for s in prod.split(' ') if s] if prod != self.epsilon else [self.epsilon]
                    rule_name = f"regla{rule_count}"
                    self.reglas[rule_name] = {
                        "Izq": left,
                        "Der": symbols
                    }
                    rule_count += 1
            except Exception as e:
                print(f"Skipping invalid line: '{line}'. Error: {e}")
                continue
                
    def calculate_first(self):
        # Inicializa FIRST para todos los símbolos
        for symbol in self.grammar:
            self.grammar[symbol]["first"] = []
        changed = True
        while changed:
            changed = False
            for rule in self.reglas.values():
                left = rule["Izq"]
                right = rule["Der"]
                # Si la producción es ε
                if right == [self.epsilon]:
                    if self.epsilon not in self.grammar[left]["first"]:
                        self.grammar[left]["first"].append(self.epsilon)
                        changed = True
                    continue
                # Para cada producción X -> X1 X2 ... Xn
                add_epsilon = True
                for symbol in right:
                    # Si es terminal o ε
                    if symbol in self.terminales or symbol == self.epsilon:
                        if symbol not in self.grammar[left]["first"]:
                            self.grammar[left]["first"].append(symbol)
                            changed = True
                        add_epsilon = False
                        break
                    # Si es no terminal
                    else:
                        for s in self.grammar[symbol]["first"]:
                            if s != self.epsilon and s not in self.grammar[left]["first"]:
                                self.grammar[left]["first"].append(s)
                                changed = True
                        if self.epsilon not in self.grammar[symbol]["first"]:
                            add_epsilon = False
                            break
                if add_epsilon:
                    if self.epsilon not in self.grammar[left]["first"]:
                        self.grammar[left]["first"].append(self.epsilon)
                        changed = True

    def calculate_follow(self):
        # Inicializa FOLLOW para todos los no terminales (incluyendo el símbolo de arranque)
        nonterminals = self.start + self.variables
        for var in nonterminals:
            self.grammar[var]["follow"] = []
        if self.start:
            # El símbolo de arranque siempre lleva '$' en su FOLLOW
            self.grammar[self.start[0]]["follow"] = ["$"]

        changed = True
        while changed:
            changed = False
            for rule in self.reglas.values():
                left = rule["Izq"]
                right = rule["Der"]
                for i, B in enumerate(right):
                    # Si B es un no terminal (incluye al start)
                    if B in nonterminals:
                        # Miramos la "cola" gamma después de B
                        gamma = right[i+1:]
                        first_gamma = set()
                        add_follow = False

                        # Si hay símbolos en gamma, calculamos FIRST(gamma)
                        if gamma:
                            add_epsilon = True
                            for symbol in gamma:
                                if symbol in self.terminales:
                                    first_gamma.add(symbol)
                                    add_epsilon = False
                                    break
                                else:
                                    # symbol es no terminal
                                    for s in self.grammar[symbol]["first"]:
                                        if s != self.epsilon:
                                            first_gamma.add(s)
                                    if self.epsilon not in self.grammar[symbol]["first"]:
                                        add_epsilon = False
                                        break
                            if add_epsilon:
                                # Si todos los símbolos de gamma pueden derivar ε
                                add_follow = True
                        else:
                            # Si gamma está vacío, tomamos FOLLOW(left)
                            add_follow = True

                        # 1) FIRST(gamma) \ {ε} se añade a FOLLOW(B)
                        for terminal in first_gamma:
                            if terminal not in self.grammar[B]["follow"]:
                                self.grammar[B]["follow"].append(terminal)
                                changed = True

                        # 2) Si ε ∈ FIRST(gamma) o gamma vacío, FOLLOW(left) ⊆ FOLLOW(B)
                        if add_follow:
                            for sym in self.grammar[left]["follow"]:
                                if sym not in self.grammar[B]["follow"]:
                                    self.grammar[B]["follow"].append(sym)
                                    changed = True

    def build_parse_table(self):
        # Inicializa la tabla de análisis LL(1) con tokens completos
        for i in self.start + self.variables:
            self.tabla[i] = {}
            for j in self.terminales + ["$"]:
                self.tabla[i][j] = []
        # Llena la tabla de análisis
        for rule in self.reglas.values():
            left = rule["Izq"]
            right = rule["Der"]
            # Calcula FIRST(der)
            first_set = set()
            add_epsilon = False
            if right == [self.epsilon]:
                add_epsilon = True
            else:
                for symbol in right:
                    if symbol in self.terminales:
                        first_set.add(symbol)
                        break
                    elif symbol in self.variables:
                        first_set.update([s for s in self.grammar[symbol]["first"] if s != self.epsilon])
                        if self.epsilon not in self.grammar[symbol]["first"]:
                            break
                    else:
                        break
                else:
                    add_epsilon = True
            # Para cada terminal en FIRST(der)\{ε}, agrega la regla
            for terminal in first_set:
                self.tabla[left][terminal].append(rule)
            # Si FIRST(der) contiene ε, agrega la regla para cada símbolo en FOLLOW(left)
            if add_epsilon:
                for follow_symbol in self.grammar[left]["follow"]:
                    self.tabla[left][follow_symbol].append(rule)

    def get_parsing_table(self):
        """
        Devuelve la cabecera y las filas de la tabla LL(1) de análisis.
        """
        variables = self.start + self.variables
        terminals = self.terminales + ["$"]
        header = ["NT"] + terminals
        rows = []
        for A in variables:
            row = [A]
            for t in terminals:
                prods = self.tabla[A].get(t, [])
                cell = " / ".join(f"{r['Izq']}→{''.join(r['Der'])}" for r in prods) if prods else "-"
                row.append(cell)
            rows.append(row)
        return header, rows

    def get_error_recovery_table(self):
        """
        Devuelve la cabecera y las filas de la tabla de recuperación de errores (panic mode).
        Marca:
            – EXT (extract) si el token está en Follow(A)
            – EP  (explore) si no está ni en First(A) ni en Follow(A)
            – '-' en caso contrario
        """
        variables = self.start + self.variables
        terminals = self.terminales + ["$"]
        header = ["NT"] + terminals
        rows = []

        for A in variables:
            firstA  = set(self.grammar[A]["first"])
            followA = set(self.grammar[A]["follow"])
            row = [A]
            for t in terminals:
                if t in followA:
                    cell = "EXT"
                elif t not in firstA and t not in followA:
                    cell = "EP"
                else:
                    cell = "-"
                row.append(cell)
            rows.append(row)

        return header, rows

    def analyze_string(self, input_string):
        # 1) Tokenizamos y preparamos pila
        tokens = [t for t in input_string.strip().split(' ') if t] + ['$']
        stack  = ['$'] + self.start[::-1]
        pos    = 0
        steps  = []

        while True:
            top     = stack[-1]
            current = tokens[pos]
            before_stack = ' '.join(stack)
            before_input = ' '.join(tokens[pos:])

            # 2.1) Caso de aceptación
            if top == '$' and current == '$':
                # opcional: podrías registrar accept aquí si quieres
                return True, steps

            # 2.2) No terminal → expansión
            if top in (self.start + self.variables):
                entry = self.tabla[top].get(current, [])
                if not entry:
                    return False, steps
                rule = entry[0]
                rule_str = f"{rule['Izq']} -> " + (
                    ' '.join(rule['Der']) 
                    if rule['Der'] != [self.epsilon] 
                    else self.epsilon
                )
                # registro ANTES de cambiar la pila
                steps.append((before_stack, before_input, rule_str))

                # ahora modifico la pila
                stack.pop()
                if rule['Der'][0] != self.epsilon:
                    for sym in reversed(rule['Der']):
                        stack.append(sym)
                continue

            # 2.3) Terminal o '$' → match
            if top in self.terminales or top == '$':
                if top == current:
                    # registro ANTES de hacer pop/avanzar
                    steps.append((before_stack, before_input, f"match {current}"))
                    stack.pop()
                    pos += 1
                    continue
                else:
                    return False, steps

            # 2.4) Cualquier otro caso = error
            return False, steps


    def get_grammar_info(self):
        info = {
            "variables": self.variables,
            "terminals": self.terminales,
            "start": self.start,
            "rules": self.reglas,
            "first_sets": {k: v["first"] for k, v in self.grammar.items()},
            "follow_sets": {k: v["follow"] for k, v in self.grammar.items() if k in self.variables + self.start}
        }
        return info
        
    def get_parse_table(self):
        return self.tabla




# For backward compatibility
if __name__ == "__main__":
    parser = LLParser()
    print("TABLA")
    print("\n")
    print(f"{'Símbolo':<10} {'Tipo':<8} {'FIRST':<20} {'FOLLOW':<20}")
    print("-" * 60)

    for simbolo, datos in parser.grammar.items():
        tipo = "V" if simbolo in parser.variables + parser.start else "T"
    first = ", ".join(datos.get('first', []))
    follow = ", ".join(datos.get('follow', [])) if 'follow' in datos else "-"
    print(f"{simbolo:<10} {tipo:<8} {first:<20} {follow:<20}")

    print("\n")
    print("\n")
    print("MATRIZ")

    terminales = parser.terminales + ["$"]
    print(f"{'':20}", end="")
    for t in terminales:
        print(f"{t:<20}", end="")
    print()

    print("-" * (12 + 20 * len(terminales)))
    for no_terminal, reglas in parser.tabla.items():
        print(f"{no_terminal:20}", end="")
    for t in terminales:
        producciones = reglas[t]
        if producciones:
            produccion_strs = ["{} → {}".format(p["Izq"], " ".join(p["Der"])) for p in producciones]
            print(f"{' / '.join(produccion_strs):<20}", end="")
        else:
            print(f"{'-':<20}", end="")
    print()