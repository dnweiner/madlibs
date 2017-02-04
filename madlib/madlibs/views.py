from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from random_words import RandomWords

import nltk, string, random, re

from .helper_functions import blanks, write_for_download

from .models import Story # database
from .forms import StoryModelForm # form to insert entries into database

# Create your views here.

def index(request):
	story_list = Story.objects.all()
	context = {
		'story_list': story_list,
	}
	return render(request, 'madlibs/index.html', context)

def home_button(request): # functions as home button
	return HttpResponseRedirect(reverse('madlibs:index'))

##########################################

def detail(request, story_id):
	story = get_object_or_404(Story, pk=story_id)
	filepath = story.story_file.path
	
	blank_types = [] # need a local copy that we can initialize as empty each time
	replace_words = [] # need a local copy that we can initialize as empty each time
	
	tokens = [] # don't strictly need to keep track of all these in arrays, but it could come in handy
	tagged = [] # don't strictly need to keep track of all these in arrays, but it could come in handy
	
	# do stuff with nltk here to populate and pass blank_types
	num_blanks = blanks(filepath) # one blank for each line
	with open(filepath, 'r') as f:
		for line in f:
			tokens.append(nltk.word_tokenize(line)) # tokenize the line and add it to a list of tokenized lines
			tagged.append(nltk.pos_tag(tokens[len(tokens)-1])) # tag the most recently tokenized line
			most_recent_line = len(tagged) - 1 # type less later: len(tagged) == len(tokens)
			num_tokens = len(tagged[most_recent_line]) # number of tokens of the most recent line
			if num_tokens > 0:
				j = random.randint(0, (num_tokens - 1)) # generate a random int between 0 and the number of tokens				
				tag = tagged[most_recent_line][j][1] # pick a random token in the most recent line
				if tag == '' or tag is None:
					continue
				while tag != 'CD' and tag != 'JJ' and tag != 'RB' and tag != 'NNS' and tag != 'VBG' and tag != 'VBD' and tag != 'NN': # sentinel
					j = (j + 1) % num_tokens # generate another random int between 0 and the number of tokens				
					tag = tagged[most_recent_line][j][1] # pick another random token in the most recent line						
				if tag == 'CD':
					blank_types.append("Number") # type of word we are filling in
					replace_words.append(tokens[most_recent_line][j]) # word we are replacing
				elif tag == 'JJ':
					blank_types.append("Adjective")
					replace_words.append(tokens[most_recent_line][j])
				elif tag == 'RB':
					blank_types.append("Adverb")
					replace_words.append(tokens[most_recent_line][j])
				elif tag == 'NNS':
					blank_types.append("Plural noun")
					replace_words.append(tokens[most_recent_line][j])
				elif tag == 'VBG':
					blank_types.append("Gerund")
					replace_words.append(tokens[most_recent_line][j])
				elif tag == 'VBD':
					blank_types.append("Past-tense verb")
					replace_words.append(tokens[most_recent_line][j])
				elif tag == 'NN':
					blank_types.append("Singular noun")
					replace_words.append(tokens[most_recent_line][j])
				else:
					continue
			else:
				continue
					
	return render(request, 'madlibs/detail.html', {'story': story, 'blank_types': blank_types, 'replace_words': replace_words})

def fill(request, story_id):
	story = get_object_or_404(Story, pk=story_id)
	filepath = story.story_file.path
	
	num_blanks = blanks(filepath)

	pattern = re.compile(r"^[\w\d]+$") 

	# we want to put the filled-in words into the lines here replacing the original words
	newlines = []
	
	filled_words = []
	replace_words = []
	
	counter1 = 1
	while len(filled_words) < num_blanks:
		filled_words.append(request.POST.get('blank'+str(counter1), "")) # add each input field word to a list of filled-in words
		counter1 = counter1 + 1
	
	counter2 = 1	
	while len(replace_words) < num_blanks:
		replace_words.append(request.POST.get('word'+str(counter2), ""))
		counter2 = counter2 + 1					
		
	with open(filepath, 'r') as f:
		counter3 = 0
		for line in f:
			newline = line
			if len(replace_words) == len(filled_words): # MUST be true
				print filled_words[counter3]
				print replace_words[counter3]
				if pattern.match(filled_words[counter3]) is not None: #only words and numbers are acceptable
					newword = str('<u>' + filled_words[counter3] + '</u>')
					newline = newline.replace(replace_words[counter3], newword)
				else:
					print "REGEX FAILS"				
				newlines.append(newline)
				counter3 = counter3 + 1
				error_message = "Success!"
			else:
				error_message = "ERROR: number of replacement words does not equal the number of words to be replaced."

	filepath_filled = write_for_download(filepath, newlines) 
		
	return render(request, 'madlibs/filled.html', {'story': story, 'filepath': filepath_filled, 'newlines': newlines, 'error_message': error_message})

