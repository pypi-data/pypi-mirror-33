# IEML
[![Build Status](https://travis-ci.org/IEMLdev/ieml.svg?branch=master)](https://travis-ci.org/IEMLdev/ieml)

IEML is an artificial "natural" language having the following properties:
  * All the semantic relationships between IEML representations are computable.
  * Every meaning has only one IEML representation and every IEML representation has only one meaning.

The [ieml grammar](https://pierrelevyblog.files.wordpress.com/2014/01/00-grammaire-ieml1.pdf "IEML grammar") is constituted of a [dictionary](https://intlekt.io/?comments=I%3A "IEML dictionary") of elementary meanings units - words - and syntactic rules to combine them into topics, then facts and finally, theories.

This language have been made by the French philosopher [Pierre Levy](https://en.wikipedia.org/wiki/Pierre_L%C3%A9vy).

The language overcomes some inherent limitations of naturals languages for algorithmic manipulation :
  - text generation : rules-based natural language generation can leverage the regularity of the IEML syntax.
  - out-of-vocabularies : every proposition in IEML is build from ~3500 words, all defined in the dictionary with their paradigmatic relationships.
  - semantic similarities : we can automatically compute semantic relations between IEML propositions.
  - as an interlingua : IEML does not use any existing natural language as its core semantics. But everything that can be said can be described in IEML.
  - interaperobility of ontologies : Each IEML expression will have an unique URL.

Every meaning has only one IEML representation and every IEML representation has only one meaning :
  - synonymy : the IEML language has an instrinsic order that ensures that every expression has only one valid representation.
  - polysemy : All the IEML expressions are built from semantic primitives (dictionary) with meanining composition operators (syntax). The dictionary is not polysemic, the operators are injetive and theirs resulting propositions can not be reduced to its constituents. Therefore, there is no polysemy in IEML.
From there, we have in IEML a bijection between the signifiers and the signified.
IEML is then a discrete coordinate system of the semantic space. The IEML expressions are called Uniform Semantic Locators (USLs).

IEML is build from a set of [semantic primes](https://en.wikipedia.org/wiki/Semantic_primes) called the dictionary, and explicit rules of [compositions](https://fr.wikipedia.org/wiki/Combinatoire_s%C3%A9mantique).

The meaning of the words in the dictionary are conventional but not arbitrary, because they respects a set of constraints:
 - Each meaning must not already be present in the dictionary, and you can not express this meaning by composition of existing meanings of the dictionary.
 - The words are defined in systems (paradigms) and a paradigm must be the broadest possible in the concept.
 - A words defined in a paradigms is build from 3 more abstract words and the words must contains these meanings.
 
All the words have a french and english translation. A definition and synonyms in french and english will soon be available.

The linguist Anna Wierzbicka showed, with her theory [NSM](https://en.wikipedia.org/wiki/Natural_semantic_metalanguage), that we can define any concept described by a proposition in any natural languages with a set of 61 semantic primes, organised in paradigms.

The semantic of IEML is not a logic description, it can not be reduced to a description of a state of the world.
A word is not true nor false. Only at least a sentence can be, and only in a descriptive enonciation.

## Install

The library works with python 3.5+

You can install the ieml package with pip:
```bash
pip install ieml
```
If you want to install it from github:
```bash
git clone https://github.com/IEMLdev/ieml
python setup.py
```
## Quick start

### Dictionary

The IEML dictionary is a set of around ~3500 basic semantics units. 

The dictionay has its own syntax and primitives. The dictionary is organised in layers, from 0 (the most abstract) to 7 (the most specific). The words excepts the primitives are built from words of lower layers.  

The last version of the IEML dictionary is automatically downloaded and installed when instanced:
```python
from ieml.dictionary import Dictionary

dic = Dictionary()
dic.index
```
This return a list of all words defined in the dictionary.
There is an order defined on the terms of the dictionary, and d.index is the position of the words in this order.

You can access the translations of a word :
 ```python
t = dic.index[100]
t.translations.en
```
There are for the moment two languages supported: french (fr) and english (en)

The dictionaryis a graph of semantic relationships (paradigmatic) between the words.
All the relations are computed automatically from the terms definitions.
```python
t.relations.neighbours
```
This return a list of all the neighboors of term t and the type of relation they share.

You can also access the graph of relation as a numpy array of transitions :
```python
m = dic.relations_graph.connexity
```
Return a dense numpy array of boolean where `m[i, j]` is true if there is a relation 
between the term number `i` and the term number `j`.
```
from ieml.dictionary import term

t0 = term('wa.')
t1 = term('we.')
m[t0.index, t1.index]
```

The `term` function with a string argument call the dictionary parser and
return a Term if the string is a valid IEML expression of a term (defined in the dictionary).


### Syntax

A syntactic meaning unit is called an USL, for Uniform Semantic Locator. 
There is five differents types of USL :
 - Word : the basic meaning constituent, you can find all the defined words in the [IEML dictionary](https://dictionary.ieml.io).  
 - Topic: a topic aggregate Words into a root and a flexing morphem, a topic represents a subject, a process. 
 - Fact : a fact is a syntactic tree of topics, a fact symbolizes an event, a description.
 - Theory: a theory is a tree of facts, it represents a set of sentence linked together by causal, temporal, logic links etc. 
 - Text: a text is a set of Topic, Fact and Theory.

To instantiate an usl, you can use the USL parser with the `usl` function
with a string argument.

```python
from ieml.grammar import usl

usl('[([wa.])]') # topic with a single word
usl("[([t.u.-s.u.-d.u.-']+[t.u.-b.u.-'])*([b.i.-])]") # topic with two words in his root morphem and one in flexing 
```

You can also create an usl with constructors :
```python
from ieml.grammar import word, topic, fact, theory, text

w = word('wa.')
t0 = topic([w])
t1 = topic(['wa.', 'e.'])
t2 = topic(root=["t.u.-s.u.-d.u.-'", "t.u.-b.u.-'"], 
           flexing=["b.i.-"])
f = fact([(t2, t0, t1)])

t = text([t0, t1, t2, f])
```

For any usls, you can access the words, topics, facts, theories and texts defined 
in the usl by accessing the dedicated property:

```python
t.words
t.topics
t.facts
t.theories
t.texts
```
Each of these properties returns a set of USLs of the specific type.

For any couple of usl, you can compute a semantic similarity measure based on the 
relation matrix of the dictionary :
```python
from ieml.grammar.distance import dword
from ieml.grammar.tools import random_usl
u0 = random_usl(Topic)
u1 = random_usl(Text)

dword(u0, u1)
```

For the moments, only a similarity using the words of the USL is defined.

### Collection of USLs
For a list of USLs, you can compute a square matrix of relative order from each USLs :
```python
from ieml.distance.sort import square_order_matrix

usl_list = [random_usl() for _ in range(100)]

m = square_order_matrix(usl_list)

i = 20
ordered_usls = [usl_list[k] for k in m[i, :]]
```
ordered_usls is the list of usl ordered from USLs number i to the farrest USL from USL i in the collection.
This method use the semantic distance between words of the dictionary.

 
 
