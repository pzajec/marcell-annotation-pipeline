#! /bin/sh

mkdir -p models/depparse \
         models/lemma \
         models/pos \
         models/ner

# POS tagging
wget -P models/pos/ http://www.clarin.si/repository/xmlui/bitstream/handle/11356/1312/ssj500k?sequence=1&isAllowed=y && \
wget -P models/pos/ http://www.clarin.si/repository/xmlui/bitstream/handle/11356/1312/ssj500k.pretrain.pt?sequence=2&isAllowed=y && \

# Lemmatisation
wget -P models/lemma/ http://www.clarin.si/repository/xmlui/bitstream/handle/11356/1286/ssj500k%2bSloleks_lemmatizer.pt?sequence=1&isAllowed=y && \

# Parsing
wget -P models/depparse/ http://www.clarin.si/repository/xmlui/bitstream/handle/11356/1258/ssj500k_ud?sequence=1&isAllowed=y && \
wget -P models/depparse/ http://www.clarin.si/repository/xmlui/bitstream/handle/11356/1258/ssj500k_ud.pretrain.pt?sequence=2&isAllowed=y && \

# NER
wget -P models/ner/ http://www.clarin.si/repository/xmlui/bitstream/handle/11356/1321/ssj500k?sequence=3&isAllowed=y && \
wget -P models/ner/ http://www.clarin.si/repository/xmlui/bitstream/handle/11356/1321/ssj500k.pretrain.pt?sequence=4&isAllowed=y

