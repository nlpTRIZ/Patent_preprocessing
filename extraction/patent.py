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
from extraction.utils import getTextFromTagNode,split,clean_txt




# THE MOST IMPORTANT: FROM .XML TEXTUAL INFORMATIONS EXTRACTION

class Patent:

	def __init__(self, doc):
		self.path=doc
		self.save= True
		self.root = ET.parse(self.path).getroot()
		self.Dict_final={}



	def Extract_ref(self):
	
		ref_patent=(re.sub(r"(.XML)",'',self.root.get('file')))
		#add to dict
		self.Dict["REF PATENT"]=ref_patent

		if(ref_patent==None):
			self.save=False
			print(" No REF PATENT")



	def Extract_inventors(self):

		try:
			inventors_xml = self.root.find(self.biblio+'/us-parties/inventors')
			if (inventors_xml==None):
				inventors_xml = self.root.find(self.biblio+'/parties/applicants')
			
			authors = []
			
			if(inventors_xml.findall('inventor')==[]):
				list_inventors = inventors_xml.findall('applicant')
			else:
				list_inventors = inventors_xml.findall('inventor')

			for inventor in list_inventors:
				try:
					last_name = inventor.find('addressbook/last-name').text
					first_name = inventor.find('addressbook/first-name').text
					authors.append(first_name+' '+last_name)
				except:
					pass

			#add to self.dict
			self.Dict["INVENTORS"]=authors

			if(authors==None):
				self.save=False
				print(" No AUTHORS")

		except:
			self.save=False
			print(" No AUTHORS")

	


	def Extract_invention_title(self):

		invention_title = self.root.find(self.biblio+'/invention-title').text
		# if(invention_title is not None):
		# 	print("INVENTION TITLE")

		#add to self.dict
		self.Dict["INVENTION_TITLE"]=invention_title

		if(invention_title==None):
			self.save=False
			print(" No INVENTION TITLE")




	def Extract_abstract(self):

		try:
			abstract = self.root.find('abstract').getchildren()
			# if(abstract!=[]):
			# 	print("ABSTRACT")

			Abstract=""
			for elt in abstract:
				Abstract += getTextFromTagNode(elt)

			
			#add to self.dict
			self.Dict["ABSTRACT"]=clean_txt(re.sub(r"(\n)",' ',Abstract))

		except:
			self.save=False
			print(" No ABSTRACT")





	def Extract_description(self):

		#print("DESCRIPTION")
		description = self.root.find('description').getchildren()
		#print(" ",len(description), "paragraphs in the description")
		iterator_titles = iter(self.root.find('description').findall('heading'))

		if(self.root.find('description').findall('heading')!=[]):
			title = next(iterator_titles).text
			#print(" ",len(self.root.find('description').findall('heading')), "headings")
		else:
			title=""
		title_ancient=title

		i=1
		Text=""
		headings=[]

		try:
			for elt in description:
				
				if(elt.findall('heading')!=[]):
					#print("    ",len(elt.findall('heading')),"sub-headings")
					for head in elt.findall('heading'):
						headings.append(head.text)

				if((getTextFromTagNode(elt).rstrip('\n')==title)|(i==len(description))):
					if((i!=len(description))):
						pass
						#print(" ",title.upper())
					else:
						Text += re.sub('\n',' ',getTextFromTagNode(elt).rstrip('\n'))
					if(Text!=""):
						if(len(headings)>0):
							part_list = [clean_txt(part) for part in split(re.sub(r"(\n)",' ',Text),headings)]
							self.Dict[title_ancient.upper()]= part_list
							headings=[]

						else:
							self.Dict[title_ancient.upper()]=clean_txt(Text)

					Text= ""
					title_ancient = title
					try:
						title = next(iterator_titles).text
						
					except:
						pass

				else:
					Text += re.sub('\n',' ',getTextFromTagNode(elt).rstrip('\n'))


				i+=1
		except:
			self.save=False
			print(" No proper DESCRIPTION")
			



	def Extract_claims(self):

		try:
			claims = self.root.find('claims').getchildren()
			# if(claims!=[]):
			# 	print("CLAIMS")

			Text=""
			for claim in claims:
				Text += getTextFromTagNode(claim)

			self.Dict["CLAIMS"]=clean_txt(re.sub(r"(\n)",' ',Text))

		except:
			self.save=False
			print(" No CLAIMS")




	def patent_processing(self,save_directory):
		# DOC --> PATH TO .XML FILE
		# DIRECTORY --> WHERE TO SAVE RESULTS
		
		# Considered as no patent if no file name found in self.root
		if(self.root.get('file')==None):
			# list_problems.append(doc)
			print(" No PatentName")

		else:

			# Dictionnary for all relevant textual information
			self.Dict = {}
			if(self.root.find('us-bibliographic-data-grant')==None):
				self.biblio = 'us-bibliographic-data-application'
			else:
				self.biblio = 'us-bibliographic-data-grant'
			
			
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
						

				
					
					elif ((key.find('BRIEF DESCRIPTION')>=0
							or key.find('DESCRIPTION OF THE INVENTION')>=0
							or key.find('DESCRIPTION OF THE DISCLOSURE')>=0
							or key.find('DETAILED DESCRIPTION')>=0
							or key.find('DETAILED DISCLOSURE')>=0
							or key.find('BRIEF DISCLOSURE')>=0
							or key.find('DESCRIPTION OF EMBODIMENT')>=0
							or key.find('DESCRIPTION OF PREFERRED EMBODIMENT')>=0
							or key.find('DESCRIPTION OF THE PREFERRED EMBODIMENT')>=0)
							and indic3==0):
						indic3=1
						# self.DESCRIPTION=key
						self.Dict_final['DESCRIPTION'] = self.Dict[key]
						
							
				
				# 2 or more found among the State of art, field, summary and description ==> ok
				if(((indic1+indic2+indic3)<2) or not(indic)):
					self.save=False


	
###############################################################################################



