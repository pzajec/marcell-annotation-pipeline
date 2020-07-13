#! /bin/sh

mkdir -p models/depparse \
                models/lemma \
                models/pos \
                models/ner

# POS tagging
wget -N -O models/pos/ssj500k "http://www.clarin.si/repository/xmlui/bitstream/handle/11356/1312/ssj500k?sequence=1&isAllowed=y" && \
wget -N -O models/pos/ssj500k.pretrain.pt "http://www.clarin.si/repository/xmlui/bitstream/handle/11356/1312/ssj500k.pretrain.pt?sequence=2&isAllowed=y" && \

# Lemmatisation
wget -N -O models/lemma/ssj500k+Sloleks_lemmatizer.pt "http://www.clarin.si/repository/xmlui/bitstream/handle/11356/1286/ssj500k%2bSloleks_lemmatizer.pt?sequence=1&isAllowed=y" && \

# Parsing
wget -N -O models/depparse/ssj500k_ud "http://www.clarin.si/repository/xmlui/bitstream/handle/11356/1258/ssj500k_ud?sequence=1&isAllowed=y" && \
wget -N -O models/depparse/ssj500k_ud.pretrain.pt "http://www.clarin.si/repository/xmlui/bitstream/handle/11356/1258/ssj500k_ud.pretrain.pt?sequence=2&isAllowed=y" && \

# NER
wget -N -O models/ner/ssj500k "http://www.clarin.si/repository/xmlui/bitstream/handle/11356/1321/ssj500k?sequence=3&isAllowed=y" && \
wget -N -O models/ner/ssj500k.pretrain.pt "http://www.clarin.si/repository/xmlui/bitstream/handle/11356/1321/ssj500k.pretrain.pt?sequence=4&isAllowed=y"

