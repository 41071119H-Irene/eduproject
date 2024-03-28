from flask import Flask, render_template, request, jsonify, redirect, url_for
import csv
import pandas as pd
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from community import community_louvain
import io
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        data = request.form.to_dict()
        with open('persona.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data.keys())
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow(data)
        # 返回 JSON 响应以在前端显示成功消息
        return redirect(url_for('index'))


@app.route('/get_persona_data', methods=['GET'])
def get_persona_data():
    persona_data = []
    with open('persona.csv', 'r', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            persona_data.append(row)
    print("Persona data:", persona_data)  # 在终端输出以检查数据
    return jsonify(persona_data)



@app.route('/generate_network_graph', methods=['POST'])
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
    dic_df = pd.read_csv("index2.csv")
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
    pos = nx.spring_layout(T, k=1.5, iterations=500)

    import matplotlib
    matplotlib.use('Agg')

    plt.figure(figsize=(8, 6))
    nx.draw_networkx_edges(T, pos, alpha=0.5)
    nx.draw_networkx_nodes(T, pos, node_color=values, node_size=node_sizes, cmap=plt.cm.jet)
    nx.draw_networkx_labels(T, pos, font_size=10, font_family='SimSun')
    plt.axis('off')
    
    # Save the generated graph to a file
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)
    img_base64 = base64.b64encode(img_data.getvalue()).decode('utf-8')
    
    # Return the Base64 encoded image string
    return jsonify({"graph_data": img_base64})

if __name__ == '__main__':
    app.run(debug=True)
