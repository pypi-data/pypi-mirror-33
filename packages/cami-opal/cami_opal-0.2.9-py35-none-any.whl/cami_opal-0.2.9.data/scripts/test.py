import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# mu, sigma = 200, 25
# x = mu + sigma*np.random.randn(1000,3)
# x1 = mu + sigma*np.random.randn(990,1)
# x2 = mu + sigma*np.random.randn(980,1)
# x3 = mu + sigma*np.random.randn(1000,1)
#plt.figure()
#n, bins, patches = plt.hist(x, 30, stacked=True, normed = True)
x1 = [1,2,3]
x2 = [4,5,6]

df2 = pd.DataFrame(np.random.rand(10, 2), columns=['a', 'b']).T
# print(df2)
# print(df2.T)
#print(np.random.rand(10, 4))
#print(pd.DataFrame(np.random.rand(10, 4), columns=['a', 'b', 'c', 'd']))

#df2.T.plot(kind='bar', stacked=True, legend=False, colormap=plt.get_cmap('gist_rainbow'))

fig, axs = plt.subplots(figsize=(8, 5))
axs.tick_params(axis='x',
                which='both',
                bottom='off',
                top='off',
                labelbottom='off')
# axs.plot(df2.index, df2)
df2.plot(kind='bar', ax=axs, stacked=True, legend=False, colormap=plt.get_cmap('gist_rainbow'), width=.9)

#print(n)
#print(bins)

#plt.hist([x1,x2], histtype='barstacked')
plt.show()