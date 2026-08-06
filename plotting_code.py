import matplotlib.pyplot as plt   # plotting library
import numpy as np                # scientific computing library

fig, ax = plt.subplots()
ax.plot([1, 2, 3, 4], [1, 4, 2, 3], label="first run", color="crimson")
ax.plot([1, 2, 3, 4], [2, 3, 1, 4], label="second run", color="teal")
ax.set_title("My First Plot")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.legend()
plt.show()
fig.savefig("my_plot.png", dpi=300, bbox_inches="tight")
plt.close(fig)