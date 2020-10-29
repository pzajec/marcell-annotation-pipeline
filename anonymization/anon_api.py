from flask import Flask
from flask import request
from flask import Response

from bs4 import BeautifulSoup
import pandas as pd

from utils import *

app = Flask(__name__)


def parse_xml(xml_doc):
    bs = BeautifulSoup(xml_doc, "lxml-xml")    
    
    body = bs.find('body')
    sources = [x for x in body.find_all('source')]
    
    chunks = pd.DataFrame({
        'text': [x.text for x in sources],
        'seg': [x['mq:segpart'] for x in sources]
    })
    chunks = chunks.drop_duplicates()
    return chunks


@app.route('/anonymize', methods=['POST'])
def run_pipeline():
    xml_doc = request.data.decode('utf-8-sig')
    
    chunks = parse_xml(xml_doc)
    
    response = query_pipeline(chunks)
    meta, sents = parse_conll(response.text)
    html_doc = generate_html(sents)

    return Response(
        response=html_doc, 
        status=200, 
        mimetype="application/html")

if __name__ == "__main__":
    app.run(port=5001)