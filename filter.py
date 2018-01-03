#========================================================
# 2017 - UTFPR
# https://gitlab.com/gabrielsouzaesilva
# https://github.com/cordeirolibel/
# https://gitlab.com/mcampx
#========================================================

import pandas as pd 
from xml.dom.minidom import parse
import xml.dom.minidom
from unidecode import unidecode
from stringdist import levenshtein

#========================================================
#===== .TXT  
#========================================================
try:
	lines = open('data/movie_titles.txt', 'r').read().split('\n')
	titles = [line.split(',')[2:][0].strip() for line in lines]
except:
	print('Erro:','data/movie_titles.txt','not found')
	print('Download all data in','https://archive.org/details/nf_prize_dataset.tar')
	exit()

#========================================================
#===== .XML   (read all names)
#========================================================

# Open XML document using minidom parser
MovieXML = xml.dom.minidom.parse("movie.xml")

movies = MovieXML.documentElement

# Get all the movies in the universe
movies = movies.getElementsByTagName("movie")

names_xml = set()
urls_xml = set()
for movie in movies:
	#add if not exist
	names_xml.add(movie.getAttribute('name'))
	urls_xml.add(movie.getAttribute('url'))

#========================================================
#===== Find netflix indexes
#========================================================

count_without = 0
count_with = 0
indexes = list()
for name,url in zip(names_xml,urls_xml):
	#procura o q tiver menor distancia de edicao com 'name'
	ls = list()
	for title in titles:
		ls.append(levenshtein(name,title))
	#fator de qualidade
	if min(ls) < 5: 
		idx = ls.index(min(ls))
		indexes.append((idx,url,name))
		count_with+=1
	else:
		count_without+=1
	
print('Found',count_with,'/',count_without+count_with)

#========================================================
#===== Organizing Netflix Data
#========================================================

df = pd.DataFrame()
for idx,url,name in indexes:

	#http://www.imdb.com/title/tt0086190/  ->  0086190   ->   86190
	url = url[-8:-1]

	# load netflix data
	file = 'mv_'+'0'*(7-len(str(idx)))+str(idx)+'.txt'
	nf_data = open('data/training_set/'+file, 'r').read()
	nf_data = nf_data.split('\n')[1:-1]
	nf_data = [nf_d.split(',') for nf_d in nf_data]

	#to dataframe
	df_movie = pd.DataFrame(nf_data,columns = ['user','rate','date'])
	df_movie['name'] = name
	df_movie['url'] = url

	df = pd.concat([df,df_movie])

#eliminando usuarios que aparecem só uma vez
df['freq'] = df.groupby('user')['user'].transform('count')
df = df[df['freq']>1]
df['user'] = pd.Categorical(df['user']).codes
df = df.sort_values('user')

#eliminando colunas inuteis
columns = ['freq','name','date']
df = df.drop(columns, axis=1)

#save
df.to_csv('NetFlix.csv',index=False)

print('NetFlix.csv ',len(df),'rows')
print('End')