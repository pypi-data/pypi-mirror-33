#!/usr/bin/env python
# encoding: utf-8
"""
install_glove.py
~~~~~~~~~~~~~~~~

Install pretrained glove word embeddings

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-05-30"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports 
import os
import urllib
import sys
import hashlib
import zipfile

# third party imports

# local imports
from atnlp.model.embed import EMB_DIR

# globals
URL = "http://nlp.stanford.edu/data/glove.6B.zip"
MD5ZIP = "056ea991adb4740ac6bf1b6d9b50408b"
MD5TXT = "b78f53fb56ec1ce9edc367d2e6186ba4"
MD5W2V = "0833e974ac24308f448031cd1d0e3c76"
TARGETZIP = os.path.join(EMB_DIR, 'glove.6B.zip')
TARGETTXT = os.path.join(EMB_DIR, 'glove.6B.300d.txt')
TARGETW2V = os.path.join(EMB_DIR, 'glove.6B.300d.w2vformat.txt')

def main():
    # check if already installed
    if os.path.exists(TARGETW2V):
        if md5hash(TARGETW2V) == MD5W2V:
            print("glove embeddings already installed at: {}".format(TARGETW2V))
            return
        else:
            print("glove embbeddings found but appear corrupt, removing...")
            os.remove(TARGETW2V)

    # prepare directory
    if not os.path.exists(EMB_DIR):
        os.makedirs(EMB_DIR)
    
    # check if txt already available else install 
    if not os.path.exists(TARGETTXT) or md5hash(TARGETTXT) != MD5TXT: 

        # check for zip
        if os.path.exists(TARGETZIP) and md5hash(TARGETZIP) != MD5ZIP:
            print("glove embbeddings zip found but appers corrupt, removing...")
            os.remove(TARGETZIP)

        # download zip
        if not os.path.exists(TARGETZIP):
            print("downloading glove embeddings from {}".format(URL))
            urllib.request.urlretrieve(URL, TARGETZIP, reporthook)

        # extract zip
        print("extracting zip...")
        with zipfile.ZipFile(TARGETZIP,"r") as zip_ref:
            zip_ref.extractall(EMB_DIR)

        # remove zip 
        print("cleaning up zip...")
        os.remove(TARGETZIP)

    # convert 
    print("converting to w2v format...")
    from gensim.scripts.glove2word2vec import glove2word2vec
    glove2word2vec(TARGETTXT, TARGETW2V)


def reporthook(blocknum, blocksize, totalsize):
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = readsofar * 1e2 / totalsize
        s = "\r%5.1f%% %*d / %d" % (
            percent, len(str(totalsize)), readsofar, totalsize)
        sys.stderr.write(s)
        if readsofar >= totalsize: # near the end
            sys.stderr.write("\n")
    else: # total size is unknown
        sys.stderr.write("read %d\n" % (readsofar,))

def md5hash(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


if __name__ == "__main__":
    main()
# EOF
