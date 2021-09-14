import json
from acs import acs
import sys
  
f = open(sys.argv[1])
data = json.load(f)
batchmeansList = []
for j in range (0, len(data["global"]["avg_wait"])):
    batchmeansList.append(str(data["global"]["avg_wait"][j]))
f.close()

acs( batchmeansList, str(sys.argv[2]) )
