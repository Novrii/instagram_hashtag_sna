import time
import json
import csv

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
    print("Saved json file")

with open('captions.csv', mode='w') as csv_file:
    for x in captions:
        # print(x['shortcode'])
        kolom = ['shortcode', 'caption', 'display']
        writer = csv.DictWriter(csv_file, fieldnames=kolom)

        writer.writeheader()
        writer.writerow({'shortcode': x['shortcode'], 'caption': (x['caption'].encode('ascii', 'ignore')).decode('utf-8'), 'display': x['display']})
    print("saved csv file")