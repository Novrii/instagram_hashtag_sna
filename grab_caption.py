import time
import json


arr = []

with open('hasil/posts.json', 'r') as f:
    arr = json.loads(f.read()) # load json data from previous step
    
# print(len(arr))

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
    
with open('captions.json', 'w', encoding='utf-8') as outfile:
    json.dump(captions, outfile, ensure_ascii=False) # save to json
    print("Saved")