from matplotlib import pyplot as plt
from matplotlib import style
import numpy as np

style.use('ggplot')

l1, l2, l1l2, sim, calc = np.loadtxt('traces3.1.csv', unpack=True, delimiter=',')

plt.plot(l1l2, sim)
plt.plot(l1l2, calc, color='g', linestyle='--')
plt.title('lambda vs E[U] (estimado=red, calculado=green)')
plt.ylabel('E [U]')
plt.xlabel('lambda1 + lambda2')

plt.show()
