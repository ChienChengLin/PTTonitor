from id_query.models import UserWordFreq
from id_query.models import WordFreq

import json
import codecs

def DatabaseCreate():
	with open('id_freq_dict.json') as f:
		id_freq_dict = json.load(f)


	for ID, freq_dict in id_freq_dict.iteritems():
		UserWordFreq_obj = UserWordFreq.objects.create(user=ID)

		length = len(freq_dict.keys())
		if(length >= 50):
		    top_word_freq = [t for t in sorted(freq_dict.items(), key=lambda x: -x[1])][:50]
		else:
		    top_word_freq = [t for t in sorted(freq_dict.items(), key=lambda x: -x[1])][:length]

		for word_freq in top_word_freq:
			WordFreq.objects.create(word=word_freq[0], freq=word_freq[1], user=UserWordFreq_obj)