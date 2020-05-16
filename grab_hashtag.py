import json

arr = []

with open('captions3.json', encoding='utf-8') as f:
    arr = json.load(f)

hashtag = []

for item in arr:
    shortcode = item['shortcode']
    caption = item['caption']
    hashtags = []
    
    for tag in caption.split():
        if tag.startswith("#"):
            tag_cek = tag.strip("#").split("#")
            if len(tag_cek) > 0: # cek jika hashtag tidak pakai spasi
                for tag_tag in tag_cek:
                    # menghilangkan tag dan emoji
                    hashtags.append((tag_tag.strip("#").encode('ascii', 'ignore')).decode('utf-8'))
            else:
                hashtags.append((tag.strip("#").encode('ascii', 'ignore')).decode('utf-8'))
    
    # hashtags = [tag.strip("#") for tag in caption.split() if tag.startswith("#")]
    hashtag.append({
        'shortcode' : shortcode,
        'hashtag' :  hashtags
    })

with open('hashtags1.json', 'w', encoding='utf-8') as outfile:
    json.dump(hashtag, outfile, ensure_ascii=False) # save file

print("Jumlah Captions:",len(arr))
print("Jumlah Caption with tag:",len(hashtag))
