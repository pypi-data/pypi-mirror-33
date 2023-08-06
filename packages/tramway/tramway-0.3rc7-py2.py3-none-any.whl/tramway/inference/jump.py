
from .base import *
import numpy as np
import pandas as pd

setup = {}

def infer(cells, **kwargs):
        index, dr = [], []
        for i in cells:
                cell = cells[i]
                if not cell:
                        continue
                index.append(i)
                dr_i = np.mean(cell.dr, axis=0)
                dr.append(dr_i)
        dr = np.vstack(dr)
        # format the output
        result = pd.DataFrame(dr,
                index=index,
                columns=[ 'dr ' + col for col in cells.space_cols ])
        return result

