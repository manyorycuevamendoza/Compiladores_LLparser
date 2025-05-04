import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout
from LL_parser import LLParser
from itertools import count

st.set_page_config(layout="wide")
st.title("LL(1) Parser Analyzer")

# ——— 1) Gramática ———
st.sidebar.header("1. Grammar")
grammar_text = st.sidebar.text_area(
    "Define your grammar here (→ or ->, one rule per line):",
    value=open("grammar.txt").read(),
    height=200
)
if st.sidebar.button("Reload Grammar"):
    with open("grammar.txt", "w") as f:
        f.write(grammar_text)
    st.sidebar.success("Grammar saved")
parser = LLParser("grammar.txt")

# ——— 2) Mostrar tablas ———
st.sidebar.header("2. Tables")
show_parse = st.sidebar.checkbox("Show Parse Table")
show_errrec = st.sidebar.checkbox("Show Error-Recovery Table")

if show_parse:
    header, rows = parser.get_parsing_table()
    df = pd.DataFrame(rows, columns=header)
    st.subheader("LL(1) Parsing Table")
    st.dataframe(df.style.set_properties(**{"text-align": "center"}), height=400)

if show_errrec:
    header, rows = parser.get_error_recovery_table()
    df2 = pd.DataFrame(rows, columns=header)
    st.subheader("LL(1) Error-Recovery Table")
    st.dataframe(df2.style.set_properties(**{"text-align": "center"}), height=400)

# ——— 3) Análisis de cadena ———
st.sidebar.header("3. Analyze String")
input_str = st.sidebar.text_input("Input tokens (space-separated):", value="id + id")
if st.sidebar.button("Analyze"):
    valid, steps = parser.analyze_string(input_str)
    st.subheader("Result")
    st.markdown(f"**Valid:** {'✅' if valid else '❌'}")
    df_steps = pd.DataFrame(steps, columns=["Stack", "Input", "Rule"])
    st.subheader("Trace")
    st.table(df_steps)
