import os
import json
import hashlib
import shutil

from flask import Flask
from flask import request, Response

from pathlib import Path

import stanfordnlp
from stanfordnlp.pipeline.doc import Document
from stanfordnlp.models.common.conll import CoNLLFile


app = Flask(__name__)

meta_fields = ['language', 'date', 'title', 'type', 'entype']

# Load config from env variables
data_dir = Path(os.environ.get('DATA_DIR'))
if not data_dir.exists():
    raise Exception('Invalid value for DATA_DIR: path doesn\'t exist!')

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


def check_form_data(text, meta, docid):
    if text is None:
        raise InvalidParams('Missing "text" form data inside request.')

    if meta is None:
        raise InvalidParams('Missing "meta" form data inside request.')

    if docid is None:
        raise InvalidParams('Missing "docid" form data inside request.')

    if text.isspace():
        raise InvalidParams('Form data inside "text" is empty.')

    if meta.isspace():
        raise InvalidParams('Form data inside "meta" is empty.')

    if docid.isspace():
        raise InvalidParams('Form data inside "docid" is empty.')


def run_obeliks4J(res_dir, input_name, output_name):
    input_file = res_dir / input_name
    output_file = res_dir / output_name
    command = 'java -jar ' + str(obeliks4J_path) + ' -d -if ' + str(input_file) + \
            ' -o ' + str(output_file)
    # TODO: Check for errors? Obeliks4J doesn't seem to have exit codes implemented yet.
    os.system(command)
    

def run_stanfordnlp(res_dir, input_name, output_name, standoff_metadata, docid):
    input_file = res_dir / input_name
    output_file = res_dir / output_name

    # Because we already have CoNLL-U formated input, we need to skip the tokenization step.
    # This currently done by setting the Documents text parameter as None. After that we also
    # have to manually create a CoNLLFile instance and append it to the Document.
    doc = Document(text=None)
    conll_file = CoNLLFile(filename=str(input_file))
    doc.conll_file = conll_file

    # Start processing.
    res = nlp(doc)

    # Write metadata to input file
    add_metadata(output_file, standoff_metadata, docid)

    # Save result to output CoNLL-U Plus file.
    with output_file.open('a') as f:
        f.write(res.conll_file.conll_as_string())


def add_metadata(file_path, standoff_metadata, docid):
    with file_path.open('a') as f:
        f.write('# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC\n')
        f.write('# newdoc id = {}\n'.format(docid))

        for key in meta_fields:
            if key not in standoff_metadata:
                cleanup(res_dir)
                raise InvalidParams('Missing key "{}" in standoff metadata.'.format(key))

            val = standoff_metadata[key]
            val = val.replace('\n', ' ').replace('\r', '')

            f.write('# {} = {}\n'.format(key, val))


def cleanup(res_dir):
    shutil.rmtree(res_dir)


@app.route('/annotate', methods=['POST'])
def run_pipeline():
    # Raw text for processing
    text = request.form.get('text')

    # Standoff metadata in JSON format
    meta = request.form.get('meta')

    # Document ID to be inserted into final CONLLUP file
    docid = request.form.get('docid')

    # Check input validity
    check_form_data(text, meta, docid)

    standoff_metadata =  json.loads(meta)

    # Create hash from text for use as an identity
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()

    # Create directory for data
    res_dir = data_dir / text_hash
    res_dir.mkdir(parents=True, exist_ok=True)

    input_name = 'input.txt'
    obeliks_outname = 'obeliks.out'
    result_name = 'result.conllu'

    # Save input text to file
    input_file = res_dir / input_name
    with input_file.open('a') as f:
        f.write(text)

    # Run Obeliks4J for tokenization
    run_obeliks4J(res_dir, input_name, obeliks_outname)

    # Run StanfordNLP pipeline on Obeliks4J output
    run_stanfordnlp(res_dir, obeliks_outname, result_name, standoff_metadata, docid)

    # Stream the result file because it may be quite large
    result_file = res_dir / result_name
    def generate_res():
        with result_file.open('r') as f:
            for row in f:
                yield row
        # Clean up files when done streaming
        cleanup(res_dir)
    return Response(generate_res(), status=200)


@app.errorhandler(InvalidParams)
def handle_invalid_usage(error):
    return error.message, error.status_code

