from flask import Flask, request, jsonify, render_template
import time
import os
import json
import networkx as nx
import matplotlib.pyplot as plt
import collections

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

# Init Function
def sort_and_small_dict(d, n):
    sorted_dict = collections.OrderedDict(sorted(d.items(), key=lambda x: -x[1]))
    firstnpairs = list(sorted_dict.items())[:n]
    return firstnpairs

def centrality_to_str_arr(centrality):
    str_arr = []
    for item in centrality:
        str_arr.append(item[0] + ' | ' + str(round(item[1], 2)))
    return str_arr

# route Index
@app.route('/')
def index():
    dir_data = os.path.join(BASEDIR, "data")
    riwayat = []
    for folder in os.listdir(dir_data):
        riwayat.append(folder)
    
    # return jsonify(riwayat)
    return render_template('index.html', riwayat=riwayat, status='home')

# route Proses
@app.route('/proses', methods=['POST','GET'])
def proses():
    if request.method == 'POST':
        riwayat = request.form['hashtag']
        dir_riwayat = os.path.join(BASEDIR, "data/"+riwayat)
        
        if os.path.exists(dir_riwayat): # jika data sudah tersedia

            dir_relation = os.path.join(dir_riwayat, "relations.json")

            G_symmetric = nx.Graph()
            relations = []
            start_time = time.time()
            bet_cen = []
            deg_cen = []
            clo_cen = []
            eig_cen = []

            with open(dir_relation) as openfile: # open file relations.json
                relations = json.load(openfile)

            for edge in relations:
                G_symmetric.add_edge(edge['node1'], edge['node2'])

            # Betweenness centrality
            if not os.path.exists(dir_riwayat+"/bet_cen.json"):
                bet_cen = nx.betweenness_centrality(G_symmetric)
                bet_cen = sort_and_small_dict(bet_cen, 5)

                # Save Bet Cen
                with open(dir_riwayat+"/bet_cen.json", 'w') as outfile:
                    json.dump(bet_cen, outfile)
            else:
                with open(dir_riwayat+"/bet_cen.json") as openfile:
                    bet_cen = json.load(openfile)

            # Degree centrality
            if not os.path.exists(dir_riwayat+"/deg_cen.json"):
                deg_cen = nx.degree_centrality(G_symmetric)
                deg_cen = sort_and_small_dict(deg_cen, 5)

                # Save deg cen
                with open(dir_riwayat+"/deg_cen.json", 'w') as outfile:
                    json.dump(deg_cen, outfile)
            else:
                with open(dir_riwayat+"/deg_cen.json") as openfile:
                    deg_cen = json.load(openfile)
            
            # Closeness centrality
            if not os.path.exists(dir_riwayat+"/clo_cen.json"):
                clo_cen = nx.closeness_centrality(G_symmetric)
                clo_cen = sort_and_small_dict(clo_cen, 5)

                # Save clo cen
                with open(dir_riwayat+"/clo_cen.json", 'w') as outfile:
                    json.dump(clo_cen, outfile)
            else:
                with open(dir_riwayat+"/clo_cen.json") as openfile:
                    clo_cen = json.load(openfile)
            
            # Eigenvector centrality
            if not os.path.exists(dir_riwayat+"/eig_cen.json"):
                eig_cen = nx.eigenvector_centrality(G_symmetric)
                eig_cen = sort_and_small_dict(eig_cen, 5)

                # Save eig cen
                with open(dir_riwayat+"/eig_cen.json", 'w') as outfile:
                    json.dump(eig_cen, outfile)
            else:
                with open(dir_riwayat+"/eig_cen.json") as openfile:
                    eig_cen = json.load(openfile)
            
            # Open Add html graph
            deg_cen_html = []
            with open(dir_riwayat+"/earth_html.json") as openfile:
                deg_cen_html = json.load(openfile)

            waktu = (time.time() - start_time)

            return render_template('index.html', status='proses', bet_cen=bet_cen, deg_cen=deg_cen, clo_cen=clo_cen, eig_cen=eig_cen, deg_cen_html=deg_cen_html, waktu=f'{waktu:.2f}')
        
        else: # jika data belum tersedia, maka grab postingan
            return render_template('index.html', status='proses')
    else:
        return jsonify("get")

# Run Server
if __name__ == '__main__':
    app.run(debug=True)