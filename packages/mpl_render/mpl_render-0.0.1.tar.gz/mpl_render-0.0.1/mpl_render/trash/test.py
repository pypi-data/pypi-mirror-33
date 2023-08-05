import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

fig1, ax1 = plt.subplots(1, 1)
r = ax1.imshow([[0]], origin='lower')

print(r)
print(ax1.images[0])

plt.show()
