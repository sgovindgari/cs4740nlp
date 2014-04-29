import random

def generateRandom(filename):
	with open(filename, 'w') as f:
		f.write('Id,Answer')
		for i in range(0, 1224):
			f.write(str(i) + "," + str(random.choice([-1,0,1])) + '\n')
		f.close()

generateRandom('data/baseline_random_guess_choice.csv')