# skeleton script for calling saturnlab
from saturnlab_main import saturnlab_extract
res = saturnlab_extract('test')
"""
response object is a tuple of dictionaries
0 -> papers_ranking
1 -> stub
2 -> entity responses
3 -> concept responses
"""
papers_ranking = res[0]
stub = res[1]
entity_response = res[2]
concept_response = res[3]

print(type(list(entity_response.values())[0]))
