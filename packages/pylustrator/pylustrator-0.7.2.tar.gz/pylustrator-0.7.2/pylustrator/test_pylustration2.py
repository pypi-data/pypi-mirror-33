"""
Enable picking on the legend to toggle the legended line on and off
"""
import numpy as np
import matplotlib.pyplot as plt

from pylustration import StartPylustration, fig_text, add_axes, StartDragger
#plt.ion()

fig = plt.figure(0, (4/2.54, 4/2.54))

x = np.arange(10)
y = x**2

plt.plot(x, y)
plt.tight_layout()
#plt.axes([0, 0, 1, 1], zorder=-1)

plt.show()
