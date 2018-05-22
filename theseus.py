import math
import operator
import os

def get_transition_dict(path):

	# reads from a file of the format: [space separated words] [\t] [count]
	with open(path) as f:
		ngrams = {line.split('\t')[0].lower(): float(line.split('\t')[1]) for line in f.readlines()}
	tree = {}

	for ngram, count in ngrams.items():
		head, tail = ngram.split()[0], ngram.split()[1]
		if head in tree:
			tree[head][tail] = count
		else:
			tree[head] = {tail: count}

	return tree

def normalize_dict(d):
	for head, sub_dict in d.items():
		d[head] = normalize(sub_dict)
	return d

def normalize(d):
	new_d = {}

	total = 0
	for completion, count in d.items():
		total += float(count)
	for completion, count in d.items():
		new_d[completion] = float(count)/total

	return new_d

def all_tokens(transition_dict):
	tokens = set([])
	for key, subdict in transition_dict.items():
		tokens.add(key)
		for subkey in subdict:
			tokens.add(subkey)
	return tokens

def transition_cost(bigram, d):
	head, tail = bigram[0], bigram[1]
	return -1 * math.log(d[head][tail]) if head in d and tail in d[head] else 100

def sentence_cost(sentence, d):
	seq = sentence.split()
	transitions = [seq[i:i+2] for i in range(len(seq)-1)]
	return sum([transition_cost(t, d) for t in transitions])


def shortest_paths_matrix(wordlist, td):
	matrix = {w1: {w2: (w2,100) for w2 in wordlist} for w1 in wordlist}

	for start, ends in matrix.items():
		for end, best_path in ends.items():
			next_step, total_cost = best_path[0], best_path[1]
			cost = transition_cost([start,end],td)
			if start in td and end in td[start] and cost < total_cost:
				new_path = (end, cost)
				matrix[start][end] = new_path
	return matrix

# operates on the matrix itself and returns number of changes made
def seek_new_paths(matrix, td):
	paths_found = 0
	for tok1 in matrix:
		for tok2 in matrix[tok1]:
			current_cost = matrix[tok1][tok2][1]
			if tok1 in td:
				for tail in td[tok1]:
					if tail in matrix:
						initial_cost = transition_cost([tok1, tail], td)
						remaining_cost = matrix[tail][tok2][1]
						new_cost = initial_cost + remaining_cost
						if new_cost < current_cost:
							paths_found += 1
							matrix[tok1][tok2] = (tail, new_cost)
							current_cost = new_cost
	return paths_found

def shortest_path(start, end, matrix):
	path = [start]
	length = matrix[start][end][1]
	while not path[-1] == end:
		path.append(matrix[path[-1]][end][0])
	return " ".join(path[1:]), length

def shortest_path_through(states, matrix):
	pairs = [states[i:i+2] for i in range(len(states)-1)]
	print pairs
	head = shortest_path(pairs[0][0], pairs[0][1], matrix)[0].split()
	tail = [shortest_path(pair[0],pair[1],matrix)[0] for pair in pairs[1:]]
	return " ".join([states[0]]+head+tail)

def shortest_paths_to_all(start, ends, matrix):
	paths_scores = [shortest_path(start, end, matrix) for end in ends]
	return sorted(paths_scores, key=operator.itemgetter(1))

def shortest_path_to_rhyme(start, rhyme_target, rhy, matrix):
	rhyme_set = rhy.rhyme(rhyme_target, 2)
	shortest_paths = shortest_paths_to_all(start, rhyme_set, matrix)
	print shortest_paths
	return shortest_paths[0]

def keep_seeking(matrix, td):
	new_paths = None
	while new_paths != 0:
		new_paths = seek_new_paths(matrix, td)
		print new_paths, 'new paths found'

def save_td(td, fname):
	import json
	path = 'json/%s.json' % fname
	with open(path, 'w') as fp:
	    json.dump(td, fp, sort_keys=True)

