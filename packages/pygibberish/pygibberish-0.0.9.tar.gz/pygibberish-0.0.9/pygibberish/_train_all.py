import pygibberish





if __name__ == '__main__': 
    for i in xrange(3,6):
        for data in [
            ('train_data/ch_big.txt', 'train_data/ch_good.txt', 'train_data/ch_bad.txt', 'ch'), 
            ('train_data/en_big.txt', 'train_data/en_good.txt', 'train_data/en_bad.txt', 'en')
        ]:
            model = pygibberish.Gibberish(i)
            print "Training %d %s" % (i, data[3])
            model.train(data[0])
            model.save("%s%d.pki" % (data[3], i))

