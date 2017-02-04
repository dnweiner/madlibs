from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from random_words import RandomWords

import nltk, string, random, re

def blanks(filepath): # calculate the number of lines in a file, theoretically ignoring blank lines
	num_blanks = 0
	with open(filepath, 'r') as count_lines:
		for line in count_lines:
			if line is not None and line != '' and line is not '\n':
				num_blanks = num_blanks + 1 # one blank for each line
	return num_blanks

def write_for_download(filepath, newlines): # generate a new file, suffixed with _filled and return its filepath
	filepath_filled = string.replace(filepath, '.txt', '_filled.txt')
	with open(filepath_filled, 'w') as f_filled:
		f_filled.writelines(newlines)
	return filepath_filled



