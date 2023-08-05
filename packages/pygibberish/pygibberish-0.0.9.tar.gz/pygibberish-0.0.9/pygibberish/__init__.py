#!/usr/bin/python
#huyifeng
import math
import os
import pickle
import sys
import itertools
import time
import logging
import logging.handlers


class Gibberish(object): 
    """
    main class
    """
    def __init__(self, par): 
        if isinstance(par, int): 
            if par < 2: 
                raise Exception("n must bigger then 2" % (par))
            self.accepted_chars = 'abcdefghijklmnopqrstuvwxyz'
            self.pos_y = {}
            self.pos_x = {}
            self.gram = par
            self.matrix = None
            self.pos_x = [i for i in self.accepted_chars]
            for i in xrange(self.gram - 2):
                self.pos_x  = [''.join(i) for i in\
                itertools.product(self.pos_x, self.accepted_chars)]
            self.pos_x = dict([(char, idx) for idx, char in enumerate(self.pos_x)])
            self.pos_y = dict([(char, idx) for idx, char in enumerate(self.accepted_chars)])
            logging.info('pos_x: %d' % (len(self.pos_x.keys())))
            logging.info('pos_y: %d' % (len(self.pos_y.keys())))
        elif isinstance(par, str):
            if os.path.exists(par): 
                model_data = pickle.load(open(par, 'rb'))
                self.accepted_chars = model_data['accepted_chars']
                self.pos_y = model_data['pos_y']
                self.pos_x = model_data['pos_x']
                self.gram = model_data['gram']
                self.matrix = model_data['matrix']
            else: 
                raise Exception("File %s not exists!" % (par))

    def __normalize(self, line):
        """ Return only the subset of chars from accepted_chars.
        This helps keep the  model relatively small by ignoring punctuation, 
        infrequenty symbols, etc. """
        return [c.lower() for c in line if c.lower() in self.accepted_chars]
    
    def __ngram(self, l):
        """ Return all n grams from l after normalizing """
        filtered = self.__normalize(l)
        for start in range(0, len(filtered) - self.gram + 1):
            yield ''.join(filtered[start:start + self.gram])
    
    def train(self, big):
        """ Write a simple model as a pickle file """
        if not os.path.exists(big):
            return False
        self.matrix = [[1 for i in xrange(len(self.pos_y))] for\
                                   i in xrange(len(self.pos_x))]
        for line in open(big):
            for s in self.__ngram(line):
                a = s[0:self.gram - 1]
                b = s[self.gram - 1:]
                self.matrix[self.pos_x[a]][self.pos_y[b]] += 1
        for i, row in enumerate(self.matrix):
            s = float(sum(row))
            for j in xrange(len(row)):
                row[j] = math.log(row[j] / s)
        return True

    def save(self, fname): 
        """
        save
        """
        if os.path.exists(fname): 
            logging.error('File %s already exists.' % (fname))
            return False
        data = {
                   'matrix' :   self.matrix, 
                   'accepted_chars'  :   self.accepted_chars,
                   'pos_y'  :   self.pos_y,
                   'pos_x'  :   self.pos_x,
                   'gram'   :   self.gram,
            }
        pickle.dump(data, open(fname, 'wb'))
        logging.info('Save model to %s succeed' % (fname))
        return True

    def calc(self, l):
        """ Return the average transition prob from l through log_prob_mat. """
        log_prob = 0.0
        transition_ct = 0
        for s in self.__ngram(l):
            a = s[0:self.gram - 1]
            b = s[self.gram - 1:]
            log_prob += self.matrix[self.pos_x[a]][self.pos_y[b]]
            transition_ct += 1
        return math.exp(log_prob / (transition_ct or 1))


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    def initlogger(loglevel, logo): 
        """ 
        init the logginger
        """
        logfmt = "%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s"
        log_path = BASE_DIR + '/log/'
        if os.path.exists(log_path) is False: 
            os.mkdir(log_path)
        logging.basicConfig(level = loglevel, format = logfmt)
        Rthandler = logging.handlers.RotatingFileHandler(log_path + '/%s.%d.%s.log' % 
                (os.path.basename(str(sys.argv[0])), os.getpid(), logo), 
                maxBytes = 300 * 1024 * 1024, backupCount = 20)
        Rthandler.setLevel(loglevel)
        formatter = logging.Formatter(logfmt)
        Rthandler.setFormatter(formatter)
        logging.getLogger('').addHandler(Rthandler)
    initlogger(logging.INFO, 'gib')
    if len(sys.argv) != 6: 
        print "python %s big good bad model 4" % (sys.argv[0])
        quit()
    try: 
        obj = Gibberish(int(sys.argv[5]))
        obj.train(sys.argv[1], sys.argv[2], sys.argv[3])
        obj.save(sys.argv[4])
    except Exception as e: 
        logging.error(str(e))



    
    
