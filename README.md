# SEMANTIC ROLE LABELING BR
Semantic Role Labeling is a task within the domain of natural language processing, that attempts to answer
who, did what, to whom given a sentence. This repository is a partial implementation of a masters dissertation,
(BELTRAO, 2016) that uses Propbank Br v1.1 as the golden set, Liblinear implemention for Support Vector Machines 
for multiclass classfication, Official Conll 2005 Shared Task scrips for evaluation and three sets of feature
enginnering.


## A Golden Set Example:

| **ID** | **FORM** | **LEMMA**|**GPOS**| **MORPH**   | **DTREE** | **FUNC** | **CTREE** | **PRED** | **ARG**   |
|--------|----------|----------|--------|-------------|-----------|----------|-----------|----------|-----------|
| 1      | A        | o        | art    | F\|S        | 2         | >N       | (FCL(NP*  | -        | *         |
| 2      | série    | série    | n      | F\|S        | 8         | SUBJ     | *         | -        | (A1*)     |
| 3      | exibida  | exibir   | v-pcp  | F\|S        | 2         | N<       | (ICL(VP*) | -        | *         |
| 4      | aqui     | aqui     | adv    | -           | 3         | ADVL     | (ADVP*)   | -        | *         |
| 5      | por      | por      | prp    | -           | 3         | PASS     | (PP*      | -        | *         |
| 6      | a        | o        | art    | F\|S        | 7         | >N       | (NP*      | -        | *         |
| 7      | Cultura  | cultura  | n      | F\|S        | 5         | P<       | *)))      | -        | *         |
| 8      | estreiou | estrear  | v-fin  | PS\|3S\|IND | 0         | STA      | (VP*)     | estreiar | *         |
| 9      | em       | em       | prp    | -           | 8         | ADVL     | (PP*      | -        | (AM-LOC*) |
| 10     | a        | o        | art    | F\|S        | 11        | >N       | (NP*      | -        | *         |
| 11     | TVI      | TVI      | prop   | F\|S        | 9         | P<       | *         | -        | *         |
| 12     | de       | de       | prp    | _           | 11        | N<       | (PP*      | -        | *         |
| 13     | Portugal | Portugal | prop   | M\|S        | 12        | P<       | (NP*))))  | _        | *         |
| 14     | .        | .        | pu     | -           | 8         | PUC      | *)        | -        | *         |

## The Golden Set Features:

| **Num** | **Name** | **Description**                                                                                     |
|---------|----------|-----------------------------------------------------------------------------------------------------|
| 1       | **ID**   | Counter of tokens that begins at 1 for each new proposition.                                        |
| 2       | **FORM** | Tokenized word or punctuation sign.                                                                 |
| 3       | **LEMMA**| Lemma _gold-standard_ for *FORM*.                                                                   |
| 4       | **GPOS** | Post tagging _gold-standard_ for *FORM*.                                                            |
| 5       | **MORPH**| Morphological features _gold-standard_.                                                             |
| 6       | **DTREE**| Dependency tree _gold-standard_.                                                                    |
| 7       | **FUNC** | Syntactic function of the _token_ for your regent in dependency tree.                               |
| 8       | **CTREE**| Syntactic tree _gold-standard_.                                                                     |
| 9       | **PRED** | Semantic Predicates on preposition.                                                                 |
| 10      | **ARG**  | Semantic role label for the regent of the argument on *DTREE*   according to PropBank annotations.  |

## Sematic Role Labels
|   **Tag**   | **Description**                          |
|:-----------:|------------------------------------------|
|    **A0**   | Usually the agent (actor).               |
|    **A1**   | Usually the patient or theme (receiver). |
| **A2...A5** | Verb oriented tags.                      |
|  **AM-ADV** | Modifier adverb.                         |
|  **AM-CAU** | Cause.                                   |
|  **AM-DIR** | Direction.                               |
|  **AM-DIS** | Discursive.                              |
|  **AM-EXT** | Extension.                               |
|  **AM-MED** | Non documented tag.                      |
|  **AM-LOC** | Location.                                |
|  **AM-MNR** | Manner.                                  |
|  **AM-NEG** | Negation.                                |
|  **AM-PNC** | Purpose.                                 |
|  **AM-PRD** | Secondary predication.                   |
|  **AM-REC** | Reciprocal.                              |
|  **AM-TMP** | Temporal.                                |

## FEATURE ENGINEERING (BELTRAO, 2016)
  There are 5 groups of features described on the dissertation, 4 of which are implemented as follows:

### Golden Standard Features
  All golden standard features except **ARG**.

| **Attribute** | **Description**                                                       |
|---------------|-----------------------------------------------------------------------|
| **FORM**      | **FORM** Tokenized word or punctuation sign.                          |
| **LEMMA**     | Lemma _gold-standard_ for **FORM**.                                   |
| **GPOS**      | Post tagging _gold-standard_ for **FORM**.                            |
| **MORPH**     | Morphological features _gold-standard_.                               |
| **FUNC**      | Syntactic function of the _token_ for your regent in dependency tree. |

### Window Features
  Lead and lag features around the token.

| **Attribute**             | **Description**                             |
|---------------------------|---------------------------------------------|
| **LeftForm 1,2, and 3**   | **FORM** from the 3 _tokens_ to the left.   |
| **RightForm 1,2 and 3**   | **FORM** from the 3 _tokens_ to the right.  |
| **LeftFunc 1,2 and 3**    | **FUNC** from the 3 _tokens_ to the left.   |
| **RightFunc 1,2 and 3**   | **FUNC** from the 3 _tokens_ to the right.  |
| **LeftLemma 1,2 and 3**   | **LEMMA** from the 3 _tokens_ to the left.  |
| **RightLemma 1,2, and 3** | **LEMMA** from the 3 _tokens_ to the right. |
| **LeftGPOS 1,2 and 3**    | **GPOS** from the 3 _tokens_ to the left.   |
| **RightGPOS 1,2 and 3**   | **GPOS** from the 3 _tokens_ to the right.  |    

### Context Features
  Lead and lag features around predicate.

| **Attribute**         | **Description**                                                                                                                                                 |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **PredLemma**         | **LEMMA** of target verb                                                                                                                                        |
| **PredLeftLemma**     | **LEMMA** of _token_ to the left of target verb.                                                                                                                |
| **PredRightLemma**    | **LEMMA** of _token_ to the right of the target verb.                                                                                                           |
| **PredGPOS**          | **GPOS** of target verb.                                                                                                                                        |
| **PredLeftGPOS**      | **GPOS** of _token_ to the left of target verb.                                                                                                                 |
| **PredRightGPOS**     | **GPOS** of _token_ to the right of target verb.                                                                                                                |
| **PredFunc**          | **FUNC** of target verb.                                                                                                                                        |
| **PredLeftFunc**      | **FUNC** of the _token_ to the left of the verb.                                                                                                                |
| **PredRightFunc**     | **FUNC** of the _token_ to the right of the verb.                                                                                                               |
| **PredicateDistance** | **ID** of the target verb minus **ID** of current _token_.                                                                                                      |
| **PredMorph 1..n**    | Set of 32 **MORPH** for target verb.                                                                                                                            |
| **PassiveVoice**      | Passive voice indicator. True if verb has **GPOS**=v-pcp and is   proceeded for _token_ with **LEMMA**=ser having or not _token_with **GPOS**=adv between them. |
| **PosRelVerb**        | If _token_ is before or after verb.                                                                                                                             |

### Dependency Tree Features
  Token depentencies and path to predicate.

| **Atribute**                 | **Description**                                                                               |
|------------------------------|-----------------------------------------------------------------------------------------------|
| **DepLemmaParent**           | **LEMMA** from the father of the _token_.                                                     |
| **DepLemmaGrandparent**      | **LEMMA** from the grandfather of the _token_.                                                |
| **DepLemmaChild 1, 2 and 3** | **LEMMA** from the 3 first children of the _token_.                                           |
| **DepGPOSParent**            | **GPOS** from the father of the _token_.                                                      |
| **DepGPOSGrandParent**       | **GPOS** from the grandfather of the _token_.                                                 |
| **DepGPOSChild 1, 2 and 3**  | **GPOS** from the 3 first children of the _token_.                                            |
| **DepFuncParent**            | **FUNC** from the father of the _token_.                                                      |
| **DepFuncGrandParent**       | **FUNC** from the grandfather of the _token_.                                                 |
| **DepFuncChild 1, 2 and 3**  | **FUNC** from the 3 first children of the _token_.                                            |
| **DepPathFunc**              | Path of **FUNC** tags between _token_ and target verb passing through minor common ancestor.  |
| **DepPathGPOS**              |  Path of **GPOS** tags between _token_ and target verb passing through minor common ancestor. |

## Project
The following defines the current project structure tree:

```
- srlbr/
    - datasets_1.1/
        - conll/
        - csvs/
        - props/
    - models/
        - lib/
        - __init__.py
        - evaluator.py
        - feature_factory.py
        - svm.py 
        - utils.py        
    - srlconll-1.1/
    - requirements.txt
    - README.md
    - srl.py        
    - .gitignore
```
### datasets_1.1/conll/
  Formatted Train, test and validation _gold-standard_ in a format suitable for machine learning models. Originals can be found [here.](http://www.nilc.icmc.usp.br/portlex/index.php/en/projects/propbankbringl)

### datasets_1.1/csvs/
  Stored feature columns.

### datasets_1.1/props/
  _gold-standard_ propositions which are evaluated by conll script.

### models/lib/
  Liblinear executables and python liblinear.py and liblinearutil.py

### models/\_\_init\_\_.py
  Exports svm_srl function

### models/evaluator.py
  Thin wrapper for the conll script uses subprocess and runs the official script.

### models/feature_factory.py
  Here the features are engineered

### models/svm.py
  Wrapper of liblinear calls on liblinear lib and main function svm_srl.

### models/utils.py
  Handles storing.

### models/srlconll-1.1/
  Official Conll 2005 Shared Task [Pearl script](http://www.lsi.upc.edu/~srlconll/soft.html) 

### requirements.txt
  Python project requirements.

### srl.py
  Command line callable script to run the script

## SETUP
### Python

        > pip install -r requirements.txt

### Pearl
 Conll 2005 shared task uses Pearl 5. Chances are that is already installed.

        > perl -v
 
 Set the PERL5LIB environment variable.

        > setenv PERL5LIB $HOME/path/to/srlbr/srlconll-1.1/lib:$PERL5LIB

 Usage:

        > perl $HOME/path/to/srlbr/srlconll-1.1/bin/srl-eval.pl <gold_props> <predicted_props>


 The full installation installation instructions can be found srlconll-1.1/

### Liblinear
 Download [liblinear for python.](https://github.com/cjlin1/liblinear/tree/master/python)
 Navegate to the folder.

        > make


 Place executables *.so. files at models/lib and liblinear.py and liblinearutils.py.

## USAGE

        > python srl.py -h

 
Summons help

        > python srl.py

Runs multi-class classification using the following solvers:

| **Solver** | **Description**                                               |
|------------|---------------------------------------------------------------|
| 0          | L2-regularized logistic regression (primal)                   |
| 1          | L2-regularized L2-loss support vector classification (dual)   |
| 2          | L2-regularized L2-loss support vector classification (primal) |
| 3          | L2-regularized L1-loss support vector classification (dual)   |
| 4          | support vector classification by Crammer and Singer           |
| 5          | L1-regularized L2-loss support vector classification          |
| 6          | L1-regularized logistic regression                            |
| 7          | L2-regularized logistic regression (dual),for regression      |

Using only _gold-standard_ and _windows_ set of features.

        > python srl.py 1 -context -dtree -windows

Runs L2-regularized L2-loss support vector classification (dual) with context dtree and windows set of features.

## RESULTS
### State of the art.
|                 | **C** | **Precision** | **Recall** | **F1**  |
|-----------------|-------|---------------|------------|---------|
| (BELTRAO, 2016) |0.0625 | 82.17\%       | 82.88\%    | 82.52\% |

### Validation results

| **Features**             | **C**  | **S** | **Precision**   | **Recall**   | **F1**   |
|--------------------------|--------|-------|-----------------|--------------|----------|
| context                  | 0.0625 |   4   |     57.37\%     |    46.42\%   | 51.32\%  |
| dtree                    | 0.0625 |   4   |     76.31\%     |    75.13\%   | 75.72\%  |
| window                   | 0.0625 |   2   |     40.61\%     |    26.79\%   | 32.28\%  |
| context + window         | 0.0625 |   4   |     57.13\%     |    53.96\%   | 55.50\%  |
| context + dtree + window | 0.0625 |   1   |     76.80\%     |    75.67\%   | 76.23\%  |


## BIBLIOGRAPHY (PT)
    (ALVA-MANCHEGO, 2013)
    Anotação automática semissupervisionada de papéis semânticos para o português do Brasil
>http://www.teses.usp.br/teses/disponiveis/55/55134/tde-14032013-150816/publico/dissrevfernandoAlva.pdf

    (BELTRAO, 2016)
    Anotador de Papeis Semânticos para Português
>https://www.maxwell.vrac.puc-rio.br/30371/30371.PDF
