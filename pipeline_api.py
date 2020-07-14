import os
import json
import hashlib
import shutil
import subprocess

from flask import Flask
from flask import request

from pathlib import Path

import stanfordnlp
from stanfordnlp.pipeline.doc import Document
from stanfordnlp.models.common.conll import CoNLLFile


app = Flask(__name__)

meta_fields = ['language', 'date', 'title', 'type', 'entype']

# Load config from env variables
obeliks4J_path = Path(os.environ.get('OBELIKS4J_PATH', default='/usr/src/Obelisk4J/obeliks.jar'))
if not obeliks4J_path.exists():
    raise Exception('Invalid value for OBELIKS4J_PATH: path doesn\'t exist!')

# Set up stanfordnlp pipeline
config = {
        'processors': 'tokenize,mwt,ner,pos,lemma,depparse',
        'tokenize_pretokenized': True,
        'pos_model_path': './models/pos/ssj500k',
        'pos_pretrain_path': './models/pos/ssj500k.pretrain.pt',
        'pos_batch_size': 1000,
        'lemma_model_path': './models/lemma/ssj500k+Sloleks_lemmatizer.pt',
        'depparse_model_path': './models/depparse/ssj500k_ud',
        'depparse_pretrain_path': './models/pos/ssj500k.pretrain.pt', 
        'ner_model_path': './models/ner/ssj500k',
        'ner_pretrain_path': './models/ner/ssj500k.pretrain.pt',
        'ner_forward_charlm_path': None, 'ner_backward_charlm_path': None,
        'use_gpu': True
}
nlp = stanfordnlp.Pipeline(**config)


class InvalidParams(Exception):

    def __init__(self, message, status_code=500):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code


def check_form_data(text, meta):
    if text is None:
        raise InvalidParams('Missing "text" form data inside request.')

    if meta is None:
        raise InvalidParams('Missing "meta" form data inside request.')

    if text.isspace():
        raise InvalidParams('Form data inside "text" is empty.')

    if meta.isspace():
        raise InvalidParams('Form data inside "meta" is empty.')


def run_obeliks4J(text):
    args = ['java', '-jar', str(obeliks4J_path), '-d']
    child = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    b = text.encode('utf-8')

    child.stdin.write(b)
    out = child.communicate()[0]
    child.stdin.close()

    return out.decode('utf-8')
    
    

def run_stanfordnlp(text, standoff_metadata):
    # Because we already have CoNLL-U formated input, we need to skip the tokenization step.
    # This currently done by setting the Documents text parameter as None. After that we also
    # have to manually create a CoNLLFile instance and append it to the Document.
    doc = Document(text=None)
    conll_file = CoNLLFile(input_str=text)
    doc.conll_file = conll_file

    # Start processing.
    res = nlp(doc)

    # Append CONLLU-P metadata.
    rows = create_metadata(standoff_metadata)

    for line in res.conll_file.conll_as_string().splitlines():
        if not line.startswith('#') and len(line) > 0 and not line.isspace():
            # Because stanfordnlp returns in the basic CONLLU format, we need to move
            # the NER values from the MISC column to a separate one.
            vals = line.split('\t')
            misc_vals = vals[9].split('|')

            new_misc = []
            for misc_val in misc_vals:
                if misc_val.startswith('NER='):
                    vals.append(misc_val)
                else:
                    new_misc.append(misc_val)
            vals[9] = '|'.join(new_misc)
            rows.append('\t'.join(vals))
        else:
            rows.append(line)

    return '\n'.join(rows)


def create_metadata(standoff_metadata):
    res = []

    res.append('# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC')
    res.append('# newdoc id = {}'.format(standoff_metadata['doc_id']))

    for key in meta_fields:
        if key not in standoff_metadata:
            raise InvalidParams('Missing key "{}" in standoff metadata.'.format(key))

        val = standoff_metadata[key]
        val = val.replace('\n', ' ').replace('\r', '')

        res.append('# {} = {}'.format(key, val))

    res.append('\n')
    return res


@app.route('/annotate', methods=['POST'])
def run_pipeline():
    # Raw text for processing
    text = request.form.get('text')

    # Standoff metadata in JSON format
    meta = request.form.get('meta')

    # Check input validity
    check_form_data(text, meta)

    standoff_metadata = json.loads(meta)

    # Run Obeliks4J for tokenization
    out = run_obeliks4J(text)

    # Run StanfordNLP pipeline on Obeliks4J output
    out = run_stanfordnlp(out, standoff_metadata)

    return out, 200


@app.errorhandler(InvalidParams)
def handle_invalid_usage(error):
    return error.message, error.status_code

