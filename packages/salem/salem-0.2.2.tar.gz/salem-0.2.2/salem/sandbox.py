import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

a = np.arange(9, dtype=np.float).reshape((3, 3))

f, ax = plt.subplots()

ax.imshow(a)

from matplotlib.transforms import Transform

class mytransform(Transform):
    """
    A transform class for mpl axes using Grids.
    """

    input_dims = 2
    output_dims = 2
    is_separable = False
    has_inverse = False

    def transform_non_affine(self, xy):
        xx, yy = xy[:, 0:1], xy[:, 1:2]
        return ax.transData.transform(np.concatenate((xx, yy), 1))


ax.quiver([1, 2], [1, 2], np.ones(4), np.ones(4), transform=mytransform())

cax = make_axes_locatable(ax).append_axes(position='right', size='5%', pad=0.05)

plt.show()