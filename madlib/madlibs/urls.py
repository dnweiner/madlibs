from django.conf.urls import url

from madlibs import views

app_name = 'madlibs'
urlpatterns = [
	#ex: /madlibs/
	url(r'^$', views.index, name='index'),
	#ex: /madlibs/5/
	url(r'^(?P<story_id>[0-9]+)/$', views.detail, name='detail'),
	#ex: /madlibs/5/results/
	url(r'^home_button/$', views.home_button, name='home_button'),
	#ex: /madlibs/5/fill/
	url(r'^(?P<story_id>[0-9]+)/fill/$', views.fill, name='fill'),
	#ex: /madlibs/upload_story/
	url(r'^upload_story/$', views.upload_story, name='upload_story'),
	#ex: /madlibs/download_story/
	url(r'^download_story/$', views.download_story, name='download_story'),
	#ex: /madlibs/5/randomize
	url(r'^(?P<story_id>[0-9]+)/randomize/$', views.randomize, name='randomize'),
]




