from xml.etree import ElementTree as ET
import re
import json
import glob
from zipfile import ZipFile
import tarfile
import os
import shutil
import time
import sys
import io
import xml
from extraction.utils import getTextFromTagNode,split, clean_txt




# THE MOST IMPORTANT: FROM .XML TEXTUAL INFORMATIONS EXTRACTION

class Patent_txt:

	def __init__(self, doc):
		self.path=doc
		self.save= True
		self.Dict_final={}



	def Extract_ref(self):

		with open(self.path, 'r', encoding='utf-8') as f:

			patent_number = None
			patent_date = None

			for line in f:

				if line.find('WKU')==0:
					patent_number = line.replace('WKU','').replace(' ','').replace('\n','').replace('&','')

				if line.find('APD')==0:
					patent_date= line.replace('APD','').replace(' ','').replace('\n','')

				if patent_date is not None and patent_number is not None:
					#add to dict
					self.Dict["REF PATENT"]='US'+patent_number+'-'+patent_date
					break

		if patent_number is None or patent_date is None:
			self.save=False
			print(" No Patent REF")




	def Extract_inventors(self):

		with open(self.path, 'r', encoding='utf-8') as f:

			authors = []
			pick=False

			for line in f:

				if pick:
					if line.find('NAM')==0:
						author_name = line.replace('NAM','').replace('\n','').split(';')
						author_name.reverse()
						authors.append(' '.join(' '.join(author_name).split()))
					pick = False

				if line.find('INVT')==0:
					pick=True


		if len(authors)==0:
			self.save=False
			print(" No AUTHORS")
		else:
			self.Dict["INVENTORS"]=authors

	


	def Extract_invention_title(self):

		with open(self.path, 'r', encoding='utf-8') as f:

			invention_title=None

			for line in f:

				if line.find('TTL')==0:
					invention_title = line.replace('TTL  ','')
					self.Dict["INVENTION_TITLE"]=invention_title


		if(invention_title==None):
			self.save=False
			print(" No INVENTION TITLE")

		


	def Extract_abstract(self):

		with open(self.path, 'r', encoding='utf-8') as f:

			abstract = None
			pick=False

			for line in f:

				if line.find('BSUM')==0:
					break

				if pick:
					abstract += line.replace('PAL  ','').replace('PAR  ','').replace('PAC  ','').replace('\n','')

				if line.find('ABS')==0:
					pick=True
					abstract=''


		if abstract is None:
			self.save=False
			print(" No ABSTRACT")
		else:
			self.Dict["ABSTRACT"]=clean_txt(abstract)

		





	def Extract_description(self):

		# BSUM part
		with open(self.path, 'r', encoding='utf-8') as f:

			pick=False
			new_part = False
			name_part = None

			for line in f:

				if line.find('DRWD')==0:
					if name_part is not None and len(part)>0:
							self.Dict[name_part] = clean_txt(part)
							# print(name_part)
					pick=False


				if pick:
					if line.find('PAC')==0 and line.replace(' ','').isupper():
						if name_part is not None and len(part)>0:
							self.Dict[name_part] = clean_txt(part)
							# print(name_part)
						newname = line.replace('PAC  ','').replace('\n','')
						if newname.replace(' ','').isupper():
							name_part = newname
							new_part=True
							part = ''


					if not new_part:
						part += line.replace('PAL  ','').replace('PAR  ','').replace('\n','')
					else:
						new_part = False


				if line.find('BSUM')==0:
					pick=True
					part = ''


		# DRWD part
		with open(self.path, 'r', encoding='utf-8') as f:

			pick=False
			new_part = False
			name_part = None

			for line in f:

				if line.find('DETD')==0:
					if name_part is not None and len(part)>0:
							self.Dict[name_part] = clean_txt(part)
							# print(name_part)
					pick=False


				if pick:
					if line.find('PAC')==0 and line.replace(' ','').isupper():
						if name_part is not None and len(part)>0:
							self.Dict[name_part] = clean_txt(part)
							# print(name_part)
						newname = line.replace('PAC  ','').replace('\n','')
						if newname.replace(' ','').isupper():
							name_part = newname
							new_part=True
							part = ''


					if not new_part:
						part += line.replace('PAL  ','').replace('PAR  ','').replace('\n','')
					else:
						new_part = False


				if line.find('DRWD')==0:
					pick=True
					part = ''



		# DETD part
		with open(self.path, 'r', encoding='utf-8') as f:

			pick=False
			new_part = False
			name_part = None


			for line in f:

				if line.find('CLMS')==0:
					if name_part is not None and len(part)>0:
							self.Dict[name_part] = clean_txt(part)
							# print(name_part)
					pick=False


				if pick:
					if line.find('PAC')==0 and line.replace(' ','').isupper():
						if name_part is not None and len(part)>0:
							self.Dict[name_part] = clean_txt(part)
							# print(name_part)
						newname = line.replace('PAC  ','').replace('\n','')
						if newname.replace(' ','').isupper():
							name_part = newname
							new_part=True
							part = ''


					if not new_part:
						part += line.replace('PAL  ','').replace('PAR  ','').replace('\n','')
					else:
						new_part = False



				if line.find('DETD')==0:
					pick=True
					part = ''


	def Extract_claims(self):

		with open(self.path, 'r', encoding='utf-8') as f:
			claims = None
			pick=False
			start = True

			for line in f:

				if line.find('PATN')==0:
					if start:
						start = False
					else:
						break

				if pick:
					claims += line.replace('PAL  ','').replace('PAR  ','').replace('PAC  ','').replace('\n','')

				if line.find('CLMS')>=0:
					pick=True
					claims=''


		if claims is None:
			self.save=False
			print(" No CLAIMS")
		else:
			self.Dict["CLAIMS"]=clean_txt(claims)


	def patent_processing(self,save_directory):
		# DOC --> PATH TO .XML FILE
		# DIRECTORY --> WHERE TO SAVE RESULTS
		
		# Considered as no patent if no file name found in self.root
		
		# Dictionnary for all relevant textual information
		self.Dict = {}

		self.Extract_ref()

		self.Extract_inventors()

		self.Extract_invention_title()

		self.Extract_abstract()

		self.Extract_description()

		self.Extract_claims()
		

		###################################################################################################

		# Post processing / Extraction quality evaluation
		if (self.save):
			indic=False
			indic1=0
			indic2=0
			indic3=0


			# Look for particular titles to regroup the information
			for key in self.Dict.keys():
				
				
				if ((key.find('BACKGROUND')>=0
						or (key.find('DESCRIPTION OF THE RELATED ART')>=0) 
						or (key.find('DESCRIPTION OF RELATED ART')>=0) 
						or (key.find('PRIOR ART')>=0) 
						or (key.find('STATE OF THE ART')>=0) 
						or (key.find('DISCUSSION OF RELATED ART')>=0))
						 and indic==False):
					indic=True
					# self.STATE_OF_THE_ART=key
					self.Dict_final['STATE_OF_THE_ART'] = self.Dict[key]
					
				
				
				elif key.find('SUMMARY')>=0 and indic2==0:
					indic2=1
					# self.SUMMARY=key
					self.Dict_final['SUMMARY'] = self.Dict[key]


				elif key.find('FIELD')>=0 and indic1==0:
					indic1=1
					# self.FIELD_OF_INVENTION=key
					self.Dict_final['FIELD_OF_INVENTION'] = self.Dict[key]
					

			
				
				elif ((key.find('BRIEF DESCRIPTION')>=0)
						or (key.find('DESCRIPTION OF THE INVENTION')>=0)
						or (key.find('DESCRIPTION OF THE DISCLOSURE')>=0)
						or (key.find('DETAILED DESCRIPTION')>=0)
						or (key.find('DETAILED DISCLOSURE')>=0)
						or (key.find('BRIEF DISCLOSURE')>=0)
						or (key.find('DESCRIPTION')>=0 and key.find('EMBODIMENT')>=0)
						and indic3==0):
					indic3=1
					# self.DESCRIPTION=key
					self.Dict_final['DESCRIPTION'] = self.Dict[key]
					
						
			
			# 2 or more found among the State of art, field, summary and description ==> ok
			if(((indic1+indic2+indic3)==0) or not(indic)):
				self.save=False


	
###############################################################################################



