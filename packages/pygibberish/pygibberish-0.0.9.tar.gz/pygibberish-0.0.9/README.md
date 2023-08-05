Overview
========

A sample python lib to test gibberish, the model can give a score for a given string.
This score will be very low if this string is gibberish.
It uses a N character markov chain.
[![Markov_chain]](http://en.wikipedia.org/wiki/Markov_chain)

Usage
=====
```
import pygibberish
#This demo show you how to train model & save model
if __name_ == '__main__':
    gib = pygibberish.Gibberish(3) # 3 is the n of gram len. eg.ilovepython ->ilo,lov,loe...
    # You can find these train data in the root dir of package
    gib.train('pygibberish/train_data/en_big.txt') 
    gib.save('en2.pki')
    print gib.calc("asdfasdf")
    print gib.calc("apple")

or

#This demo show you how to use a model file to calc the score
import pygibberish
if __name_ == '__main__':
    gib = pygibberish.Gibberish('en2.pki')
    print gib.calc("asdfasdf")
```

How it works
============
*The markov chain first 'trains' or 'studies' a few MB of English/Chinese text, recording how often characters appear next to each other. Eg, given the text "Rob likes hacking" it sees Ro, ob, o[space], [space]l, ... It just counts these pairs. After it has finished reading through the training data, it normalizes the counts. Then each character has a probability distribution of 26 followup character following the given initial.

*So then given a string, it measures the probability of generating that string according to the summary by just multiplying out the probabilities of the adjacent pairs of characters in that string. EG, for that "Rob likes hacking" string, it would compute prob['r']['o'] * prob['o']['b'] * prob['b']['l'] ... This probability then measures the amount of 'surprise' assigned to this string according the data the model observed when training. If there is funny business with the input string, it will pass through some pairs with very low counts in the training phase, and hence have low probability/high surprise.

*I then look at the amount of surprise per character for a few known good strings, and a few known bad strings, and pick a threshold between the most surprising good string and the least surprising bad string. Then I use that threshold whenever to classify any new piece of text.


