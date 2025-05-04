import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
from LL_parser import LLParser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout

class LLParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LL(1) Parser Analyzer")
        self.root.geometry("1200x800")
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        
        # Create main container
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.grammar_tab = ttk.Frame(self.notebook)
        self.analysis_tab = ttk.Frame(self.notebook)
        self.visualization_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.grammar_tab, text="Grammar")
        self.notebook.add(self.analysis_tab, text="Analysis")
        self.notebook.add(self.visualization_tab, text="Visualization")
        
        self.setup_grammar_tab()
        self.setup_analysis_tab()
        self.setup_visualization_tab()
        
        # Initialize parser
        self.parser = None
        self.load_grammar()
        
    def setup_grammar_tab(self):
        # Grammar input
        grammar_frame = ttk.LabelFrame(self.grammar_tab, text="Grammar Input", padding="10")
        grammar_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.grammar_text = scrolledtext.ScrolledText(grammar_frame, height=10, width=50)
        self.grammar_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(grammar_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Load Grammar", command=self.load_grammar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Grammar", command=self.save_grammar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Validate Grammar", command=self.validate_grammar).pack(side=tk.LEFT, padx=5)
        
        # Grammar info display
        info_frame = ttk.LabelFrame(self.grammar_tab, text="Grammar Information", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=10, width=50)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def setup_analysis_tab(self):
        # Input string
        input_frame = ttk.LabelFrame(self.analysis_tab, text="Input String", padding="10")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.input_text = ttk.Entry(input_frame)
        self.input_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Analysis controls
        control_frame = ttk.Frame(self.analysis_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Analyze", command=self.analyze_string).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Step by Step", command=self.step_by_step).pack(side=tk.LEFT, padx=5)
        
        # Analysis output
        output_frame = ttk.LabelFrame(self.analysis_tab, text="Analysis Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, width=50)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    

    #########################################################
    def setup_visualization_tab(self):
        control_frame = ttk.Frame(self.visualization_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(control_frame, text="Show Parse Table", command=self.show_parse_table).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Show Error Recovery Table", command=self.show_error_recovery_table).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Show Derivation Tree", command=self.show_derivation_tree).pack(side=tk.LEFT, padx=5)

        self.visualization_frame = ttk.Frame(self.visualization_tab)
        self.visualization_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _clear_vis(self):
        """Borra cualquier widget previo de la zona de visualización."""
        for w in self.visualization_frame.winfo_children():
            w.destroy()

    def _draw_single_table(self, header, rows, title=""):
        """
        Dibuja una única tabla en matplotlib con cabecera 'header' y filas 'rows'.
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axis('off')
        # calcular anchos relativos
        col_widths = [max(len(str(h)), *(len(r[i]) for r in rows)) for i,h in enumerate(header)]
        table = ax.table(
            cellText=[header] + rows,
            colLabels=None,
            cellLoc='center',
            loc='center',
            colWidths=[w/sum(col_widths) for w in col_widths]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.5)
        if title:
            ax.set_title(title)
        canvas = FigureCanvasTkAgg(fig, master=self.visualization_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_error_recovery_table(self):
        self._clear_vis()
        header, rows = self.parser.get_error_recovery_table()
        self._draw_single_table(header, rows, title="LL(1) Error Recovery Table")

    #########################################################
    def load_grammar(self):
        try:
            with open("grammar.txt", "r") as f:
                self.grammar_text.delete(1.0, tk.END)
                self.grammar_text.insert(tk.END, f.read())
            self.parser = LLParser()
            self.update_grammar_info()
            messagebox.showinfo("Success", "Grammar loaded successfully")
        except Exception as e:
            msg = str(e).strip()
            if not msg:
                msg = "Unknown error. Please check your grammar file for empty or invalid lines."
            messagebox.showerror("Error", f"Failed to load grammar: {msg}")
            
    def save_grammar(self):
        try:
            with open("grammar.txt", "w") as f:
                f.write(self.grammar_text.get(1.0, tk.END))
            self.parser = LLParser()
            self.update_grammar_info()
            messagebox.showinfo("Success", "Grammar saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save grammar: {str(e)}")
            
    def validate_grammar(self):
        if not self.parser:
            messagebox.showerror("Error", "No grammar loaded")
            return
            
        try:
            # Check for LL(1) conditions
            conflicts = []
            for var in self.parser.variables + self.parser.start:
                for term in self.parser.terminales + ["$"]:
                    if len(self.parser.tabla[var][term]) > 1:
                        conflicts.append(f"Conflict in {var} for terminal {term}")
                        
            if conflicts:
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, "Grammar is not LL(1):\n")
                for conflict in conflicts:
                    self.info_text.insert(tk.END, f"- {conflict}\n")
                messagebox.showwarning("Warning", "Grammar is not LL(1)")
            else:
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, "Grammar is LL(1)")
                messagebox.showinfo("Success", "Grammar is LL(1)")
        except Exception as e:
            messagebox.showerror("Error", f"Validation failed: {str(e)}")
            
    def update_grammar_info(self):
        if not self.parser:
            return
            
        info = self.parser.get_grammar_info()
        self.info_text.delete(1.0, tk.END)
        
        # Display variables and terminals
        self.info_text.insert(tk.END, "Variables: " + ", ".join(info["variables"]) + "\n")
        self.info_text.insert(tk.END, "Terminals: " + ", ".join(info["terminals"]) + "\n")
        self.info_text.insert(tk.END, "Start Symbol: " + info["start"][0] + "\n\n")
        
        # Display FIRST sets
        self.info_text.insert(tk.END, "FIRST Sets:\n")
        for var in info["variables"] + info["start"]:
            self.info_text.insert(tk.END, f"{var}: {', '.join(info['first_sets'][var])}\n")
            
        # Display FOLLOW sets
        self.info_text.insert(tk.END, "\nFOLLOW Sets:\n")
        for var in info["variables"] + info["start"]:
            self.info_text.insert(tk.END, f"{var}: {', '.join(info['follow_sets'][var])}\n")
            
    def analyze_string(self):
        if not self.parser:
            messagebox.showerror("Error", "No grammar loaded")
            return
        input_string = self.input_text.get().strip()
        if not input_string:
            messagebox.showerror("Error", "Please enter an input string")
            return
        try:
            valid, steps = self.parser.analyze_string(input_string)
            self.output_text.delete(1.0, tk.END)
            if valid:
                self.output_text.insert(tk.END, "String es válido :D\n\n")
            else:
                self.output_text.insert(tk.END, "String es invalido :(!\n\n")
            # Encabezado de la tabla
            header = f"{'Stack':<30} {'Input':<40} {'Rule':<40}"
            separator = "-" * (30 + 40 + 40)
            self.output_text.insert(tk.END, header + "\n")
            self.output_text.insert(tk.END, separator + "\n")
            # Mostrar pasos
            for idx, step in enumerate(steps):
                if len(step) == 3:
                    stack, input_str, rule = step
                else:
                    stack, input_str = step
                    rule = "-"
                self.output_text.insert(
                    tk.END,
                    f"{stack:<30} {input_str:<40} {rule:<40}\n"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")

    def step_by_step(self):
        if not self.parser:
            messagebox.showerror("Error", "No grammar loaded")
            return

        s = self.input_text.get().strip()
        if not s:
            messagebox.showerror("Error", "Please enter an input string")
            return

        valid, steps = self.parser.analyze_string(s)
        self.output_text.delete(1.0, tk.END)

        for i, (stack, inp, rule) in enumerate(steps):
            self.output_text.insert(tk.END, f"Step {i+1}:\n")
            self.output_text.insert(tk.END, f"  Stack: {stack}\n")
            self.output_text.insert(tk.END, f"  Input: {inp}\n")
            if rule:
                self.output_text.insert(tk.END, f"  Rule: {rule}\n")
            self.output_text.insert(tk.END, "-"*40 + "\n")
            # pequeño delay para animar
            self.root.update()
            self.root.after(200)

        self.output_text.insert(tk.END,
            "\n" + ("Accepted" if valid else "Rejected")
        )

    def show_parse_table(self):
        if not self.parser:
            messagebox.showerror("Error", "No grammar loaded")
            return

        # limpia la zona
        for w in self.visualization_frame.winfo_children():
            w.destroy()

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axis('tight')
        ax.axis('off')

        terminals = self.parser.terminales + ["$"]
        variables = self.parser.variables + self.parser.start

        # build rows, usando '-' cuando no haya regla
        table_data = []
        for var in variables:
            row = [var]
            for term in terminals:
                prods = self.parser.tabla[var][term]
                if prods:
                    row.append("\n".join(f"{r['Izq']}→{' '.join(r['Der'])}" for r in prods))
                else:
                    row.append("-")   # <-- guión en lugar de cadena vacía
            table_data.append(row)

        # dibuja la tabla con headers
        table = ax.table(
            cellText=table_data,
            colLabels=[""] + terminals,
            cellLoc='center',
            loc='center'
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.2, 1.2)

        canvas = FigureCanvasTkAgg(fig, master=self.visualization_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


    def show_derivation_tree(self):
            # limpia la zona de visualización
            for w in self.visualization_frame.winfo_children():
                w.destroy()

            s = self.input_text.get().strip()
            if not s:
                messagebox.showerror("Error", "Please enter an input string")
                return

            valid, steps = self.parser.analyze_string(s)
            if not valid:
                messagebox.showerror("Error", "Cannot show derivation tree for invalid string")
                return

            # 1) extraemos sólo los pasos de expansión (producciones)
            expansions = [rule for _, _, rule in steps if '->' in rule]

            # 2) definimos un nodo de árbol simple
            class PNode:
                __slots__ = ("symbol","children")
                def __init__(self, symbol):
                    self.symbol = symbol
                    self.children = []

            # 3) construimos el árbol de derivación en pre-orden usando una cola
            root = PNode(self.parser.start[0])
            queue = [root]
            for prod in expansions:
                left, right = prod.split("->", 1)
                A = left.strip()
                rhs = right.strip().split()
                # buscamos el siguiente nodo no expandido con símbolo == A
                for node in queue:
                    if node.symbol == A and not node.children:
                        for sym in rhs:
                            if sym != self.parser.epsilon:
                                child = PNode(sym)
                                node.children.append(child)
                                queue.append(child)
                        break

            # 4) volcamos el PNode a un grafo de networkx
            G = nx.DiGraph()
            def add_edges(node, nid):
                for i, c in enumerate(node.children):
                    cid = f"{c.symbol}_{nid}_{i}"
                    G.add_node(cid, label=c.symbol)
                    G.add_edge(nid, cid)
                    add_edges(c, cid)

            G.add_node("root", label=root.symbol)
            add_edges(root, "root")

            # 5) dibujamos con layout tipo árbol de graphviz
            fig, ax = plt.subplots(figsize=(10, 6))
            try:
                pos = graphviz_layout(G, prog="dot", root="root")
            except Exception:
                pos = nx.nx_agraph.graphviz_layout(G, prog="dot", root="root")

            labels = nx.get_node_attributes(G, "label")
            nx.draw(
                G, pos, ax=ax, labels=labels, with_labels=True,
                node_size=1200, font_size=10, arrows=False
            )
            ax.axis("off")
            plt.margins(0.2)

            canvas = FigureCanvasTkAgg(fig, master=self.visualization_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)



if __name__ == "__main__":
    root = tk.Tk()
    app = LLParserGUI(root)
    root.mainloop() 