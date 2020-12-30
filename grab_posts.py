import requests
import time
import json
import urllib3

arr = []

end_cursor = '' # penanda halaman
tag = 'earth' # tag yg mau dicari
page_count = 1 # jumlah halaman

for i in range(0, page_count):
    url = "https://www.instagram.com/explore/tags/{0}/?__a=1&max_id={1}".format(tag, end_cursor)
    # r = requests.get(url)
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    data = json.loads(r.data)
    print(r.status)
    exit()
    
    
    end_cursor = data['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor'] # value for the next page
    edges = data['graphql']['hashtag']['edge_hashtag_to_media']['edges'] # list with posts
    
    for item in edges:
        arr.append(item['node'])
        print(item['node'])

    # print(time)
    time.sleep(2) # insurence to not reach a time limit
    
print("End cursor:",end_cursor) # save this to restart parsing with the next page

with open('posts.json', 'w') as outfile:
    json.dump(arr, outfile) # save to json