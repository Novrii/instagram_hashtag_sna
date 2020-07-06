from flask import Flask, request, jsonify, render_template, redirect, session, url_for, g
import time
import os
import shutil
import json
import networkx as nx
import matplotlib.pyplot as plt
import collections
import seaborn as sns
import requests
from datetime import datetime

from bokeh.io import output_file, show
from bokeh.models import HoverTool, ColumnDataSource, LinearColorMapper, BoxSelectTool, Circle,  MultiLine, NodesAndLinkedEdges, Plot, Range1d, TapTool, BoxZoomTool, ResetTool, WheelZoomTool, PanTool
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx, figure
from bokeh.embed import components

# Init User
class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

users = []
users.append(User(id=1, username='user', password='satu'))
users.append(User(id=2, username='admin', password='zero'))
users.append(User(id=3, username='Carlos', password='somethingsimple'))

# Init App
app = Flask(__name__)
app.secret_key = 'secretkeysatu'

# Init directory & time
BASEDIR = os.path.abspath(os.path.dirname(__file__))
DATE_NOW = datetime.now()

def sort_and_small_dict(d, n): # fungsi mengurutkan
    sorted_dict = collections.OrderedDict(sorted(d.items(), key=lambda x: -x[1]))
    firstnpairs = list(sorted_dict.items())[:n]
    return firstnpairs

def centrality_to_str_arr(centrality): 
    str_arr = []
    for item in centrality:
        str_arr.append(item[0] + ' <br> ' + str(round(item[1], 5))) # output : earth | 0.08 (revisi:.5)
    return str_arr

def grab_data(dir_riwayat):
    return "oke"

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user

# route login
@app.route('/', methods=['POST', 'GET']) # Login Masih Error (Cek Lagi)
def index():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['nama']
        password = request.form['sandi']

        if username == "":
            return redirect(url_for('index'))
        
        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('cari'))

        return redirect(url_for('index'))

    return render_template('login.html')

# route logout
@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect(url_for('index'))