def randomize(request, story_id):
	story = get_object_or_404(Story, pk=story_id)
	filepath = story.story_file.path
	
	num_blanks = blanks(filepath)
	rw = RandomWords()	
	random_count = 50 * num_blanks
	words = rw.random_words(count=random_count) # generate as many random words as 10x the number of lines in the file
	
	filled_words = []
	replace_words1 = []
	blank_types = []
	
	# we want to put the filled-in words into the lines here replacing the original words
	newlines = []
	
	counter1 = 1
	while len(blank_types) < num_blanks:
		blank_types.append(request.POST.get('type'+str(counter1), "")) # add each input field word to a list of filled-in words
		counter1 = counter1 + 1
	
	counter2 = 1	
	while len(replace_words1) < num_blanks:
		replace_words1.append(request.POST.get('word'+str(counter2), ""))
		counter2 = counter2 + 1					

	if len(blank_types) != len(replace_words1): # cutoff point
		error_message = "ERROR: number of blanks is not equal to the number of words to replace"
		return render(request, 'madlibs/filled.html', {'story': story, 'filepath': filepath_filled, 'newlines': newlines, 'error_message': error_message})
	
	random_tokens = [] # don't strictly need to keep track of all these in arrays, but it could come in handy
	random_tagged = [] # don't strictly need to keep track of all these in arrays, but it could come in handy
	# do stuff with nltk here to make sure the right type of random words are inserted in the right places
	for word in words:
		random_tokens.append(nltk.word_tokenize(word)) # tokenize each and add it to a list of tokenized lines
		random_tagged.append(nltk.pos_tag(random_tokens[len(random_tokens)-1])) # tag the most recently tokenized word
	
	i = 0
	while len(filled_words) < len(replace_words1): # go through all of the blanks we need to fill
		if i == len(blank_types):
			i = i - 1
		save = i
		for j in range(len(random_tagged)): #go through the list of tagged random words
			random_tag = random_tagged[j][0][1] # get each random word's tag
			if blank_types[i] == "Number":
				filled_words.append(str(11)) # replace all numbers with 11 because it's Danny's lucky number
				break
			elif blank_types[i] == "Adjective" and random_tag == 'JJ':
				filled_words.append(str(random_tokens[j][0]))
				del random_tagged[j] #take this random word out of consideration, as it's been used
				del random_tokens[j]
				break
			elif blank_types[i] == "Adverb" and random_tag == 'RB':
				filled_words.append(str(random_tokens[j][0]))
				del random_tagged[j] #take this random word out of consideration, as it's been used
				del random_tokens[j]
				break
			elif blank_types[i] == "Plural noun" and random_tag == 'NNS':
				filled_words.append(str(random_tokens[j][0]))
				del random_tagged[j] #take this random word out of consideration, as it's been used
				del random_tokens[j]
				break
			elif blank_types[i] == "Gerund" and random_tag == 'VBG':
				filled_words.append(str(random_tokens[j][0]))
				del random_tagged[j] #take this random word out of consideration, as it's been used
				del random_tokens[j]
				break
			elif blank_types[i] == "Past-tense verb" and random_tag == 'VBD':
				filled_words.append(str(random_tokens[j][0]))
				del random_tagged[j] #take this random word out of consideration, as it's been used
				del random_tokens[j]
				break
			elif blank_types[i] == "Singular noun" and random_tag == 'NN':
				filled_words.append(str(random_tokens[j][0]))
				del random_tagged[j] #take this random word out of consideration, as it's been used
				del random_tokens[j]
				break
			else:
				i = save
				continue
		i = i + 1
	
	pattern = re.compile(r"^[\w\d]+$") # regex check

	with open(filepath, 'r') as f:
		counter3 = 0
		for line in f:
			newline = line
			if len(replace_words1) == len(filled_words): # MUST be true
				print filled_words[counter3]
				print replace_words1[counter3]
				# if pattern.match(filled_words[counter3]) is not None: #only words and numbers are acceptable
					#newline = string.replace(newline, replace_words_global[i], filled_words[i])
				newword = str('<u>' + filled_words[counter3] + '</u>')
				newline = newline.replace(replace_words1[counter3], newword)
				# else:
					# print "REGEX FAILS"				
				newlines.append(newline)
				counter3 = counter3 + 1
				error_message = "Success!"
			else:
				print replace_words1
				print "LENGTH OF REPLACE_WORDS:" + str(len(replace_words1))
				print filled_words
				print "LENGTH OF FILLED_WORDS:" + str(len(filled_words))
				error_message = "ERROR: number of replacement words does not equal the number of words to be replaced."
	
	filepath_filled = write_for_download(filepath, newlines)
		
	return render(request, 'madlibs/filled.html', {'story': story, 'filepath': filepath_filled, 'newlines': newlines, 'error_message': error_message})

##########################################

def upload_story(request):
	if request.method == 'POST':
		form = StoryModelForm(request.POST, request.FILES)
		if form.is_valid():
			story_instance = form.save(commit=False)
			story_instance.save()
			return HttpResponseRedirect(reverse('madlibs:index'))
	
	else:
		form = StoryModelForm()
	
	return render(request, 'madlibs/upload_story.html', {'form':form})

def download_story(request):
	filepath = request.POST.get('filepath', "")
	# print filepath
	if filepath is not "" and filepath is not None:
		with open(filepath, 'r+') as f_filled:
			response = HttpResponse(f_filled, content_type='text/plain')
			response['Content-Disposition'] = 'attachment; filename='+f_filled.name
			return response
	return HttpResponseRedirect(reverse('madlibs:index'))