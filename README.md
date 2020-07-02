# Data extraction from patents


The script takes the raw compressed patents archives as input and may be used simply with:
```bash
python3 main.py -task Extraction -target_file path_to_compressed_file
```
_For example:_

```bash
python3 main.py -task Extraction -target_file './data/Downloaded_data/ipg070102.zip'
```


<p>&nbsp;</p>

**The results are stored into ```./data/Extraction_results```. It will contain 2 sub-directories and a .txt file.**

* The .txt file is the list of unprocessed files contained in the original patents archive.

* **Extracted_patents** contains all the .XML/txt patents found in the archive.

* **Extracted_parts_patents** contains one directory per patent with the several parts of the patent (summary, state of the art, abstract...) in .txt files.

<p>&nbsp;</p>
<p>&nbsp;</p>

# Data preprocessing


The script takes the user's database (test/train/valid dataset) as input. These data must be placed into ```./data/Dataset/train```, ```./data/Dataset/test``` and ```./data/Dataset/valid```. 
A file called **_ref-patent_.SUM** containing the chosen sentences for the summary must be placed in each patent directory along with .txt files of the other parts (abstract, summary...).

The script may be simply used with:
```bash
python3 main.py -task Preprocessing
```
To process only test data for example you can use the -dataset option:
```bash
python3 main.py -task Preprocessing -dataset 'test'
```
To process only particular parts of the patent you can use the -parts_of_interest option:
```bash
python3 main.py -task Preprocessing -dataset 'test' -parts_of_interest 'STATE_OF_THE_ART'
```
To add a data augmentation process through a double translation you can use the -translate option:
```bash
python3 main.py -task Preprocessing -dataset 'test' -parts_of_interest 'STATE_OF_THE_ART' -translate True
```
<p>&nbsp;</p>

**The results are stored into ```./data/Preprocessing_results```. It will contain 2 sub-directories.**

* **Preprocessing_results_init** contains the preprocessing results. The source texts and the summaries are saved together in big files.

* **Preprocessing_results_bert** contains the preprocessing results adapted for a use with BERT model

<p>&nbsp;</p>
<p>&nbsp;</p>

## StanfordCoreNLP tokenizer

To use **StanfordCoreNLP tokenizer** you must set an env var pointing towards stanford-corenlp-3.9.2.jar:

```bash
export CLASSPATH=path_to/stanford-corenlp-full-2018-10-05/stanford-corenlp-3.9.2.jar
```
_For example:_

```bash
export CLASSPATH=/media/guillaume/Stockage/Pytorch_files/Preprocessing/stanford-corenlp-full-2018-10-05/stanford-corenlp-3.9.2.jar
```
