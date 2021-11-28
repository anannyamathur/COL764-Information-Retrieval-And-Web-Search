# ASSIGNMENT-2 : Document Reranking Task
## TOPICS COVERED:
- Pseudo-relevance Feedback with Rocchio’s method
- Relevance Model based Language Modeling: Using Lavrenko and Croft’s relevance models with an Unigram model with Dirichlet smoothing

## REQUIREMENTS:
- `pip install lxml`, `pip install bs4` to use beautifulsoup library of python for parsing xml files
- `pip install nltk`
- `pip install numpy`

## DATA COLLECTION
- This assignment has used the CORD19 data release from 16th July 2020. It is available for download from https://ai2-semanticscholar-cord-19.s3-us-west-2.
amazonaws.com/historical_releases/cord-19_2020-07-16.tar.gz. Metadata corresponding to all CORD ids is listed in a file called metadata.csv. The format and the description of this file is given at https://github.com/allenai/cord19/blob/master/
README.md
- Queries: We have considered only 40 topics from the TREC COVID19 track. Each topic, indexed by a topic number, consists of the following three fields: query, question, and
narrative. The field `query` was used in this assignment. 

## PROGRAM STRUCTURE
- `rocchio_rerank.py` conducts re-ranking of documents using Rocchio's method  
It can be called by `python rocchio_rerank.py [query-file] [top-100-file] [collection-file] [outputfile]`  or `/.rocchio rerank.sh [query-file] [top-100-file] [collection-file] [outputfile]`  

- `lm_rerank.py` conducts re-ranking of documents using language modelling  
It can be called by `python lm_rerank.py [rm1|rm2] [query-file] [top-100-file] [collection-dir]
[output-file] [expansions-file]` or `/. lm_rerank.sh [rm1|rm2] [query-file] [top-100-file] [collection-dir]
[output-file] [expansions-file]`, where  
  ```
 
  rocchio rerank: bash script file

  lm rerank: bash script file

  query-file: file containing the queries in the same xml form as the training queries released

  top-100-file: a file containing the top100 documents in the same format as train and dev top100 files given, which need to be reranked

  collection-dir: directory containing the full document collection. Specifically, it will have metadata.csv, a subdirectory named document parses which in turn contains subdirectories pdf json and pmc json.

  output-file: file to which the output in the trec eval format has to be written

  rm1|rm2: (only for LM) specifies if we are using RM1 or RM2 variant of relevance model.

  expansions-file: (only for LM) specifies the file to which the expansion terms used for each query should be output.

  Here, rm1 variant of LM refers to i.i.d. sampling and rm2 variant refers to conditional sampling.

## EVALUATION
- Link to TREC EVAL tool: https://trec.nist.gov/trec_eval/
