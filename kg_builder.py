# kg_builder.py
import pandas as pd
from neo4j import GraphDatabase

class KnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_entity_node(self, tx, entity, label, row_id):
        tx.run(
            "MERGE (e:Entity {name: $entity, type: $label}) "
            "SET e.row_ids = coalesce(e.row_ids, []) + $row_id",
            entity=entity, label=label, row_id=row_id
        )

    def create_relationship(self, tx, e1, e2):
        tx.run(
            "MATCH (a:Entity {name: $e1}), (b:Entity {name: $e2}) "
            "MERGE (a)-[:RELATED_TO]->(b)",
            e1=e1, e2=e2
        )

    def build_graph(self, df):
        with self.driver.session() as session:
            for idx, row in df.iterrows():
                entities = row['entities']  # list of tuples [(ent, label), ...]
                for ent, label in entities:
                    session.write_transaction(self.create_entity_node, ent, label, idx)
                # Connect entities in the same row
                for i in range(len(entities)):
                    for j in range(i+1, len(entities)):
                        session.write_transaction(self.create_relationship, entities[i][0], entities[j][0])

if __name__ == "__main__":
    df = pd.read_csv("corpus_with_entities.csv")
    # Convert string representation of list back to list.
    import ast
    df['entities'] = df['entities'].apply(ast.literal_eval)

    kg = KnowledgeGraph("bolt://localhost:7687", "neo4j", "your password")
    kg.build_graph(df)
    kg.close()
    print("Knowledge Graph built successfully in Neo4j.")
