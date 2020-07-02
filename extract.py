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
from extraction.patent import Patent
from extraction.patent_txt import Patent_txt




class Extractor:


	def __init__(self, args):
		self.TARGET_FILE = args.target_file
		self.FINAL_DIR = args.final_dir
		self.FINAL_XML_DIR = args.final_xml_dir
		self.FINAL_TXT_DIR = args.final_txt_dir
		self.ready = False
		self.start_time=time.time()
	



	def Prepare_directories(self):
		# CREATE FILENAMES
		###############################################################################################
		self.FILENAME = os.path.basename(self.TARGET_FILE)

		if(self.TARGET_FILE.find('/')>=0):
			self.TARGET_DIR = "/".join(self.TARGET_FILE.split('/')[:-1])+"/"
		else:
			self.TARGET_DIR = os.getcwd()+"/"

		self.TEMP_DIR = self.TARGET_DIR+'temp'
		self.TARGET_UNTAR_FILE = self.FILENAME[:-4]
		###############################################################################################


		# CREATION RESULTS DIRECTORIES
		###############################################################################################
		for path in [self.FINAL_DIR,self.FINAL_DIR+'/'+self.FINAL_XML_DIR,self.FINAL_DIR+'/'+self.FINAL_TXT_DIR]:
			try:
				os.mkdir(path)
			except:
				continue
		###############################################################################################

		self.ready=True



	def XML_extraction(self):

		#Prepare _directories
		self.Prepare_directories()

		# UNZIPING/UNTAR AND .XML FILES EXTRACTION
		##############################################################################################

		if((self.FILENAME[0:3]=='ipa') | (self.FILENAME[0:3]=='ipg')):
			# IF FILE IS .ZIP

			# UNZIPPING
			print("\nUnzipping file...")

			zip_ref = ZipFile(self.TARGET_FILE,"r")
			zip_ref.extractall(self.TARGET_DIR+'/')


			# .XML EXTRACTION IN FINAL_XML_DIR
			print("\nExtracting patents...")

			with open(self.TARGET_DIR+self.FILENAME[:-4]+'.xml', 'r', encoding='utf-8') as f:
				#contents = f.read()

				current_file = ''

				for line in f:
					current_file += line

					if '<?xml version="1.0" encoding="UTF-8"?>' in line:
						current_file = line

					elif '</us-patent-application>' in line:
						root = ET.fromstringlist(current_file)
						if(root.get('file') is not None):
							f =  open(self.FINAL_DIR+'/'+self.FINAL_XML_DIR+'/'+root.get('file'), "w")
							f.write(current_file)

					elif '</us-patent-grant>' in line:
						root = ET.fromstringlist(current_file)
						if(root.get('file') is not None):
							f =  open(self.FINAL_DIR+'/'+self.FINAL_XML_DIR+'/'+root.get('file'), "w")
							f.write(current_file)

			# UNZIPPED FILE IS REMOVED
			os.remove(self.TARGET_DIR+self.FILENAME[:-4]+'.xml')
						

		elif ((self.TARGET_FILE[-4::]=='.tar') or (self.TARGET_FILE[-4::]=='.ZIP')):
			# IF FILE IS .TAR OR .ZIP

			# CREATION TEMPORARY FILE FOR UNZIPPING
			try:
				os.mkdir(self.TEMP_DIR)
			except:
				pass

			print("Extracting content...")
			if (self.TARGET_FILE[-4::]=='.tar'):
				# UNTAR
				tf = tarfile.open(self.TARGET_DIR+self.FILENAME)
				tf.extractall(self.TEMP_DIR)
			else:
				# UNZIP
				zip_ref = ZipFile(self.TARGET_DIR+self.FILENAME,"r")
				zip_ref.extractall(self.TEMP_DIR)

			# UNZIPPING ALL FILES
			print("Unzipping files...")
			count=0
			fichiers=[]
			for root, dirs, files in os.walk(self.TEMP_DIR+"/"+self.TARGET_UNTAR_FILE): 
				for i in files: 
					fichiers.append(os.path.join(root, i))

			for path in fichiers: 

				# Print % processed files
				#########################################################
				sys.stdout.write('\r')
				# the exact output you're looking for:
				j=(count+1)/len(fichiers)
				sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100*j))
				sys.stdout.flush()
				count+=1
				#########################################################

				if(path.find('.ZIP')>=0):
					zip_ref = ZipFile(path,"r")
					zip_ref.extractall(self.TEMP_DIR+'/Extracted_files')


			# .XML EXTRACTION IN self.FINAL_XML_DIR
			print("\nExtracting patents...")
			count=0
			fichiers=[]
			for root, dirs, files in os.walk(self.TEMP_DIR+'/Extracted_files'): 
				for i in files:
					fichiers.append(os.path.join(root, i))

			for path in fichiers: 

				# Print % extracted patents
				#########################################################
				sys.stdout.write('\r')
				# the exact output you're looking for:
				j=(count+1)/len(fichiers)
				sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100*j))
				sys.stdout.flush()
				count+=1
				#########################################################

				if(path.find(".XML")>=0):
					shutil.copy2(path,self.FINAL_DIR+'/'+self.FINAL_XML_DIR+'/')


			shutil.rmtree(self.TEMP_DIR)


		else:
			# IF NO ZIP OR NO TAR: ERROR
			print("I want .tar file or .xml file")

		##############################################################################################
			



	def Process_XML(self):

		if not(self.ready):
			self.Prepare_directories()

		# PROCESSING OF ALL .XML FILES IN FINAL_XML_DIR + SAVING EXTRACTED DICT IN FINAL_TXT_DIR
		###############################################################################################

		print("\nExtracting patents content")
		count=0
		self.list_fichiers = sorted(glob.glob(self.FINAL_DIR+'/'+self.FINAL_XML_DIR+'/*.XML'))
		self.list_problems=[]


		for file in self.list_fichiers:
			
			patent = Patent(file)
			patent.patent_processing(self.FINAL_DIR+'/'+self.FINAL_TXT_DIR)	

			#SAVE DICT

			if patent.save:

				target_dir=self.FINAL_DIR+'/'+self.FINAL_TXT_DIR+'/'+patent.Dict["REF PATENT"]
				try:
					os.mkdir(target_dir)
				except:
					pass

				for key in ["INVENTORS", "INVENTION_TITLE","ABSTRACT","CLAIMS"]:
					with open(target_dir+'/'+patent.Dict["REF PATENT"]+'.'+key, 'w') as fp:
						if(key=="INVENTORS"):
							comp=0
							for elt in patent.Dict[key]:
								if comp>0:
									fp.write(', '+elt)
								else:
									fp.write(elt)
								comp+=1	
						else:
							if isinstance(patent.Dict[key],list):
								fp.write(patent.Dict[key][0])
							else:
								fp.write(patent.Dict[key])

				for key in list(patent.Dict_final.keys()):
					with open(target_dir+'/'+patent.Dict["REF PATENT"]+'.'+key, 'w') as fp:
						if isinstance(patent.Dict_final[key],list):
							fp.write(patent.Dict_final[key][0])
						else:
							fp.write(patent.Dict_final[key])



			else:
				self.list_problems.append(file)

			# Print % extracted contents
			########################################################
			sys.stdout.write('\r')
			# the exact output you're looking for:
			j=(count+1)/len(self.list_fichiers)
			sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100*j))
			sys.stdout.flush()
			count+=1
			########################################################

		print("\n\nProcessing time",time.time()-self.start_time)
		print("\n", len(self.list_problems), " unprocessed files.")

		with open(self.FINAL_DIR+"/unprocessed_files.txt", "w") as file:
		    file.write(str(self.list_problems))









	def txt_extraction(self):

		#Prepare _directories
		self.Prepare_directories()

		# UNZIPING/UNTAR AND .XML FILES EXTRACTION
		##############################################################################################

		
		# UNZIPPING
		print("\nUnzipping file...")

		zip_ref = ZipFile(self.TARGET_FILE,"r")
		zip_ref.extractall(self.TARGET_DIR+'/')


		# .XML EXTRACTION IN FINAL_XML_DIR
		print("\nExtracting patents...")

		with open(self.TARGET_DIR+self.FILENAME[:-4]+'.txt', 'r', encoding='utf-8') as f:
			#contents = f.read()

			current_file = ''
			patent_number = None
			patent_date = None

			for line in f:
				current_file += line

				if line.find('WKU')==0 and patent_number is None:
					patent_number = line.replace('WKU','').replace(' ','').replace('\n','').replace('&','')

				if line.find('APD')==0 and patent_date is None:
					patent_date= line.replace('APD','').replace(' ','').replace('\n','')

				if line.find('PATN')==0 and patent_date is not None and patent_number is not None:
					f =  open(self.FINAL_DIR+'/'+self.FINAL_XML_DIR+'/US'+patent_number+'-'+patent_date, "w")
					f.write(current_file)
					current_file=line
					patent_number = None
					patent_date = None

			# UNZIPPED FILE IS REMOVED
			os.remove(self.TARGET_DIR+self.FILENAME[:-4]+'.txt')




	def Process_txt(self):

		if not(self.ready):
			self.Prepare_directories()

		# PROCESSING OF ALL .XML FILES IN FINAL_XML_DIR + SAVING EXTRACTED DICT IN FINAL_TXT_DIR
		###############################################################################################

		print("\nExtracting patents content")
		count=0
		self.list_fichiers = sorted(glob.glob(self.FINAL_DIR+'/'+self.FINAL_XML_DIR+'/*'))
		self.list_problems=[]


		for file in self.list_fichiers:
			
			patent = Patent_txt(file)
			patent.patent_processing(self.FINAL_DIR+'/'+self.FINAL_TXT_DIR)	

			#SAVE DICT

			if patent.save:

				target_dir=self.FINAL_DIR+'/'+self.FINAL_TXT_DIR+'/'+patent.Dict["REF PATENT"]
				try:
					os.mkdir(target_dir)
				except:
					pass

				for key in ["INVENTORS", "INVENTION_TITLE","ABSTRACT","CLAIMS"]:
					with open(target_dir+'/'+patent.Dict["REF PATENT"]+'.'+key, 'w') as fp:
						if(key=="INVENTORS"):
							comp=0
							for elt in patent.Dict[key]:
								if comp>0:
									fp.write(', '+elt)
								else:
									fp.write(elt)
								comp+=1	
						else:
							if isinstance(patent.Dict[key],list):
								fp.write(patent.Dict[key][0])
							else:
								fp.write(patent.Dict[key])

				for key in list(patent.Dict_final.keys()):
					with open(target_dir+'/'+patent.Dict["REF PATENT"]+'.'+key, 'w') as fp:
						if isinstance(patent.Dict_final[key],list):
							fp.write(patent.Dict_final[key][0])
						else:
							fp.write(patent.Dict_final[key])



			else:
				self.list_problems.append(file)

			# Print % extracted contents
			########################################################
			sys.stdout.write('\r')
			# the exact output you're looking for:
			j=(count+1)/len(self.list_fichiers)
			sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100*j))
			sys.stdout.flush()
			count+=1
			########################################################

		print("\n\nProcessing time",time.time()-self.start_time)
		print("\n", len(self.list_problems), " unprocessed files.")

		with open(self.FINAL_DIR+"/unprocessed_files.txt", "w") as file:
		    file.write(str(self.list_problems))


