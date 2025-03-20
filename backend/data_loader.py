import pandas as pd
import networkx as nx
from itertools import combinations
from neo4j import GraphDatabase
from tqdm import tqdm

class ProteinGraph:
    def __init__(self):
        self.graph = nx.Graph()
        self.driver = None

    def load_data(self, file_path, sample_size=100):
        # Load CSV
        data = pd.read_csv(file_path, sep='\t')
        # Preprocessing
        protein_data_clean = data.dropna(subset=['InterPro']).copy()
        protein_data_clean['InterPro_list'] = protein_data_clean['InterPro'].apply(lambda x: x.strip(';').split(';'))
        protein_data_final = protein_data_clean[['Entry', 'Entry Name', 'Protein names', 'Gene Names', 'EC number', 'InterPro_list']]
        sample_data = protein_data_final.head(sample_size).reset_index(drop=True)
        self.sample_data = sample_data
        return sample_data

    def build_graph(self, similarity_threshold=0.3):
        # Add nodes
        for idx, row in self.sample_data.iterrows():
            self.graph.add_node(row['Entry'],
                                entry_name=row['Entry Name'],
                                protein_names=row['Protein names'],
                                gene_names=row['Gene Names'],
                                ec_number=row['EC number'],
                                interpro_domains=set(row['InterPro_list']))
        # Add edges
        for (u, v) in tqdm(combinations(self.sample_data['Entry'], 2), total=(len(self.sample_data)*(len(self.sample_data)-1)//2)):
            domains_u = self.graph.nodes[u]['interpro_domains']
            domains_v = self.graph.nodes[v]['interpro_domains']
            intersection = len(domains_u.intersection(domains_v))
            union = len(domains_u.union(domains_v))
            jaccard_similarity = intersection / union if union else 0
            if jaccard_similarity >= similarity_threshold:
                self.graph.add_edge(u, v, weight=jaccard_similarity)
        return {
            'Number of nodes': self.graph.number_of_nodes(),
            'Number of edges': self.graph.number_of_edges()
        }

    def connect_neo4j(self, uri="bolt://localhost:7687", user="neo4j", password="12345678"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def upload_to_neo4j(self):
        def load_graph(tx, graph):
            # Create nodes
            for node, data in graph.nodes(data=True):
                tx.run(
                    "MERGE (p:Protein {entry: $entry}) "
                    "SET p.entry_name = $entry_name, "
                    "    p.protein_names = $protein_names, "
                    "    p.gene_names = $gene_names, "
                    "    p.ec_number = $ec_number",
                    entry=node,
                    entry_name=data['entry_name'],
                    protein_names=data['protein_names'],
                    gene_names=data['gene_names'],
                    ec_number=data['ec_number']
                )
            # Create edges
            for u, v, data in graph.edges(data=True):
                tx.run(
                    "MATCH (a:Protein {entry: $u}), (b:Protein {entry: $v}) "
                    "MERGE (a)-[r:SIMILARITY {weight: $weight}]->(b)",
                    u=u, v=v, weight=data['weight']
                )
        if self.driver:
            with self.driver.session() as session:
                session.execute_write(load_graph, self.graph)
            self.driver.close()
