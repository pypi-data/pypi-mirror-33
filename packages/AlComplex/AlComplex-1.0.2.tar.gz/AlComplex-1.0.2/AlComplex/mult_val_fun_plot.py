import matplotlib.pyplot as plt

fig = plt.figure()

def split(coords):
	x = []
	y = []
	for i in coords:
		x.append(i[0])
		y.append(i[1])

	return x, y

def show_complex_plane(ax):
	ax.set_title('Complex Plane')

	ax.spines['left'].set_position('center')
	ax.spines['bottom'].set_position('center')

	fig.show()

def optimize(generator):
	return split(map(lambda x: x.to_rect_coord(), generator))

def scatter(generator):
	fig.clear()
	ax = fig.add_subplot(1,1,1)
	ax.scatter(*optimize(generator))
	show_complex_plane(ax)

def plot(generator):
	fig.clear()
	ax = fig.add_subplot(111)
	ax.plot(*optimize(generator))
	show_complex_plane(ax)