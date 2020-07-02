import argparse
import time
import os

from extract import Extractor
from preprocess import Preprocessor
from preprocessing.preprocess_init import str2bool
from others.logging import init_logger


os.environ["CLASSPATH"] = "./stanford-corenlp-full-2018-10-05/stanford-corenlp-3.9.2.jar"



if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    # Choose between:
    # - 'Extraction' = patents extraction from compressed files
    # - 'Preprocessing_bert' = patents preprocessing for BERT use
    parser.add_argument('-task', type=str, default='Extraction')

    # Extraction parameters
    parser.add_argument('-target_file', type=str, default='./data/Downloaded_data/ipg090609.zip')
    parser.add_argument('-final_dir', type=str, default='./data/Extraction_results')
    parser.add_argument('-final_txt_dir', type=str, default='Extracted_parts_patents')
    parser.add_argument('-final_xml_dir', type=str, default='Extracted_patents')

    # Preprocessing parameters
    parser.add_argument('-data_augmentation', type=str, default="None", help='"None", translation" or "transformation"')
    parser.add_argument('-translation_language', type=str, default="ca", help='korean:"ko", chinese:"zh-TW", catalan:"ca"')
    parser.add_argument('-transformation_type', type=str, default="bert_embeddings", help='"bert_embeddings", "word2vec_embeddings" or "synonyms"')

    parser.add_argument('-dataset_dir', type=str, default='./data/Dataset')
    parser.add_argument('-dataset', type=str, default='', help='train, valid or test, default will process all datasets')
    parser.add_argument("-save_path_dir", type=str, default='./data/Preprocessing_results')
    parser.add_argument("-save_path_prepro", type=str, default='./data/Preprocessing_results/Preprocessing_results_init')
    parser.add_argument("-save_path_nn", type=str, default='./data/Preprocessing_results/Preprocessing_results_')
    
    # Summaries parameters
    parser.add_argument('-summary_size', type=int, default=5, help='size of the output summary')
    parser.add_argument('-adaptive_summary', type=str, default='both', help='which part of the contradiction will be used in the summary: "first","second", or "both')
    parser.add_argument('-parts_of_interest', help='delimited list input', type=str, default='ABSTRACT,STATE_OF_THE_ART,SUMMARY,FIELD_OF_INVENTION,CLAIMS,DESCRIPTION,SUMM')
    parser.add_argument("-oracle_mode", default='greedy', type=str, help='how to generate oracle summaries, greedy or combination, combination will generate more accurate oracles but take much longer time.')

    # Model parameters
    parser.add_argument('-model', type=str, default='bert')
    parser.add_argument('-min_src_nsents', default=1, type=int)
    parser.add_argument('-max_src_nsents', default=60, type=int)
    parser.add_argument('-min_src_ntokens_per_sent', default=5, type=int)
    parser.add_argument('-max_src_ntokens_per_sent', default=200, type=int)
    parser.add_argument('-max_tgt_ntokens', default=1000, type=int)
    parser.add_argument('-min_tgt_ntokens', default=1, type=int)
    parser.add_argument('-use_bert_basic_tokenizer', default=True, type=str)


    parser.add_argument('-log_file', type=str, default='./logs/patent.log')
    parser.add_argument('-n_cpus', default=1, type=int)


    args = parser.parse_args()
    init_logger(args.log_file)
    



    if args.task == 'Extraction':

        # DATA EXTRACTION
        begin = time.time()

        if args.target_file.find('pftaps')>=0:
            Extracteur = Extractor(args)
            Extracteur.txt_extraction()
            Extracteur.Process_txt()
        else:
            Extracteur = Extractor(args)
            Extracteur.XML_extraction()
            Extracteur.Process_XML()

        end_operation = time.time()
        print('\n\nDuration extraction = %d seconds.' %(end_operation-begin))

    else:

        # PREPROCESSING
        begin = time.time()

        Preprocesseur=Preprocessor(args)
        Preprocesseur.tokenize()
        Preprocesseur.format_to_lines()
        Preprocessor.format_to_nn(args)

        end_operation = time.time()
        print('Duration preprocessing = %d seconds.' %(end_operation-begin))




