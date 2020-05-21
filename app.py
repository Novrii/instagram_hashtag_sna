from flask import Flask, request, jsonify, render_template
import time
import os
import json
import networkx as nx
import matplotlib.pyplot as plt

# TESTING SCRAPING SELENIUM -----------------------------------------
# options = webdriver.ChromeOptions()
# options.add_argument('--ignore-certificate-errors')
# options.add_argument('--ignore-ssl-errors')
# options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')

# driver = webdriver.Chrome(chrome_options=options)
# driver.get("https://instagram.com")
# time.sleep(3)
# driver.quit()

# Init App
app = Flask(__name__)

# Init directory
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# route Index
@app.route('/')
def index():
    dir_data = os.path.join(BASEDIR, "data")
    riwayat = []
    for folder in os.listdir(dir_data):
        riwayat.append(folder)
    
    # return jsonify(riwayat)
    return render_template('index.html', riwayat=riwayat)

# route Proses
@app.route('/proses', methods=['POST','GET'])
def proses():
    if request.method == 'POST':
        riwayat = request.form['hashtag']
        dir_relation = os.path.join(BASEDIR, "data/"+riwayat+"/relations.json")

        G_symmetric = nx.Graph()
        relations = []
        start_time = time.time()

        with open(dir_relation) as openfile: # open file relations.json
            relations = json.load(openfile)

        for edge in relations:
            G_symmetric.add_edge(edge['node1'], edge['node2'])


        pos = nx.spring_layout(G_symmetric)
        betCent = nx.betweenness_centrality(G_symmetric, normalized=True, endpoints=True)
        node_color = [20000.0 * G_symmetric.degree(v) for v in G_symmetric]
        node_size =  [v * 10000 for v in betCent.values()]
        plt.figure(figsize=(10,10))
        nx.draw_networkx(G_symmetric, pos=pos, with_labels=False,
                        node_color=node_color,
                        node_size=node_size )
        plt.title('Graph #earth', fontsize = 20)
        plt.axis('off')
        print(f"{(time.time() - start_time):.2f} seconds")
        plt.show()

        return jsonify("oke")
    else:
        return jsonify("get")

# Run Server
if __name__ == '__main__':
    app.run(debug=True)