# route Index
@app.route('/cari', methods=['POST', 'GET'])
def cari():
    if not g.user:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        riwayat = request.form['hashtag']
        # update = request.form['update']
        # jika request = hashtag, tampilkan data lama atau membuat data
        # jika request = update, update data
        if len(riwayat) != 0:
            day = DATE_NOW.day
            month = DATE_NOW.month
            year = DATE_NOW.year
            dir_riwayat = os.path.join(BASEDIR, "data/"+riwayat+"_"+str(day)+"_"+str(month)+"_"+str(year))
            start_time = time.time()
            
            count = 0 # hitung jumlah direktori berdasarkan hashtag
            dir_data = os.path.join(BASEDIR, "data")
            for x in os.listdir(dir_data):
                if riwayat in x: # jika data belum tersedia, maka grab postingan, caption, hashtag dan relation
                    dir_riwayat = os.path.join(dir_data, x)
                    count =+ 1
            if count == 0: # jika data belum tersedia, maka grab postingan, caption, hashtag dan relation
                # remove old folder
                # dir_data = os.path.join(BASEDIR, "data")
                # for x in os.listdir(dir_data):
                #     if riwayat in x:
                #         shutil.rmtree(os.path.join(dir_data, x))
                #         print(riwayat,"dihapus")
                os.mkdir(dir_riwayat) # create dir riwayat
                # Grab Posts
                arr = []
                
                end_cursor = '' # penanda halaman
                tag = riwayat # tag yg mau dicari
                page_count = 9 # jumlah halaman (1 halaman kurang lebih 60 posts)

                try:
                    for i in range(0, page_count):
                        url = "https://www.instagram.com/explore/tags/{0}/?__a=1&max_id={1}".format(tag, end_cursor)
                        r = requests.get(url)
                        data = json.loads(r.text)
                        
                        end_cursor = data['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor'] # value for the next page
                        edges = data['graphql']['hashtag']['edge_hashtag_to_media']['edges'] # list with posts
                        
                        for item in edges:
                            arr.append(item['node'])
                            print(item['node'])

                        time.sleep(2) # insurence to not reach a time limit
                except:
                    return jsonify("Error - Grap Posts")
                    
                print("End cursor:",end_cursor) # save this to restart parsing with the next page

                with open(dir_riwayat+'/posts.json', 'w') as outfile:
                    json.dump(arr, outfile) # save to json
                
                # Grab captions
                captions = []
                for item in arr:
                    shortcode = item['shortcode']
                    display = item['display_url']
                    caption = item['edge_media_to_caption']['edges']
                    # print(len(caption))
                    try:
                        if len(caption) != 0:
                            text = item['edge_media_to_caption']['edges'][0]['node']['text']
                            # print(text)
                            captions.append({
                                'shortcode' : shortcode,
                                'caption' : text,
                                'display' : display
                            })
                    except:
                        print(len(caption))
                    
                with open(dir_riwayat+'/captions.json', 'w', encoding='utf-8') as outfile:
                    json.dump(captions, outfile, ensure_ascii=False) # save to json
                
                # Grab Hashtag
                hashtag = []

                for item in captions:
                    shortcode = item['shortcode']
                    caption = item['caption']
                    hashtags = []
                    display = item['display'] # url gambar
                    
                    for tag in caption.split():
                        if tag.startswith("#"):
                            tag_cek = tag.strip("#").split("#")
                            if len(tag_cek) > 0: # cek jika hashtag tidak pakai spasi
                                for tag_tag in tag_cek:
                                    # menghilangkan tag, emoji dan bahasa selain latin (HANYA BAHASA LATIN)
                                    save_tag = (tag_tag.strip("#").encode('ascii', 'ignore')).decode('utf-8')
                                    if len(save_tag) is not 0:
                                        hashtags.append(save_tag)
                            else:
                                save_tag = (tag.strip("#").encode('ascii', 'ignore')).decode('utf-8')
                                if len(save_tag) is not 0:
                                    hashtags.append(save_tag)
                    
                    # hashtags = [tag.strip("#") for tag in caption.split() if tag.startswith("#")]
                    if len(hashtags) is not 0: # jika ada hashtags kosong, maka tidak disimpan
                        hashtag.append({
                            'shortcode' : shortcode,
                            'hashtag' :  hashtags,
                            'display' : display
                        })

                with open(dir_riwayat+'/hashtags.json', 'w') as outfile: # encoding utf-8 utk izin simpan karakter selain latin
                    json.dump(hashtag, outfile)
                
                # Grab Relations
                relations = []

                count = 0
                for idx_arr, post in enumerate(hashtag):
                    tags = post['hashtag']
                    if len(tags) is not 0:
                        for idx_tag, tag in enumerate(tags):
                            for jdx_tag, jtag in enumerate(tags):
                                batas = jdx_tag + idx_tag + 1
                                if batas <= len(tags)-1: # looping sampai akhir, tapi tidak lewat batas
                                    i = tags[idx_tag]
                                    j = tags[jdx_tag+idx_tag+1]
                                    relations.append({
                                        "node1" : i,
                                        "node2" : j
                                    })

                with open(dir_riwayat+'/relations.json', 'w') as outfile:
                    json.dump(relations, outfile)

                waktu = (time.time() - start_time) # Hitung waktu proses

                return jsonify(f"Info - Data Tersedia {len(hashtag)} hashtag - {waktu:.2f} s")

            dir_relation = os.path.join(dir_riwayat, "relations.json")

            tag_html = []
            bet_cen = []
            bet_cen_html = []
            deg_cen = []
            deg_cen_html = []
            clo_cen = []
            clo_cen_html = []
            eig_cen = []
            eig_cen_html = []

            G_count = nx.Graph()
            relations_c = []

            with open(dir_relation) as openfile:
                relations_c = json.load(openfile)
            
            for edge in relations_c:
                G_count.add_edge(edge['node1'], edge['node2'])

            n_nodes = len(G_count)
            n_edges = G_count.number_of_edges()

            # Visual Graph of Tag
            if not os.path.exists(dir_riwayat+"/tag_html.json"):
                G_symmetric = nx.Graph()
                G_temp = nx.Graph() # temporary graph utk mengurangi node yg kurang dari 100
                relations = []

                with open(dir_relation) as openfile:
                    relations = json.load(openfile)
                
                for edge in relations:
                    G_symmetric.add_edge(edge['node1'], edge['node2'])
                    G_temp.add_edge(edge['node1'], edge['node2'])

                for i in G_temp.degree():
                    if i[1] < 100:
                        G_symmetric.remove_node(i[0])
                
                # set attr size and color
                node_size = {k:v/5 for k, v in G_symmetric.degree()}
                node_color = {k:v/5 for k, v in G_symmetric.degree()}

                # Set node attribute
                nx.set_node_attributes(G_symmetric, node_color, 'node_color')
                nx.set_node_attributes(G_symmetric, node_size, 'node_size')

                # Map cubehelix_palette (Untuk Warna)
                palette = sns.cubehelix_palette(21)
                pal_hex_lst = palette.as_hex()

                mapper = LinearColorMapper(palette=pal_hex_lst, low=0, high=21)

                # Init Plot
                plot = Plot(x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))
                plot.title.text = "Graph Relations Hashtag"

                plot.add_tools(HoverTool(tooltips=[("index", "@index")]), TapTool(), BoxSelectTool(), ResetTool(), BoxZoomTool(), WheelZoomTool(), PanTool())

                # Graph render
                graph = from_networkx(G_symmetric, nx.spring_layout, scale=1, center=(0,0))

                graph.node_renderer.glyph = Circle(size='node_size', fill_color={'field': 'node_color', 'transform': mapper})

                graph.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
                graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=1)
                graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=1)

                graph.selection_policy = NodesAndLinkedEdges()

                plot.renderers.append(graph)

                # Save and get div and script
                script, div = components(plot) 
                tag_html.append({
                    'div' : div,
                    'script' : script
                })
                with open(dir_riwayat+'/tag_html.json', 'w') as outfile:
                    json.dump(tag_html, outfile) # save html part Graph
            else:
                with open(dir_riwayat+'/tag_html.json') as openfile:
                    tag_html = json.load(openfile)

            # Betweenness centrality
            if not os.path.exists(dir_riwayat+"/bet_cen.json") or not os.path.exists(dir_riwayat+"/bet_cen_html.json"):
                G_symmetric = nx.Graph()
                relations = []

                with open(dir_relation) as openfile: # open file relations.json
                    relations = json.load(openfile)

                for edge in relations:
                    G_symmetric.add_edge(edge['node1'], edge['node2'])

                bet_cen = nx.betweenness_centrality(G_symmetric)

                # Set node size and color
                node_size = {k:100*v for k, v in bet_cen.items()}
                node_color = {k:15*v for k, v in bet_cen.items()}

                # bet_cen_sort = sort_and_small_dict(bet_cen, 5)
                for i in bet_cen.items():
                    if i[1] < 0.01: # menghapus node yg skornya kurang dari 0.1
                        G_symmetric.remove_node(i[0])

                # Set node attribute
                nx.set_node_attributes(G_symmetric, node_color, 'node_color')
                nx.set_node_attributes(G_symmetric, node_size, 'node_size')

                # Map cubehelix_palette (Untuk Warna)
                palette = sns.cubehelix_palette(21)
                pal_hex_lst = palette.as_hex()

                mapper = LinearColorMapper(palette=pal_hex_lst, low=0, high=21)

                # Init Plot
                plot = Plot(x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))
                plot.title.text = "Graph Betweenness Centrality"

                plot.add_tools(HoverTool(tooltips=[("index", "@index")]), TapTool(), BoxSelectTool(), ResetTool(), BoxZoomTool(), WheelZoomTool(), PanTool())

                # Graph render
                graph = from_networkx(G_symmetric, nx.spring_layout, scale=1, center=(0,0))

                graph.node_renderer.glyph = Circle(size='node_size', fill_color={'field': 'node_color', 'transform': mapper})

                graph.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
                graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=1)
                graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=1)

                graph.selection_policy = NodesAndLinkedEdges()

                plot.renderers.append(graph)

                # Save and get div and script
                script, div = components(plot) 
                bet_cen_html.append({
                    'div' : div,
                    'script' : script
                })
                with open(dir_riwayat+'/bet_cen_html.json', 'w') as outfile:
                    json.dump(bet_cen_html, outfile) # save html part Graph
                
                bet_cen = sort_and_small_dict(bet_cen, 100) # filter 100 terbesar
                with open(dir_riwayat+"/bet_cen.json", 'w') as outfile:
                    json.dump(bet_cen, outfile) # Save Bet Cen tabel
            else:
                with open(dir_riwayat+"/bet_cen_html.json") as openfile:
                    bet_cen_html = json.load(openfile) # load data json Graph
                with open(dir_riwayat+"/bet_cen.json") as openfile:
                    bet_cen = json.load(openfile) # load data json Tabel

            # Degree centrality
            if not os.path.exists(dir_riwayat+"/deg_cen.json") or not os.path.exists(dir_riwayat+"/deg_cen_html.json"):
                G_symmetric = nx.Graph()
                relations = []

                with open(dir_relation) as openfile: # open file relations.json
                    relations = json.load(openfile)

                for edge in relations:
                    G_symmetric.add_edge(edge['node1'], edge['node2'])

                deg_cen = nx.degree_centrality(G_symmetric)

                # Membuat graph 
                # Set node size and color
                node_size = {k:100*v for k, v in deg_cen.items()}
                node_color = {k:15*v for k, v in deg_cen.items()}

                for i in deg_cen.items():
                    if i[1] < 0.1: # menghapus node yg skornya kurang dari 0.1
                        G_symmetric.remove_node(i[0])

                # Set node attribute
                nx.set_node_attributes(G_symmetric, node_color, 'node_color')
                nx.set_node_attributes(G_symmetric, node_size, 'node_size')

                # Map cubehelix_palette (Untuk Warna)
                palette = sns.cubehelix_palette(21)
                pal_hex_lst = palette.as_hex()

                mapper = LinearColorMapper(palette=pal_hex_lst, low=0, high=21)

                # Init Plot
                plot = Plot(x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))
                plot.title.text = "Graph Degree Centrality"

                plot.add_tools(HoverTool(tooltips=[("index", "@index")]), TapTool(), BoxSelectTool(), ResetTool(), BoxZoomTool(), WheelZoomTool(), PanTool())

                # Graph render
                graph = from_networkx(G_symmetric, nx.spring_layout, scale=1, center=(0,0))

                graph.node_renderer.glyph = Circle(size='node_size', fill_color={'field': 'node_color', 'transform': mapper})

                graph.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
                graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=1)
                graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=1)

                graph.selection_policy = NodesAndLinkedEdges()

                plot.renderers.append(graph)

                # Save and get div and script
                script, div = components(plot) 
                deg_cen_html.append({
                    'div' : div,
                    'script' : script
                })
                with open(dir_riwayat+'/deg_cen_html.json', 'w') as outfile:
                    json.dump(deg_cen_html, outfile) # save html part Graph
                
                deg_cen = sort_and_small_dict(deg_cen, 100) # sort hasil jadi 100 besar utl tabel
                with open(dir_riwayat+"/deg_cen.json", 'w') as outfile:
                    json.dump(deg_cen, outfile) # Save deg cen tabel
            else: # Jika sudah tersedia
                with open(dir_riwayat+"/deg_cen_html.json") as openfile:
                    deg_cen_html = json.load(openfile) # load data json Graph
                with open(dir_riwayat+"/deg_cen.json") as openfile:
                    deg_cen = json.load(openfile) # load data json tabel
            
            # Closeness centrality
            if not os.path.exists(dir_riwayat+"/clo_cen.json") or not os.path.exists(dir_riwayat+"/clo_cen_html.json"):
                G_symmetric = nx.Graph()
                relations = []

                with open(dir_relation) as openfile: # open file relations.json
                    relations = json.load(openfile)

                for edge in relations:
                    G_symmetric.add_edge(edge['node1'], edge['node2'])

                clo_cen = nx.closeness_centrality(G_symmetric)
                
                # Set node size and color
                node_size = {k:100*v for k, v in clo_cen.items()}
                node_color = {k:15*v for k, v in clo_cen.items()}

                clo_cen_sort = sort_and_small_dict(clo_cen, 5)
                for i in clo_cen.items():
                    if i[1] < clo_cen_sort[4][1]: # menghapus node yg skornya kurang dari 0.1
                        G_symmetric.remove_node(i[0])

                # Set node attribute
                nx.set_node_attributes(G_symmetric, node_color, 'node_color')
                nx.set_node_attributes(G_symmetric, node_size, 'node_size')

                # Map cubehelix_palette (Untuk Warna)
                palette = sns.cubehelix_palette(21)
                pal_hex_lst = palette.as_hex()

                mapper = LinearColorMapper(palette=pal_hex_lst, low=0, high=21)

                # Init Plot
                plot = Plot(x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))
                plot.title.text = "Graph Closeness Centrality"

                plot.add_tools(HoverTool(tooltips=[("index", "@index")]), TapTool(), BoxSelectTool(), ResetTool(), BoxZoomTool(), WheelZoomTool(), PanTool())

                # Graph render
                graph = from_networkx(G_symmetric, nx.spring_layout, scale=1, center=(0,0))

                graph.node_renderer.glyph = Circle(size='node_size', fill_color={'field': 'node_color', 'transform': mapper})

                graph.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
                graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=1)
                graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=1)

                graph.selection_policy = NodesAndLinkedEdges()

                plot.renderers.append(graph)

                # Save and get div and script
                script, div = components(plot) 
                clo_cen_html.append({
                    'div' : div,
                    'script' : script
                })
                with open(dir_riwayat+'/clo_cen_html.json', 'w') as outfile:
                    json.dump(clo_cen_html, outfile) # save html part Graph
                
                clo_cen = sort_and_small_dict(clo_cen, 100) # filter 100 besar
                with open(dir_riwayat+"/clo_cen.json", 'w') as outfile:
                    json.dump(clo_cen, outfile) # Save clo cen tabel
            else:
                with open(dir_riwayat+"/clo_cen_html.json") as openfile:
                    clo_cen_html = json.load(openfile) # save data json graph
                with open(dir_riwayat+"/clo_cen.json") as openfile:
                    clo_cen = json.load(openfile) # save data tabel
            
            # Eigenvector centrality
            if not os.path.exists(dir_riwayat+"/eig_cen.json") or not os.path.exists(dir_riwayat+"/eig_cen_html.json"):
                G_symmetric = nx.Graph()
                relations = []

                with open(dir_relation) as openfile: # open file relations.json
                    relations = json.load(openfile)

                for edge in relations:
                    G_symmetric.add_edge(edge['node1'], edge['node2'])
                    
                eig_cen = nx.eigenvector_centrality(G_symmetric)
                
                # Set node size and color
                node_size = {k:100*v for k, v in eig_cen.items()}
                node_color = {k:15*v for k, v in eig_cen.items()}

                for i in eig_cen.items():
                    if i[1] < 0.1: # menghapus node yg skornya kurang dari 0.1
                        G_symmetric.remove_node(i[0])

                # Set node attribute
                nx.set_node_attributes(G_symmetric, node_color, 'node_color')
                nx.set_node_attributes(G_symmetric, node_size, 'node_size')

                # Map cubehelix_palette (Untuk Warna)
                palette = sns.cubehelix_palette(21)
                pal_hex_lst = palette.as_hex()

                mapper = LinearColorMapper(palette=pal_hex_lst, low=0, high=21)

                # Init Plot
                plot = Plot(x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))
                plot.title.text = "Graph Eigenvector Centrality"

                plot.add_tools(HoverTool(tooltips=[("index", "@index")]), TapTool(), BoxSelectTool(), ResetTool(), BoxZoomTool(), WheelZoomTool(), PanTool())

                # Graph render
                graph = from_networkx(G_symmetric, nx.spring_layout, scale=1, center=(0,0))

                graph.node_renderer.glyph = Circle(size='node_size', fill_color={'field': 'node_color', 'transform': mapper})

                graph.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
                graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=1)
                graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=1)

                graph.selection_policy = NodesAndLinkedEdges()

                plot.renderers.append(graph)

                # Save and get div and script
                script, div = components(plot) 
                eig_cen_html.append({
                    'div' : div,
                    'script' : script
                })
                with open(dir_riwayat+'/eig_cen_html.json', 'w') as outfile:
                    json.dump(eig_cen_html, outfile) # save html part Graph
                
                eig_cen = sort_and_small_dict(eig_cen, 100) # filter 100 besar
                with open(dir_riwayat+"/eig_cen.json", 'w') as outfile:
                    json.dump(eig_cen, outfile) # Save eig cen
            else:
                with open(dir_riwayat+"/eig_cen_html.json") as openfile:
                    eig_cen_html = json.load(openfile) # save data graph
                with open(dir_riwayat+"/eig_cen.json") as openfile:
                    eig_cen = json.load(openfile) # save data tabel

            deg_cen = centrality_to_str_arr(deg_cen)
            clo_cen = centrality_to_str_arr(clo_cen)
            bet_cen = centrality_to_str_arr(bet_cen)
            eig_cen = centrality_to_str_arr(eig_cen)

            # show raw data
            raw_data = []
            with open(dir_riwayat+"/hashtags.json") as openfile:
                raw_data = json.load(openfile)
            
            waktu = (time.time() - start_time) # Hitung waktu proses
            waktu_filter = divmod(waktu, 60)
            menit = waktu_filter[0]
            detik = waktu_filter[1]

            cut_date = os.path.basename(dir_riwayat).split("_")
            day = cut_date[1]
            month = cut_date[2]
            year = cut_date[3]

            return render_template('index.html', status='proses', tag=riwayat+"_"+str(day)+"/"+str(month)+"/"+str(year), n_nodes=f'{n_nodes:,d}', n_edges=f'{n_edges:,d}', raw_data=raw_data, tag_html=tag_html, bet_cen=bet_cen, deg_cen=deg_cen, clo_cen=clo_cen, eig_cen=eig_cen, deg_cen_html=deg_cen_html, bet_cen_html=bet_cen_html, clo_cen_html=clo_cen_html, eig_cen_html=eig_cen_html, menit=f'{menit:.0f}', detik=f'{detik:.2f}')
        else:
            return jsonify("Isian Kosong")

    dir_data = os.path.join(BASEDIR, "data")
    riwayat = []
    for folder in os.listdir(dir_data):
        x = folder.split("_")
        riwayat.append(x[0])
    
    # return jsonify(riwayat)
    return render_template('index.html', riwayat=riwayat, status='home')

