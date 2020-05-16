import requests
import time
import json


arr = []

with open('posts.json', 'r') as f:
    arr = json.loads(f.read()) # load json data from previous step
    
print(len(arr))

captions = []
for item in arr:
    shortcode = item['shortcode']

    caption = item['edge_media_to_caption']['edges']
    print(len(caption))
    try:
        if len(caption) != 0:
            text = item['edge_media_to_caption']['edges'][0]['node']['text']
            print(text)
            captions.append({
                'shortcode' : shortcode,
                'caption' : text
            })
    except:
        print(len(caption))
    
with open('captions3.json', 'w', encoding='utf-8') as outfile:
    json.dump(captions, outfile, ensure_ascii=False) # save to json