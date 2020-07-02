import glob
import json
import os
import time
import subprocess
from os.path import join as pjoin
import re
import sys
import shutil
import random

#Data augmentation
#####
# from google.cloud import translate_v2 as translate
# # Instantiates a client
# translate_client = translate.Client()
import nlpaug.augmenter.word as naw
#####

from multiprocessing import Pool
from preprocessing.preprocess_init import *
from preprocessing.preprocess_nn import *
from others.data_analysis import *



class Preprocessor:

    def __init__(self,args):

        # self.data_path : with which dataset to proceed (none = all)
        # self.temp_path : temporary directory to store output of Stanford nlp tokenizer
        # self.save_path_prepro : path to save preprocessing results
        # self.n_cpus : number cpus
        # self.parts_of_interest : which parts of the patents must be preprocessed
        # self.adaptive_summary : which sentences/parameters are put into the TRIZ summary

        if args.dataset != '':
            self.data_path=[args.dataset_dir+'/'+args.dataset]
        else:
            self.data_path = [args.dataset_dir+'/'+dataset for dataset in ['train','test','valid']]

        self.temp_path=args.dataset_dir + '/TEMP'
        self.save_path_prepro=args.save_path_prepro
        self.n_cpus=args.n_cpus
        self.parts_of_interest = [str(item) for item in args.parts_of_interest.split(',')]
        self.adaptive_summary = args.adaptive_summary
        self.data_augmentation = args.data_augmentation
        self.translation_language = args.translation_language
        self.transformation_type = args.transformation_type

        # Creation of all needed directories 
        for path in [args.dataset_dir,args.dataset_dir+'/train',args.dataset_dir+'/test',args.dataset_dir+'/valid',args.save_path_dir,args.save_path_nn+args.model,self.save_path_prepro,self.temp_path]:
            try:
                os.mkdir(path)
            except:
                continue




    def tokenize(self):

        # This method rewrite the TRIZ summary in accordance with the will of the user (only one part of the contradiction in the summary or both parts)
        # It also rewrites every part involved to add spaces between sentences and avoid problems during tokenization
        # Finally it tokenizes text+summary using Stanford Core NLP. The results are saved 
       

        for path in self.data_path:
            corpus_type = path.split('/')[-1]
            

            # Data augmentation with double translation
            # Add spaces between sentences in all used texts including summaries to avoid problems during tokenization
            #########################################################################################################################
            

            for tipe in self.parts_of_interest+["SUM"]:

                if self.data_augmentation != "None" and corpus_type=='train':
                    print("\n"+corpus_type +" set: Data augmentation in progress for "+tipe+" parts...")
                else:
                    print("\n"+corpus_type +" set: Sentences verification for "+tipe+" parts...")

                files=sorted(glob.glob(path+'/*/*.'+tipe))
                count=0
                
                for file in files:

                    with open(file, "r", encoding='utf-8') as f:
                        print(file)
                        
                        # Add spaces between sentences
                        if tipe != "SUM":
                            data = f.read()
                            data = data.replace(".",". ")
                            data = ' '.join(data.split())
                            with open(file,'w') as f:
                                f.write(data)
                        else:
                            data=''
                            for sentence in f:
                                if sentence.find("STATE_OF_THE_ART")>=0:
                                    continue
                                else:
                                    data+= sentence

                            param_sents = data.split("///")
                            first_param_sents = param_sents[0].replace("\n","").split("//")
                            if len(param_sents)>1:
                                second_param_sents = param_sents[1].replace("\n","").split("//")
                            else:
                                second_param_sents=[]



                    # Data augmentation with double translation
                    if self.data_augmentation != "None" and corpus_type=='train':


                        if self.data_augmentation=="transformation" and self.transformation_type=="bert_embeddings":
                            aug = naw.ContextualWordEmbsAug(model_path='bert-base-uncased', action="substitute")
                        elif self.data_augmentation=="transformation" and self.transformation_type=="word2vec_embeddings":
                            aug = naw.WordEmbsAug(model_type='word2vec', model_path='./word2vec/GoogleNews-vectors-negative300.bin')
                        elif self.data_augmentation=="transformation" and self.transformation_type=="synonyms":
                            aug = naw.SynonymAug()
                            
                        print("ok")

                            # Print % processed files
                        #########################################################
                        sys.stdout.write('\r')
                        # the exact output you're looking for:
                        j=(count+1)/len(files)
                        sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100*j))
                        sys.stdout.flush()
                        count+=1
                        #########################################################

                        path_augmented_text = file.split('/')
                        path_augmented_text[4]+='b'
                        path_augmented_text[5]='.'.join([path_augmented_text[4],path_augmented_text[5].split('.')[-1]])
                        path_new_directory = '/'.join(path_augmented_text[:-1])
                        path_augmented_text='/'.join(path_augmented_text)

                        if os.path.isfile(path_augmented_text) or file.find('b')>0:
                            continue

                        if self.data_augmentation=="translation":
                            # Not to exceed google translations quotas
                            time.sleep(1.25)

                        augmented_text =''
                        if tipe != "SUM":
                            for sentence in data.split('.'):
                                if self.data_augmentation=="translation":
                                    augmented_text += translate_client.translate(translate_client.translate(sentence+'.',target_language=self.translation_language)['translatedText'].replace("&#39;","'").replace("."," ")+'.',target_language='en')['translatedText'].replace("&#39;","'").replace("."," ")+'.'
                                elif self.data_augmentation=="transformation":
                                    augmented_text += aug.augment(sentence+'.').replace("."," ")+'.'
                                    print("ok2")
                        else:
                            for sentence in first_param_sents:
                                if self.data_augmentation=="translation":
                                    augmented_text += translate_client.translate(translate_client.translate(sentence+'.',target_language=self.translation_language)['translatedText'].replace("&#39;","'").replace("."," ")+'.',target_language='en')['translatedText'].replace("&#39;","'").replace("."," ")+'. //'
                                elif self.data_augmentation=="transformation":
                                    augmented_text += aug.augment(sentence+'.').replace("."," ")+'. //'
                                    print("ok3")
                            augmented_text +='/'
                            for sentence in second_param_sents:
                                if self.data_augmentation=="translation":
                                    augmented_text += translate_client.translate(translate_client.translate(sentence+'.',target_language=self.translation_language)['translatedText'].replace("&#39;","'").replace("."," ")+'.',target_language='en')['translatedText'].replace("&#39;","'").replace("."," ")+'. //'
                                elif self.data_augmentation=="transformation":
                                    augmented_text += aug.augment(sentence+'.').replace("."," ")+'. //'
                                    print("ok4")
                            augmented_text = augmented_text[:-3]


                        augmented_text = augmented_text.replace(".",". ")
                        augmented_text = ' '.join(augmented_text.split())


                        # Write translation
                        try:
                            os.mkdir(path_new_directory)
                        except:
                            pass

                        with open(path_augmented_text,'w') as f:
                            f.write(augmented_text[:-1])


            #########################################################################################################################
            # Rewriting of summaries with chosen sentences/parameters (one side of the contradiction or both)
            #########################################################################################################################""
            try:
                data_analyzer= summary_preparation(path+'/')
                (path_state_of_the_art,summary) = data_analyzer.get_data(self.adaptive_summary)
                for num in range (0,len(summary[0])):
                    summary_patent = ''
                    for x in range(0,len(summary[0][num])):
                        summary_patent += (summary[0][num][x]+' ')
                    if (len(summary)==2):
                        for x in range(0,len(summary[1][num])):
                            summary_patent += (summary[1][num][x]+' ') 
                    
                    with open(path_state_of_the_art[num][0:-16]+'SUMTRIZ', "w") as file:
                        file.write(summary_patent)
               
            except:
                print("No summaries provided for "+corpus_type+' files.')
                time.sleep(1)
            #########################################################################################################################""


            # Tokenization using Standford Core NLP
            #########################################################################################################################
            for tipe in self.parts_of_interest+["SUMTRIZ"]:
                print("\n\n\nTokenization in progress...")
                files=sorted(glob.glob(path+'/*/*.'+tipe))
                print(str(len(files))+" "+tipe+" found for "+corpus_type+" set.")

                extracted_patents_dir = os.path.abspath(path)
                tokenized_patents_dir = os.path.abspath(self.temp_path+'/'+corpus_type+'/'+tipe)
             
                print("Preparing to tokenize %s to %s..." % (extracted_patents_dir, tokenized_patents_dir))
                stories = os.listdir(extracted_patents_dir)
                # make IO list file
                print("Making list of files to tokenize...")
                with open("mapping_for_corenlp.txt", "w") as f:
                    for s in files:
                        f.write("%s\n" % (s))
                command = ['java', 'edu.stanford.nlp.pipeline.StanfordCoreNLP', '-annotators', 'tokenize,ssplit',
                           '-ssplit.newlineIsSentenceBreak', 'always', '-filelist', 'mapping_for_corenlp.txt', '-outputFormat',
                           'json', '-outputDirectory', tokenized_patents_dir]
                print("Tokenizing %i files in %s and saving in %s..." % (len(stories), extracted_patents_dir, tokenized_patents_dir))
                subprocess.call(command)
                
                os.remove("mapping_for_corenlp.txt")

            #########################################################################################################################

        print("Stanford CoreNLP Tokenizer has finished.")
        print("Successfully finished tokenizing %s to %s.\n" % (extracted_patents_dir, tokenized_patents_dir))




    
    def format_to_lines(self):

        # This method rewrites the output of Stanford Core NLP tokenizer into a single file with several source texts and their summaries

        print("\nJSON files simplification...")
       
        for corpus_type in ['train','test','valid']:

            files=[]
            for tipe in self.parts_of_interest:
                files=sorted(glob.glob(self.temp_path+'/'+corpus_type+'/'+tipe+'/*'+'json'))
                summaries = sorted(glob.glob(self.temp_path+'/'+corpus_type+'/'+'SUMTRIZ'+'/*'+'json'))
                
                # Shuffle files list
                random.seed(1)
                random.shuffle(files)

                # Shuffle summaries list with same seed
                random.seed(1)
                random.shuffle(summaries)


                print("\n"+str(len(files))+" "+tipe+" found for "+corpus_type+" set.")
                    
                # creation iterator for data
                a_lst = [(f) for f in files]
                s_lst = [(summary) for summary in summaries]
                gen_data = zip(a_lst,s_lst)

                pool = Pool(self.n_cpus)
                dataset = []
                p_ct = 0
                count=0

                for d in pool.imap_unordered(format_to_lines_, gen_data):
                    dataset.append(d)
                    if (len(dataset) > 49):
                        pt_file = "{:s}.{:s}.{:d}.json".format(self.save_path_prepro+'/'+tipe, corpus_type, p_ct)
                        with open(pt_file, 'w') as save:
                            # save.write('\n'.join(dataset))
                            save.write(json.dumps(dataset))
                            p_ct += 1
                            dataset = []

                    # Print % processed files
                    #########################################################
                    sys.stdout.write('\r')
                    # the exact output you're looking for:
                    j=(count+1)/len(files)
                    sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100*j))
                    sys.stdout.flush()
                    count+=1
                    #########################################################


                pool.close()
                pool.join()
                if (len(dataset) > 0):
                    pt_file = "{:s}.{:s}.{:d}.json".format(self.save_path_prepro+'/'+tipe, corpus_type, p_ct)
                    with open(pt_file, 'w') as save:
                        # save.write('\n'.join(dataset))
                        save.write(json.dumps(dataset))
                        p_ct += 1
                        dataset = []

        shutil.rmtree(self.temp_path)
        print('\n')

        


    def format_to_nn(args):

        # This method formats the preprocessed files by format_to_lines into files usable with a nn algorithm

        if (args.dataset != ''):
            datasets = [args.dataset]
        else:
            datasets = ['train', 'valid', 'test']

        for corpus_type in datasets:

            if args.model == 'bert':
                a_lst = []
                for json_f in sorted(glob.glob(pjoin(args.save_path_prepro, '*' + corpus_type + '.*.json'))):
                    real_name = json_f.split('/')[-1]
                    a_lst.append((json_f, args, pjoin(args.save_path_nn+args.model, real_name.replace('json', args.model+'.pt'))))

                
                pool = Pool(args.n_cpus)

                for d in pool.imap(format_to_bert_, a_lst):
                    pass

                pool.close()
                pool.join()

            elif args.model == 'neusum':
                src_path = pjoin(args.save_path_nn+args.model,'text_'+corpus_type+'.src.txt')
                tgt_path = pjoin(args.save_path_nn+args.model,'text_'+corpus_type+'.tgt.txt')

                writer_src = open(src_path, 'w', encoding='utf-8')
                writer_tgt = open(tgt_path, 'w', encoding='utf-8')

                for json_f in sorted(glob.glob(pjoin(args.save_path_prepro, '*' + corpus_type + '.*.json'))):
                    src,tgt = format_to_neusum(json_f)
                    writer_src.write(src)
                    writer_tgt.write(tgt)

                writer_src.close()
                writer_tgt.close()

                 # Verification if some labels are empty (2nd part of contradiction)
                ############################################################################################################################
                src=''
                tgt=''

                with open(src_path, 'r', encoding='utf-8') as src_reader, \
                    open(tgt_path, 'r', encoding='utf-8') as tgt_reader:
                        for src_line, tgt_line in zip(src_reader, tgt_reader):
                            if tgt_line !='\n':
                                tgt+=tgt_line
                                src+=src_line
                src_writer = open(src_path, 'w', encoding='utf-8')
                tgt_writer = open(tgt_path, 'w', encoding='utf-8')
                src_writer.write(src)
                tgt_writer.write(tgt)
                src_writer.close()
                tgt_writer.close()
                ############################################################################################################################

                # Oracle computation
                oracle_path = pjoin(args.save_path_nn+args.model,corpus_type+'.rouge_bigram_F1.oracle')
                oracle_rouge_path = pjoin(args.save_path_nn+args.model,corpus_type+'rouge_bigram_F1.oracle.regGain')

                print('\n'+corpus_type+' set: Oracle predictions...')
                find_oracle(src_path,tgt_path,oracle_path,50,100000)

                print(corpus_type+' set: Regression gains computation...\n')
                get_regression_gain(src_path, tgt_path, oracle_path, oracle_rouge_path)



            


