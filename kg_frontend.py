# import streamlit as st
# from pyvis.network import Network
# from neo4j import GraphDatabase
# import streamlit.components.v1 as components
# import tempfile

# def visualize_kg(uri, user, password, query=None):
#     driver = GraphDatabase.driver(uri, auth=(user, password))
#     net = Network(height="600px", width="100%", notebook=False)
#     added_nodes = set()

#     with driver.session() as session:
#         if query:
#             result = session.run(query)
#         else:
#             result = session.run("MATCH (a)-[r]->(b) RETURN a, r, b")

#         for record in result:
#             a, b = record['a'], record['b']
#             if a['name'] not in added_nodes:
#                 net.add_node(a['name'], label=a['name'], title=f"Type: {a['type']}<br>Rows: {a.get('row_ids', [])}")
#                 added_nodes.add(a['name'])
#             if b['name'] not in added_nodes:
#                 net.add_node(b['name'], label=b['name'], title=f"Type: {b['type']}<br>Rows: {b.get('row_ids', [])}")
#                 added_nodes.add(b['name'])
#             net.add_edge(a['name'], b['name'])

#     # Save HTML instead of show()
#     tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
#     net.save_graph(tmp_file.name)  # <-- fixed here
#     driver.close()
#     return tmp_file.name


# # Streamlit App
# st.set_page_config(page_title="KG Chat Retrieval", layout="wide")
# st.title("Knowledge Graph Query Chat")

# user_input = st.text_input("Type your query (e.g., stock symbol or entity):", "")

# if st.button("Search"):
#     if user_input.strip():
#         # Construct Cypher query dynamically
#         cypher_query = f"""
#         MATCH (a:Entity)-[:RELATED_TO]->(b:Entity)
#         WHERE a.name CONTAINS '{user_input}' OR b.name CONTAINS '{user_input}'
#         RETURN a, b
#         """
#         html_file = visualize_kg("bolt://localhost:7687", "neo4j", "test1234!", query=cypher_query)
#         # Display graph in Streamlit
#         components.html(open(html_file, 'r', encoding='utf-8').read(), height=700, width=1000)
#     else:
#         st.warning("Please type a query to search in the Knowledge Graph.")
import streamlit as st
from pyvis.network import Network
from neo4j import GraphDatabase
import streamlit.components.v1 as components
import tempfile
import pandas as pd
import ast

# Load your CSV once
df = pd.read_csv("corpus_with_entities.csv")
if df['entities'].dtype == object:
    df['entities'] = df['entities'].apply(ast.literal_eval)

def visualize_kg(uri, user, password, query=None):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    net = Network(height="600px", width="100%", notebook=False)
    added_nodes = set()
    all_row_ids = set()  # collect row IDs from all nodes

    with driver.session() as session:
        if query:
            result = session.run(query)
        else:
            result = session.run("MATCH (a)-[r]->(b) RETURN a, r, b")

        for record in result:
            a, b = record['a'], record['b']

            # Add row IDs to set
            all_row_ids.update(a.get('row_ids', []))
            all_row_ids.update(b.get('row_ids', []))

            if a['name'] not in added_nodes:
                net.add_node(a['name'], label=a['name'],
                             title=f"Type: {a['type']}<br>Rows: {a.get('row_ids', [])}")
                added_nodes.add(a['name'])
            if b['name'] not in added_nodes:
                net.add_node(b['name'], label=b['name'],
                             title=f"Type: {b['type']}<br>Rows: {b.get('row_ids', [])}")
                added_nodes.add(b['name'])

            net.add_edge(a['name'], b['name'])

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    net.save_graph(tmp_file.name)
    driver.close()
    return tmp_file.name, all_row_ids

# Streamlit App
st.set_page_config(page_title="KG Chat Retrieval + News", layout="wide")
st.title("Knowledge Graph Query Chat with Related News")

user_input = st.text_input("Type your query (e.g., stock symbol or entity):", "")

if st.button("Search"):
    if user_input.strip():
        cypher_query = f"""
        MATCH (a:Entity)-[:RELATED_TO]->(b:Entity)
        WHERE a.name CONTAINS '{user_input}' OR b.name CONTAINS '{user_input}'
        RETURN a, b
        """
        html_file, row_ids = visualize_kg("bolt://localhost:7687", "neo4j", "your password", query=cypher_query)

        # Display graph
        components.html(open(html_file, 'r', encoding='utf-8').read(), height=700, width=1000)

        # Show related rows from CSV
        if row_ids:
            related_rows = df.loc[df.index.isin(row_ids)]
            st.subheader("Related News / Rows")
            st.dataframe(related_rows)  # or select specific columns like ['news', 'sentiment']
        else:
            st.info("No related rows found for this query.")
    else:
        st.warning("Please type a query to search in the Knowledge Graph.")
