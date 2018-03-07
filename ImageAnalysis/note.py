N = 1005
a = np.zeros(1005, dtype='B')
i = N//8
j = N - i*8
a[i] = 1 << j
v = (a[i] & (1 << j)) >> j
