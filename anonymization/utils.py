import pandas as pd
from io import StringIO

import requests
from requests_toolbelt import MultipartEncoder


def query_pipeline(chunks):

    data = {
        "text": "\n".join(chunks.text),
        "meta": '''{
            "doc_id":"sl-test123", 
            "language":"sl", 
            "date":"2020-06-30", 
            "title":"Poskusni dokument", 
            "type":"poskus", 
            "entype":"test"
        }'''
    }
    payload = MultipartEncoder(data)

    response = requests.post('http://localhost:80/annotate', 
                            data=payload, headers={'Content-Type': payload.content_type})
    return response

def parse_conll(text):
    sents = []
    
    spl = text.split('\n')
    i = 0

    meta = {}
    while i < len(spl) and len(spl[i]) > 0:
        key, val = spl[i][2:].split(' = ')
        meta[key] = val
        i += 1

    while i < len(spl):
        while i < len(spl) and len(spl[i]) == 0:
            i += 1

        t_meta = {}
        while i < len(spl) and spl[i][0] == '#':
            key, val = spl[i][2:].split(' = ')
            t_meta[key] = val
            i += 1

        tokens = []
        while i < len(spl) and len(spl[i]) > 0:
            tokens.append(spl[i])
            i += 1
            
        if len(tokens) > 0:
            resp_csv = StringIO("\n".join(tokens))
            tokens = pd.read_csv(resp_csv, sep='\t', header=None,
                    names=meta['global.columns'].split(' '))
            sents.append((t_meta, tokens))

    return meta, sents

def generate_html(sents):
    
    html = "<html><body>"
    for sent_meta, tokens in sents:
        curr_ent = None
        for _, token in tokens.iterrows():
            ne = token['MARCELL:NE']
            
            if ne == 'O' and curr_ent:
                html += "</s></b> "
                curr_ent = None
            elif ne != 'O':
                pos, ent = ne[:ne.find('-')], ne[ne.find('-') + 1:]
                if pos == 'B':
                    if curr_ent:
                        html += "</s></b> "
                    curr_ent = ent
                    html += "<b><s> "
            html += token['FORM']
            if not 'SpaceAfter=No' in token['MISC']:
                html += " "
        if curr_ent:
            html += "</s></b> "
        html += "<br>"
    html += "</body></html>"
    return html