from neo4j import GraphDatabase

class ProteinGraphQuery:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="12345678"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()
        
    def get_full_graph(self, limit=100):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Protein)
                OPTIONAL MATCH (p)-[r:SIMILARITY]-(n:Protein)
                RETURN p, n, r.weight
                LIMIT $limit
                """,
                limit=limit
            )
            proteins = {}
            edges = []

            for record in result:
                p = record['p']
                n = record['n']
                weight = record['r.weight']

                proteins[p['entry']] = {
                    "entry": p['entry'],
                    "name": p['entry_name']
                }
                if n:
                    proteins[n['entry']] = {
                        "entry": n['entry'],
                        "name": n['entry_name']
                    }
                    edges.append({
                        "source": p['entry'],
                        "target": n['entry'],
                        "weight": weight
                    })
            return proteins, edges

    def search_protein(self, entry_id=None, protein_name=None):
        with self.driver.session() as session:
            if entry_id and protein_name:
                query = """
                MATCH(p:Protein {entry: $entry, protein_names: $protein_name})
                OPTIONAL MATCH (p)-[:SIMILARITY]-(neighbor)
                OPTIONAL MATCH (neighbor)-[r:SIMILARITY]-(second_neighbor)
                RETURN p, 
                    COLLECT(DISTINCT neighbor) AS direct_neighbors, 
                    COLLECT(DISTINCT second_neighbor) AS second_neighbors,
                    COLLECT(DISTINCT r) AS second_edges
                """
                params = {"entry": entry_id, "protein_name": protein_name}
            elif entry_id:
                query = """
                MATCH(p:Protein {entry: $entry})
                OPTIONAL MATCH (p)-[:SIMILARITY]-(neighbor)
                OPTIONAL MATCH (neighbor)-[r:SIMILARITY]-(second_neighbor)
                RETURN p, 
                    COLLECT(DISTINCT neighbor) AS direct_neighbors, 
                    COLLECT(DISTINCT second_neighbor) AS second_neighbors,
                    COLLECT(DISTINCT r) AS second_edges
                """
                params = {"entry": entry_id}
            elif protein_name:
                query = """
                MATCH (p:Protein {protein_names: $protein_name})
                OPTIONAL MATCH (p)-[:SIMILARITY]-(neighbor)
                OPTIONAL MATCH (neighbor)-[r:SIMILARITY]-(second_neighbor)
                RETURN p, 
                    COLLECT(DISTINCT neighbor) AS direct_neighbors, 
                    COLLECT(DISTINCT second_neighbor) AS second_neighbors,
                    COLLECT(DISTINCT r) AS second_edges
                """
                params = {"protein_name": protein_name}
            else:
                return None

            result = session.run(query, **params)
            record = result.single()
            if not record:
                return None

            protein = record['p']
            direct_neighbors = record['direct_neighbors']
            second_neighbors = record['second_neighbors']
            second_edges = record['second_edges']

            # Prepare edges
            edges_list = []
            for rel in second_edges:
                if rel:
                    edges_list.append({
                        "source": rel.start_node['entry'],
                        "target": rel.end_node['entry'],
                        "weight": rel['weight']
                    })

            return {
                "protein": {
                    "entry": protein['entry'],
                    "name": protein['entry_name'],
                    "gene_names": protein['gene_names'],
                    "function": protein['ec_number']
                },
                "direct_neighbors": [{
                    "entry": n['entry'],
                    "name": n['entry_name']
                } for n in direct_neighbors if n],
                "second_neighbors": [{
                    "entry": n['entry'],
                    "name": n['entry_name']
                } for n in second_neighbors if n],
                "second_edges": edges_list
            }
            
    def get_neighbors_by_id(self, entry_id):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Protein {entry: $entry})
                OPTIONAL MATCH (p)-[r:SIMILARITY]-(neighbor)
                RETURN p, COLLECT(DISTINCT neighbor) AS neighbors, COLLECT(DISTINCT r) AS edges
                """,
                entry=entry_id
            )
            record = result.single()
            if not record:
                return None

            protein = record['p']
            neighbors = record['neighbors']
            edges = record['edges']

            edge_list = []
            for rel in edges:
                if rel:
                    edge_list.append({
                        "source": rel.start_node['entry'],
                        "target": rel.end_node['entry'],
                        "weight": rel['weight']
                    })

            return {
                "protein": {
                    "entry": protein['entry'],
                    "name": protein['entry_name']
                },
                "neighbors": [{
                    "entry": n['entry'],
                    "name": n['entry_name']
                } for n in neighbors if n],
                "edges": edge_list
            }

    def get_total_proteins(self):
        with self.driver.session() as session:
            result = session.run("MATCH (p:Protein) RETURN COUNT(p) AS TotalProteins")
            return result.single()["TotalProteins"]

    def get_labelled_unlabelled(self):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Protein)
                RETURN 
                COUNT(CASE WHEN p.ec_number IS NOT NULL THEN 1 END) AS LabelledProteins,
                COUNT(CASE WHEN p.ec_number IS NULL THEN 1 END) AS UnlabelledProteins
                """
            )
            record = result.single()
            return record["LabelledProteins"], record["UnlabelledProteins"]

    def get_isolated_proteins_count(self):
        with self.driver.session() as session:
            result = session.run(
                "MATCH (p:Protein) WHERE NOT (p)-[]-() RETURN COUNT(p) AS IsolatedProteins"
            )
            return result.single()["IsolatedProteins"]

    def get_isolated_proteins_list(self, limit=10):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Protein)
                WHERE NOT (p)-[]-()
                RETURN p.entry AS Entry, p.protein_names AS Name
                LIMIT $limit
                """, limit=limit
            )
            return result.data()

    def get_degree_distribution(self):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Protein)
                RETURN p.entry AS Entry, COUNT { (p)--() } AS Degree
                """
            )
            return result.data()
