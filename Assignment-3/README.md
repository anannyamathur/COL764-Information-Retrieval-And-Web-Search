# ASSIGNMENT 3: Prior Ranking of Documents
## TOPICS COVERED:
- Computed a similarity graph between each pair of documents in the collection using a similarity function as mentioned
- On this similarity graph, computed the PageRank scores of all documents

## DATASET
We use a collection of newsgroup documents from about 20
different newsgroups. Some background about the dataset can be found at http://qwone.com/~jason/20Newsgroups/

## SIMILARITY COMPUTATION
- Term Overlap: 
Run ``simgraph_gen.sh jaccard [collection-directory] simgraph_jaccard``  
The result gets stored in a file named ``simgraph_jaccard``

- Tf-Idf Similarity: Run ``simgraph_gen.sh cosine [collection-directory] simgraph_cosine``  
The result gets stored in a file named ``simgraph_cosine``

## PageRank Scores Computation
- Install NetworkX using ``pip install networkx`` for computing the PageRank scores on the similarity graph
- To generate the scores, uncomment the commented lines in the code ``simgraph_gen.py``