def load_td(fname):
	import json
	path = 'json/%s.json' % fname
	with open(path, 'r') as fp:
	    return json.load(fp)


def make_voice_dicts():
	import os
	for fname in os.listdir('voices')[1:]:
		path = 'voices/%s' % fname
		print path
		d = normalize_dict(get_transition_dict(path))
		matrix = shortest_paths_matrix((all_tokens(d)),d)
		keep_seeking(matrix,d)
		print 'saving to', fname
		save_td(matrix, fname)

### TESTS ####

def transition_tests():
	print transition_cost(['of', 'the'], d)
	print sentence_cost('percent of the time', d)


def make_ramones_matrices(d):
	ramones_d = normalize_dict(get_transition_dict('voices/ramones_2w.txt'))
	ramones_matrix = shortest_paths_matrix(all_tokens(ramones_d), ramones_d)
	keep_seeking(ramones_matrix,ramones_d)
	save_td(ramones_matrix,'ramones_self')

	ramones_matrix = shortest_paths_matrix(all_tokens(ramones_d), d)
	keep_seeking(ramones_matrix,d)
	save_td(ramones_matrix,'ramones_general')

def ramones_test(d):
	print shortest_path('i','pain',ramones_matrix)
	print shortest_path('i','rain',ramones_matrix)
	print shortest_path('i','again',ramones_matrix)
	print shortest_path('i','brain',ramones_matrix)
	print shortest_path('i','complain',ramones_matrix)

def usa_test():
	spm = shortest_paths_matrix('the united states of america'.split(), d)
	keep_seeking(spm, d)

def lyrics_batch():
	path = '/Users/jbrew/Desktop/library/lyrics/'
	for fname in os.listdir(path)[1:]:
		full_path = path + fname
		print full_path
		print 'saving to', fname
		d = normalize_dict(get_transition_dict(full_path))
		matrix = shortest_paths_matrix((all_tokens(d)),d)
		keep_seeking(matrix,d)
		save_td(matrix, fname)

def ramones():
	ramones_matrix = load_td('ramones_self')
	#print shortest_path('wish','pain',ramones_matrix)
	print shortest_path('rain','brain',ramones_matrix)
	print shortest_path('today','brain',ramones_matrix)
	print shortest_path('as','brain',ramones_matrix)
	print shortest_path('you','brain',ramones_matrix)
	print shortest_path('we','brain',ramones_matrix)
	print shortest_path('everyones','brain',ramones_matrix)
	print shortest_path('my','street',ramones_matrix)
	print
	"""
	for key in ramones_matrix:
		print shortest_path(key,'brain',ramones_matrix)

	for key in ramones_matrix:
		print shortest_path(key,'again',ramones_matrix)
	"""

def hello_worlds():
	import os
	matrices = [(load_td(fname.split('.')[0]),fname) for fname in os.listdir('json')[1:]]
	for m, mname in matrices:
		print mname
		try:
			print shortest_path('i','again', m)
		except:
			print 'words not both in matrix'


def big_test():
	d = normalize_dict(get_transition_dict('words/count_2w.txt'))


def rhyme_test():
	print shortest_paths_to_all('i',['brain','pain','again'],ramones_matrix)[0]

	from rhymer import Rhymer
	r = Rhymer(filter_list=ramones_matrix.keys())
	rhyme_set = r.rhyme('pain',2)
	print shortest_paths_to_all('i',rhyme_set,ramones_matrix)
	print shortest_path_to_rhyme('i','goon',r,ramones_matrix)
	print shortest_path_to_rhyme('i','heat',r,ramones_matrix)
	print shortest_path_to_rhyme('i','want',r,ramones_matrix)
	print shortest_path_to_rhyme('i','one',r,ramones_matrix)



if __name__ == '__main__':

	ramones_matrix = load_td('ramones')
	print shortest_path('i','you',ramones_matrix)
	print shortest_path('you','to',ramones_matrix)
	print shortest_path_through(['i','need','yeah'],ramones_matrix)

	#hello_worlds()
	#make_voice_dicts()
	




	