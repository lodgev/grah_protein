import numpy as np
import pandas as pd

# Load and inspect the data file provided by the user
file_path = 'uniprotkb_AND_model_organism_9606_2025_02_07.tsv'
data = pd.read_csv(file_path, sep='\t')

# Display basic information and first few rows of the dataset
data_info = data.info()
data_head = data.head()

data_info, data_head

# Предобработка данных

# Уберем записи без данных по доменам (InterPro)
protein_data_clean = data.dropna(subset=['InterPro']).copy()

# Очистим все колонки от NaN и 'NaN', заменив их на None
for col in ['Entry', 'Entry Name', 'Protein names', 'Gene Names', 'EC number', 'InterPro']:
    protein_data_clean[col] = protein_data_clean[col].replace({np.nan: None, 'NaN': None})

# Конвертируем строки с доменами InterPro в списки для удобного дальнейшего анализа
protein_data_clean['InterPro_list'] = protein_data_clean['InterPro'].apply(lambda x: x.strip(';').split(';'))

# Оставим только нужные для дальнейших задач колонки (идентификатор, имя белка, список доменов, EC номер)
protein_data_final = protein_data_clean[['Entry', 'Entry Name', 'Protein names', 'Gene Names', 'EC number', 'InterPro_list']]

# Показать пример обработанных данных
protein_data_final.head()

import networkx as nx
from itertools import combinations
from tqdm import tqdm

# Построим новую выборку из 10 000 записей
new_sample_data = protein_data_final.head(5000).reset_index(drop=True)

# Строим граф заново
protein_graph_large = nx.Graph()

# Добавляем узлы с атрибутами
for idx, row in new_sample_data.iterrows():
    protein_graph_large.add_node(row['Entry'],
                                 entry_name=row['Entry Name'],
                                 protein_names=row['Protein names'],
                                 gene_names=row['Gene Names'],
                                 ec_number=row['EC number'],
                                 interpro_domains=set(row['InterPro_list']))

# Порог сходства
similarity_threshold = 0.3

# Рассчитаем ребра по коэффициенту Жаккара
for (u, v) in tqdm(combinations(new_sample_data['Entry'], 2),
                   total=(len(new_sample_data) * (len(new_sample_data) - 1) // 2)):
    domains_u = protein_graph_large.nodes[u]['interpro_domains']
    domains_v = protein_graph_large.nodes[v]['interpro_domains']

    intersection = len(domains_u.intersection(domains_v))
    union = len(domains_u.union(domains_v))
    jaccard_similarity = intersection / union if union else 0

    if jaccard_similarity >= similarity_threshold:
        protein_graph_large.add_edge(u, v, weight=jaccard_similarity)

# Краткая статистика по графу
graph_large_info = {
    'Количество узлов': protein_graph_large.number_of_nodes(),
    'Количество рёбер': protein_graph_large.number_of_edges()
}

graph_large_info

from neo4j import GraphDatabase
import networkx as nx

# Настройки подключения к Neo4j
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "12345678")

driver = GraphDatabase.driver(URI, auth=AUTH)

# Функция загрузки графа в Neo4j
def load_graph(tx, graph):
    # Создание узлов
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

    # Создание ребер
    for u, v, data in graph.edges(data=True):
        tx.run(
            "MATCH (a:Protein {entry: $u}), (b:Protein {entry: $v}) "
            "MERGE (a)-[r:SIMILARITY {weight: $weight}]->(b)",
            u=u, v=v, weight=data['weight']
        )

# Загрузка графа в Neo4j
with driver.session() as session:
    session.execute_write(load_graph, protein_graph_large)

driver.close()