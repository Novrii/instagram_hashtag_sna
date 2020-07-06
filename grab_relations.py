import json

arr = []
relations = []

with open('data/withgalaxy/hashtags.json') as openfile:
    arr = json.load(openfile)

count = 0
for idx_arr, post in enumerate(arr):
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
                    print(i,j)

# print(relations)

# with open('relations.json', 'w') as outfile:
#     json.dump(relations, outfile)