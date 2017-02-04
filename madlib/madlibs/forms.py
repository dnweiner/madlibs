from django.forms import ModelForm
from madlibs.models import Story

class StoryModelForm(ModelForm):
	class Meta:
		model = Story
		fields = ['story_name', 'story_file']