# route Proses
@app.route('/proses', methods=['POST','GET'])
def proses():
    if not g.user:
        return redirect(url_for('index'))

    if request.method == 'POST':
        riwayat = request.form['hashtag']
        # update = request.form['update']
        # jika request = hashtag, tampilkan data lama atau membuat data
        # jika request = update, update data
        if len(riwayat) != 0:
            day = DATE_NOW.day
            month = DATE_NOW.month
            year = DATE_NOW.year
            dir_riwayat = os.path.join(BASEDIR, "data/"+riwayat+"_"+str(day)+"_"+str(month)+"_"+str(year))
            start_time = time.time()
            
            # count = 0 # hitung jumlah direktori berdasarkan hashtag
            # dir_data = os.path.join(BASEDIR, "data")
            # for x in os.listdir(dir_data):
            #     if riwayat in x: # jika data belum tersedia, maka grab postingan, caption, hashtag dan relation
            #         dir_riwayat = os.path.join(dir_data, x)
            #         count =+ 1
            if not os.path.exists(dir_riwayat): # jika data belum tersedia, maka grab postingan, caption, hashtag dan relation
                # remove old folder
                dir_data = os.path.join(BASEDIR, "data")
                for x in os.listdir(dir_data):
                    if riwayat in x:
                        shutil.rmtree(os.path.join(dir_data, x))
                        print(riwayat,"dihapus")
                os.mkdir(dir_riwayat) # create dir riwayat
                # Grab Posts
                arr = []
                
                end_cursor = '' # penanda halaman
                tag = riwayat # tag yg mau dicari
                page_count = 9 # jumlah halaman (1 halaman kurang lebih 60 posts)

                try:
                    for i in range(0, page_count):
                        url = "https://www.instagram.com/explore/tags/{0}/?__a=1&max_id={1}".format(tag, end_cursor)
                        r = requests.get(url)
                        data = json.loads(r.text)
                        
                        end_cursor = data['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor'] # value for the next page
                        edges = data['graphql']['hashtag']['edge_hashtag_to_media']['edges'] # list with posts
                        
                        for item in edges:
                            arr.append(item['node'])
                            print(item['node'])

                        time.sleep(2) # insurence to not reach a time limit
                except:
                    return jsonify("Error - Grap Posts")
                    
                print("End cursor:",end_cursor) # save this to restart parsing with the next page

                with open(dir_riwayat+'/posts.json', 'w') as outfile:
                    json.dump(arr, outfile) # save to json
                
                # Grab captions
                captions = []
                for item in arr:
                    shortcode = item['shortcode']
                    display = item['display_url']
                    caption = item['edge_media_to_caption']['edges']
                    # print(len(caption))
                    try:
                        if len(caption) != 0:
                            text = item['edge_media_to_caption']['edges'][0]['node']['text']
                            # print(text)
                            captions.append({
                                'shortcode' : shortcode,
                                'caption' : text,
                                'display' : display
                            })
                    except:
                        print(len(caption))
                    
                with open(dir_riwayat+'/captions.json', 'w', encoding='utf-8') as outfile:
                    json.dump(captions, outfile, ensure_ascii=False) # save to json
                
                # Grab Hashtag
                hashtag = []

                for item in captions:
                    shortcode = item['shortcode']
                    caption = item['caption']
                    hashtags = []
                    display = item['display'] # url gambar
                    
                    for tag in caption.split():
                        if tag.startswith("#"):
                            tag_cek = tag.strip("#").split("#")
                            if len(tag_cek) > 0: # cek jika hashtag tidak pakai spasi
                                for tag_tag in tag_cek:
                                    # menghilangkan tag, emoji dan bahasa selain latin (HANYA BAHASA LATIN)
                                    save_tag = (tag_tag.strip("#").encode('ascii', 'ignore')).decode('utf-8')
                                    if len(save_tag) is not 0:
                                        hashtags.append(save_tag)
                            else:
                                save_tag = (tag.strip("#").encode('ascii', 'ignore')).decode('utf-8')
                                if len(save_tag) is not 0:
                                    hashtags.append(save_tag)
                    
                    # hashtags = [tag.strip("#") for tag in caption.split() if tag.startswith("#")]
                    if len(hashtags) is not 0: # jika ada hashtags kosong, maka tidak disimpan
                        hashtag.append({
                            'shortcode' : shortcode,
                            'hashtag' :  hashtags,
                            'display' : display
                        })

                with open(dir_riwayat+'/hashtags.json', 'w') as outfile: # encoding utf-8 utk izin simpan karakter selain latin
                    json.dump(hashtag, outfile)
                
                # Grab Relations
                relations = []

                count = 0
                for idx_arr, post in enumerate(hashtag):
                    tags = post['hashtag']
                    if len(tags) is not 0:
                        for idx_tag, tag in enumerate(tags):
                            for jdx_tag, jtag in enumerate(tags):
                                batas = jdx_tag + idx_tag + 1
                                if batas <= len(tags)-1: # looping sampai akhir, tapi tidak lewat batas
                                    i = tags[idx_tag]
                                    j = tags[jdx_tag+idx_tag+1]
                                    relations.append({
                                        "node1" : i,
                                        "node2" : j
                                    })

                with open(dir_riwayat+'/relations.json', 'w') as outfile:
                    json.dump(relations, outfile)

                waktu = (time.time() - start_time) # Hitung waktu proses

                # return jsonify(f"Info - Data Tersedia {len(hashtag)} hashtag - {waktu:.2f} s")

            dir_relation = os.path.join(dir_riwayat, "relations.json")

            tag_html = []
            bet_cen = []
            bet_cen_html = []
            deg_cen = []
            deg_cen_html = []
            clo_cen = []
            clo_cen_html = []
            eig_cen = []
            eig_cen_html = []

            G_count = nx.Graph()
            relations_c = []

            with open(dir_relation) as openfile:
                relations_c = json.load(openfile)
            
            for edge in relations_c:
                G_count.add_edge(edge['node1'], edge['node2'])

            n_nodes = len(G_count)
            n_edges = G_count.number_of_edges()

            # Visual Graph of Tag
            if not os.path.exists(dir_riwayat+"/tag_html.json"):
                G_symmetric = nx.Graph()
                G_temp = nx.Graph() # temporary graph utk mengurangi node yg kurang dari 100
                relations = []

                with open(dir_relation) as openfile:
                    relations = json.load(openfile)
                
                for edge in relations:
                    G_symmetric.add_edge(edge['node1'], edge['node2'])
                    G_temp.add_edge(edge['node1'], edge['node2'])

                for i in G_temp.degree():
                    if i[1] < 100:
                        G_symmetric.remove_node(i[0])
                
                # set attr size and color
                node_size = {k:v/5 for k, v in G_symmetric.degree()}
                node_color = {k:v/5 for k, v in G_symmetric.degree()}

                # Set node attribute
                nx.set_node_attributes(G_symmetric, node_color, 'node_color')
                nx.set_node_attributes(G_symmetric, node_size, 'node_size')

                # Map cubehelix_palette (Untuk Warna)
                palette = sns.cubehelix_palette(21)
                pal_hex_lst = palette.as_hex()

                mapper = LinearColorMapper(palette=pal_hex_lst, low=0, high=21)

                # Init Plot
                plot = Plot(x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))
                plot.title.text = "Graph Relations Hashtag"

                plot.add_tools(HoverTool(tooltips=[("index", "@index")]), TapTool(), BoxSelectTool(), ResetTool(), BoxZoomTool(), WheelZoomTool(), PanTool())

                # Graph render
                graph = from_networkx(G_symmetric, nx.spring_layout, scale=1, center=(0,0))

                graph.node_renderer.glyph = Circle(size='node_size', fill_color={'field': 'node_color', 'transform': mapper})

                graph.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
                graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=1)
                graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=1)

                graph.selection_policy = NodesAndLinkedEdges()

                plot.renderers.append(graph)

                # Save and get div and script
                script, div = components(plot) 
                tag_html.append({
                    'div' : div,
                    'script' : script
                })
                with open(dir_riwayat+'/tag_html.json', 'w') as outfile:
                    json.dump(tag_html, outfile) # save html part Graph
            else:
                with open(dir_riwayat+'/tag_html.json') as openfile:
                    tag_html = json.load(openfile)

            # Betweenness centrality
            if not os.path.exists(dir_riwayat+"/bet_cen.json") or not os.path.exists(dir_riwayat+"/bet_cen_html.json"):
                G_symmetric = nx.Graph()
                relations = []

                with open(dir_relation) as openfile: # open file relations.json
                    relations = json.load(openfile)

                for edge in relations:
                    G_symmetric.add_edge(edge['node1'], edge['node2'])

                bet_cen = nx.betweenness_centrality(G_symmetric)

                # Set node size and color
                node_size = {k:100*v for k, v in bet_cen.items()}
                node_color = {k:15*v for k, v in bet_cen.items()}

                # bet_cen_sort = sort_and_small_dict(bet_cen, 5)
                for i in bet_cen.items():
                    if i[1] < 0.01: # menghapus node yg skornya kurang dari 0.1
                        G_symmetric.remove_node(i[0])

                # Set node attribute
                nx.set_node_attributes(G_symmetric, node_color, 'node_color')
                nx.set_node_attributes(G_symmetric, node_size, 'node_size')

                # Map cubehelix_palette (Untuk Warna)
                palette = sns.cubehelix_palette(21)
                pal_hex_lst = palette.as_hex()

                mapper = LinearColorMapper(palette=pal_hex_lst, low=0, high=21)

                # Init Plot
                plot = Plot(x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))
                plot.title.text = "Graph Betweenness Centrality"

                plot.add_tools(HoverTool(tooltips=[("index", "@index")]), TapTool(), BoxSelectTool(), ResetTool(), BoxZoomTool(), WheelZoomTool(), PanTool())

                # Graph render
                graph = from_networkx(G_symmetric, nx.spring_layout, scale=1, center=(0,0))

                graph.node_renderer.glyph = Circle(size='node_size', fill_color={'field': 'node_color', 'transform': mapper})

                graph.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
                graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=1)
                graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=1)

                graph.selection_policy = NodesAndLinkedEdges()

                plot.renderers.append(graph)

                # Save and get div and script
                script, div = components(plot) 
                bet_cen_html.append({
                    'div' : div,
                    'script' : script
                })
                with open(dir_riwayat+'/bet_cen_html.json', 'w') as outfile:
                    json.dump(bet_cen_html, outfile) # save html part Graph
                
                bet_cen = sort_and_small_dict(bet_cen, 100) # filter 100 terbesar
                with open(dir_riwayat+"/bet_cen.json", 'w') as outfile:
                    json.dump(bet_cen, outfile) # Save Bet Cen tabel
            else:
                with open(dir_riwayat+"/bet_cen_html.json") as openfile:
                    bet_cen_html = json.load(openfile) # load data json Graph
                with open(dir_riwayat+"/bet_cen.json") as openfile:
                    bet_cen = json.load(openfile) # load data json Tabel

            # Degree centrality
            if not os.path.exists(dir_riwayat+"/deg_cen.json") or not os.path.exists(dir_riwayat+"/deg_cen_html.json"):
                G_symmetric = nx.Graph()
                relations = []

                with open(dir_relation) as openfile: # open file relations.json
                    relations = json.load(openfile)

                for edge in relations:
                    G_symmetric.add_edge(edge['node1'], edge['node2'])

                deg_cen = nx.degree_centrality(G_symmetric)

                # Membuat graph 
                # Set node size and color
                node_size = {k:100*v for k, v in deg_cen.items()}
                node_color = {k:15*v for k, v in deg_cen.items()}

                for i in deg_cen.items():
                    if i[1] < 0.1: # menghapus node yg skornya kurang dari 0.1
                        G_symmetric.remove_node(i[0])

                # Set node attribute
                nx.set_node_attributes(G_symmetric, node_color, 'node_color')
                nx.set_node_attributes(G_symmetric, node_size, 'node_size')

                # Map cubehelix_palette (Untuk Warna)
                palette = sns.cubehelix_palette(21)
                pal_hex_lst = palette.as_hex()

                mapper = LinearColorMapper(palette=pal_hex_lst, low=0, high=21)

                # Init Plot
                plot = Plot(x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))
                plot.title.text = "Graph Degree Centrality"

                plot.add_tools(HoverTool(tooltips=[("index", "@index")]), TapTool(), BoxSelectTool(), ResetTool(), BoxZoomTool(), WheelZoomTool(), PanTool())

                # Graph render
                graph = from_networkx(G_symmetric, nx.spring_layout, scale=1, center=(0,0))

                graph.node_renderer.glyph = Circle(size='node_size', fill_color={'field': 'node_color', 'transform': mapper})

                graph.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
                graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=1)
                graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=1)

                graph.selection_policy = NodesAndLinkedEdges()

                plot.renderers.append(graph)

                # Save and get div and script
                script, div = components(plot) 
                deg_cen_html.append({
                    'div' : div,
                    'script' : script
                })
                with open(dir_riwayat+'/deg_cen_html.json', 'w') as outfile:
                    json.dump(deg_cen_html, outfile) # save html part Graph
                
                deg_cen = sort_and_small_dict(deg_cen, 100) # sort hasil jadi 100 besar utl tabel
                with open(dir_riwayat+"/deg_cen.json", 'w') as outfile:
                    json.dump(deg_cen, outfile) # Save deg cen tabel
            else: # Jika sudah tersedia
                with open(dir_riwayat+"/deg_cen_html.json") as openfile:
                    deg_cen_html = json.load(openfile) # load data json Graph
                with open(dir_riwayat+"/deg_cen.json") as openfile:
                    deg_cen = json.load(openfile) # load data json tabel
            
            # Closeness centrality
            if not os.path.exists(dir_riwayat+"/clo_cen.json") or not os.path.exists(dir_riwayat+"/clo_cen_html.json"):
                G_symmetric = nx.Graph()
                relations = []

                with open(dir_relation) as openfile: # open file relations.json
                    relations = json.load(openfile)

                for edge in relations:
                    G_symmetric.add_edge(edge['node1'], edge['node2'])

                clo_cen = nx.closeness_centrality(G_symmetric)
                
                # Set node size and color
                node_size = {k:100*v for k, v in clo_cen.items()}
                node_color = {k:15*v for k, v in clo_cen.items()}

                clo_cen_sort = sort_and_small_dict(clo_cen, 5)
                for i in clo_cen.items():
                    if i[1] < clo_cen_sort[4][1]: # menghapus node yg skornya kurang dari 0.1
                        G_symmetric.remove_node(i[0])

                # Set node attribute
                nx.set_node_attributes(G_symmetric, node_color, 'node_color')
                nx.set_node_attributes(G_symmetric, node_size, 'node_size')

                # Map cubehelix_palette (Untuk Warna)
                palette = sns.cubehelix_palette(21)
                pal_hex_lst = palette.as_hex()

                mapper = LinearColorMapper(palette=pal_hex_lst, low=0, high=21)

                # Init Plot
                plot = Plot(x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))
                plot.title.text = "Graph Closeness Centrality"

                plot.add_tools(HoverTool(tooltips=[("index", "@index")]), TapTool(), BoxSelectTool(), ResetTool(), BoxZoomTool(), WheelZoomTool(), PanTool())

                # Graph render
                graph = from_networkx(G_symmetric, nx.spring_layout, scale=1, center=(0,0))

                graph.node_renderer.glyph = Circle(size='node_size', fill_color={'field': 'node_color', 'transform': mapper})

                graph.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
                graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=1)
                graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=1)

                graph.selection_policy = NodesAndLinkedEdges()

                plot.renderers.append(graph)

                # Save and get div and script
                script, div = components(plot) 
                clo_cen_html.append({
                    'div' : div,
                    'script' : script
                })
                with open(dir_riwayat+'/clo_cen_html.json', 'w') as outfile:
                    json.dump(clo_cen_html, outfile) # save html part Graph
                
                clo_cen = sort_and_small_dict(clo_cen, 100) # filter 100 besar
                with open(dir_riwayat+"/clo_cen.json", 'w') as outfile:
                    json.dump(clo_cen, outfile) # Save clo cen tabel
            else:
                with open(dir_riwayat+"/clo_cen_html.json") as openfile:
                    clo_cen_html = json.load(openfile) # save data json graph
                with open(dir_riwayat+"/clo_cen.json") as openfile:
                    clo_cen = json.load(openfile) # save data tabel
            
            # Eigenvector centrality
            if not os.path.exists(dir_riwayat+"/eig_cen.json") or not os.path.exists(dir_riwayat+"/eig_cen_html.json"):
                G_symmetric = nx.Graph()
                relations = []

                with open(dir_relation) as openfile: # open file relations.json
                    relations = json.load(openfile)

                for edge in relations:
                    G_symmetric.add_edge(edge['node1'], edge['node2'])
                    
                eig_cen = nx.eigenvector_centrality(G_symmetric)
                
                # Set node size and color
                node_size = {k:100*v for k, v in eig_cen.items()}
                node_color = {k:15*v for k, v in eig_cen.items()}

                for i in eig_cen.items():
                    if i[1] < 0.1: # menghapus node yg skornya kurang dari 0.1
                        G_symmetric.remove_node(i[0])

                # Set node attribute
                nx.set_node_attributes(G_symmetric, node_color, 'node_color')
                nx.set_node_attributes(G_symmetric, node_size, 'node_size')

                # Map cubehelix_palette (Untuk Warna)
                palette = sns.cubehelix_palette(21)
                pal_hex_lst = palette.as_hex()

                mapper = LinearColorMapper(palette=pal_hex_lst, low=0, high=21)

                # Init Plot
                plot = Plot(x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))
                plot.title.text = "Graph Eigenvector Centrality"

                plot.add_tools(HoverTool(tooltips=[("index", "@index")]), TapTool(), BoxSelectTool(), ResetTool(), BoxZoomTool(), WheelZoomTool(), PanTool())

                # Graph render
                graph = from_networkx(G_symmetric, nx.spring_layout, scale=1, center=(0,0))

                graph.node_renderer.glyph = Circle(size='node_size', fill_color={'field': 'node_color', 'transform': mapper})

                graph.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
                graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=1)
                graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=1)

                graph.selection_policy = NodesAndLinkedEdges()

                plot.renderers.append(graph)

                # Save and get div and script
                script, div = components(plot) 
                eig_cen_html.append({
                    'div' : div,
                    'script' : script
                })
                with open(dir_riwayat+'/eig_cen_html.json', 'w') as outfile:
                    json.dump(eig_cen_html, outfile) # save html part Graph
                
                eig_cen = sort_and_small_dict(eig_cen, 100) # filter 100 besar
                with open(dir_riwayat+"/eig_cen.json", 'w') as outfile:
                    json.dump(eig_cen, outfile) # Save eig cen
            else:
                with open(dir_riwayat+"/eig_cen_html.json") as openfile:
                    eig_cen_html = json.load(openfile) # save data graph
                with open(dir_riwayat+"/eig_cen.json") as openfile:
                    eig_cen = json.load(openfile) # save data tabel

            deg_cen = centrality_to_str_arr(deg_cen)
            clo_cen = centrality_to_str_arr(clo_cen)
            bet_cen = centrality_to_str_arr(bet_cen)
            eig_cen = centrality_to_str_arr(eig_cen)

            # show raw data
            raw_data = []
            with open(dir_riwayat+"/hashtags.json") as openfile:
                raw_data = json.load(openfile)
            
            waktu = (time.time() - start_time) # Hitung waktu proses
            waktu_filter = divmod(waktu, 60)
            menit = waktu_filter[0]
            detik = waktu_filter[1]

            cut_date = os.path.basename(dir_riwayat).split("_")
            day = cut_date[1]
            month = cut_date[2]
            year = cut_date[3]

            return render_template('index.html', status='proses', tag=riwayat+"_"+str(day)+"/"+str(month)+"/"+str(year), n_nodes=f'{n_nodes:,d}', n_edges=f'{n_edges:,d}', raw_data=raw_data, tag_html=tag_html, bet_cen=bet_cen, deg_cen=deg_cen, clo_cen=clo_cen, eig_cen=eig_cen, deg_cen_html=deg_cen_html, bet_cen_html=bet_cen_html, clo_cen_html=clo_cen_html, eig_cen_html=eig_cen_html, menit=f'{menit:.0f}', detik=f'{detik:.2f}')
        else:
            return jsonify("Isian Kosong")
        
    # else:
    #     return jsonify("Get Back !")

# Run Server
if __name__ == '__main__':
    app.run(debug=True)