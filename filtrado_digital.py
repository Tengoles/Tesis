#b = [2,4,5,6,7]
#a = [1,6,3,5,4,3]
def filtrar(b,a,x):
	y = []
	for n in range(len(x)):
		y.append(0)
		for i in range(len(b)):
			y[n] = b[i]*x[n-i] + y[n]
			if ((n-i) == 0):
				break

		for j in range(len(a)-1):
			if (n-(j+1))<0:
				break
			y[n] = -a[(j+1)]*y[n-(j+1)] + y[n]
			
	return y
