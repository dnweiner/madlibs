from __future__ import unicode_literals

from django.db import models
from django.core.files.storage import FileSystemStorage

fs = FileSystemStorage(location='/media/stories/')

# Create your models here.

class Story(models.Model):
	#id = models.AutoField(primary_key=True) #wiki says this is included by default
	story_name = models.CharField(max_length = 30)
	story_file = models.FileField(storage=fs) #should upload to ~/public_html/CP/madlib/media/stories
	# num_blanks = models.PositiveSmallIntegerField() #specify the number of blanks
	#keywords = #a list (of length num_blanks) of words to fill in the blanks (in story-traversal order)
	def __str__(self):
		return self.story_name
	
	