import json

arr = []

with open('captions.json', encoding='utf-8') as f:
    arr = json.load(f)

hashtag = []

for item in arr:
    shortcode = item['shortcode']
    caption = item['caption']
    hashtags = []
    display = item['display']
    
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
    hashtag.append({
        'shortcode' : shortcode,
        'hashtag' :  hashtags,
        'display' : display
    })

with open('hashtags3.json', 'w', encoding='utf-8') as outfile: # encoding utf-8 utk izin simpan karakter selain latin
    json.dump(hashtag, outfile, ensure_ascii=False)

print("Jumlah Captions:",len(arr))
print("Jumlah Caption with tag:",len(hashtag))
