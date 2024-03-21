from flask import Flask, render_template, request
import csv
import pandas as pd
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from community import community_louvain

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        data = request.form.to_dict()
        with open('persona.csv', 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data.keys())
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow(data)
        return 'Data submitted successfully!'

@app.route('/Generate', methods=['POST'])
def generate_network_graph():
    # Load persona CSV file
    df = pd.read_csv('persona.csv')
    df['標籤'] = df['標籤'].str.replace('、', ',').str.split(',')
    
    # Create mappings
    keyword_to_ids = defaultdict(list)
    id_to_keywords = defaultdict(list)

    for index, row in df.iterrows():
        id = row['id']
        id_to_keywords[id].append
        keywords = [keyword.strip() for keyword in row['標籤']]
        for keyword in keywords:
            keyword_to_ids[keyword].append(id)

    # Load index CSV file
    dic_df = pd.read_csv("index.csv")
    key_to_index = defaultdict(list)

    for index, row in dic_df.iterrows():
        key = row['key']
        index_val = row['index']
        key_to_index[key].append(index_val)

    # Create network graph
    T = nx.Graph()

    # Add nodes
    for id in id_to_keywords:
        T.add_node(id, type='id')
    for keyword in keyword_to_ids:
        T.add_node(keyword, type='keyword')
    for index in key_to_index:
        T.add_node(index, type="index")

    # Add edges
    for keyword, ids in keyword_to_ids.items():
        for id in ids:
            T.add_edge(id, keyword)

    for key, index in key_to_index.items():
        for index in index:
            T.add_edge(index, key)

    # Apply community detection
    partition = community_louvain.best_partition(T)

    # Draw graph
    community_colors = {node: partition[node] for node in T.nodes()}
    values = [community_colors[node] for node in T.nodes()]
    node_sizes = [100 * T.degree(node) for node in T.nodes()]
    pos = nx.spring_layout(T, k=0.15, iterations=40)

    plt.figure(figsize=(30, 30))
    nx.draw_networkx_edges(T, pos, alpha=0.5)
    nx.draw_networkx_nodes(T, pos, node_color=values, node_size=node_sizes, cmap=plt.cm.jet)
    nx.draw_networkx_labels(T, pos, font_size=20, font_family='SimSun')
    plt.axis('off')
    plt.show()

if __name__ == '__main__':
    app.run(debug=True)
