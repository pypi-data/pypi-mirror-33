import pyximport; pyximport.install()


from ncls import NCLS

import pickle
import pandas as pd
import numpy as np

# starts = np.random.randint(0, int(1e8), int(1e3))
starts = np.array(range(100))
ends = starts + 100
ids = starts

ncls = NCLS(starts, ends, ids)

print(ncls.c_has_overlap(0, 1000))

for i in range(0, 100):
    for j in ncls.find_overlap_list(i, i + 10):
        print(j)
