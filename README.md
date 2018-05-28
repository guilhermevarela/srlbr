# SEMANTIC ROLE LABELING BR
Semantic Role Labeling is a task within the domain of natural language processing, that attempts to answer
who, did what, to whom given a sentence. This repository is a partial implementation of a masters dissertation,
(BELTRAO, 2016) that uses Propbank Br v1.1 as the golden set, Liblinear implemention for Support Vector Machines 
for multiclass classfication, Official Conll 2005 Shared Task scrips for evaluation and three sets of feature
enginnering.


## A golden set example:

| ID | FORM     | LEMMA    | GPOS  | MORPH       | DTREE | FUNC | CTREE     | PRED     | ARG       |
|----|----------|----------|-------|-------------|-------|------|-----------|----------|-----------|
| 1  | A        | o        | art   | F\|S        | 2     | >N   | (FCL(NP*  | -        | *         |
| 2  | série    | série    | n     | F\|S        | 8     | SUBJ | *         | -        | (A1*)     |
| 3  | exibida  | exibir   | v-pcp | F\|S        | 2     | N<   | (ICL(VP*) | -        | *         |
| 4  | aqui     | aqui     | adv   | -           | 3     | ADVL | (ADVP*)   | -        | *         |
| 5  | por      | por      | prp   | -           | 3     | PASS | (PP*      | -        | *         |
| 6  | a        | o        | art   | F\|S        | 7     | >N   | (NP*      | -        | *         |
| 7  | Cultura  | cultura  | n     | F\|S        | 5     | P<   | *)))      | -        | *         |
| 8  | estreiou | estrear  | v-fin | PS\|3S\|IND | 0     | STA  | (VP*)     | estreiar | *         |
| 9  | em       | em       | prp   | -           | 8     | ADVL | (PP*      | -        | (AM-LOC*) |
| 10 | a        | o        | art   | F\|S        | 11    | >N   | (NP*      | -        | *         |
| 11 | TVI      | TVI      | prop  | F\|S        | 9     | P<   | *         | -        | *         |
| 12 | de       | de       | prp   | _           | 11    | N<   | (PP*      | -        | *         |
| 13 | Portugal | Portugal | prop  | M\|S        | 12    | P<   | (NP*))))  | _        | *         |
| 14 | .        | .        | pu    | -           | 8     | PUC  | *)        | -        | *         |

## The Golden Set Features:
## Sematic Role Labels

## FEATURE ENGINEERING (BELTRAO, 2016)
### Window features
### Context features
### Dtree featires

## SETUP
### Project
### Python
### Pearl
### Liblinear

## RESULTS
### State of the art.
### Partial results.


## BIBLIOGRAPHY (PT)
    (ALVA-MANCHEGO, 2013)
    Anotação automática semissupervisionada de papéis semânticos para o português do Brasil
>http://www.teses.usp.br/teses/disponiveis/55/55134/tde-14032013-150816/publico/dissrevfernandoAlva.pdf

    (BELTRAO, 2016)
    Anotador de Papeis Semânticos para Português
>https://www.maxwell.vrac.puc-rio.br/30371/30371.PDF
