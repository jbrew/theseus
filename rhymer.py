import nltk
import cmprssr
import models
import math
import operator
import pathfinder


class Rhymer(object):

	def __init__(self, filter_list):
		self.filter_list = filter_list
		self.entries = dict(nltk.corpus.cmudict.entries())

	def rhyme(self, target, level):
		rhymes = []
		syllables = self.entries[target]
		rhymes += [word for word, pron in self.entries.items() if pron[-level:] == syllables[-level:]]
		rhymes = [rhyme for rhyme in rhymes if rhyme in self.filter_list]
		return set(rhymes)

def make_rhymer(d):
	return Rhymer(filter_list=d.keys())

def paths_to_rhyme(start, endsound, rhymer, d):
	candidates = rhymer.rhyme(endsound, 2)
	print candidates





### TESTS ####

def rhyme_tests(d):
	r = Rhymer(d.keys())
	assert 'dashing' in r.rhyme('flashing',4)
	assert 'tragic' in r.rhyme('magic',3)




if __name__ == '__main__':
	pass



	#d = cmprssr.get_dict('words/norm_1w.txt',0.98)
	#rhyme_tests(d)
	#entropy_tests()
	#account_tests()



