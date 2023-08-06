# csirtg-urlsml-tf-py
simple python/keras/tensorflow library for detecting odd urls in python

# References

https://csirtgadgets.com/commits/2018/6/9/phishing-predictions-with-deep-learning-and-tensorflow
https://github.com/csirtgadgets/tf-phishing-example

https://medium.com/slalom-engineering/detecting-malicious-requests-with-keras-tensorflow-5d5db06b4f28
https://csirtgadgets.com/commits/2018/3/8/hunting-for-suspicious-domains-using-python-and-sklearn
https://csirtgadgets.com/commits/2018/3/30/hunting-for-threats-like-a-quant

# Getting Started

## Incorporating into a Project

```bash
$ pip install csirtg_urlsml_tf
```

```python
from csirtg_urlsml_tf import predict, normalize_urls
from pprint import pprint

indicators = normalize_urls('https://g00gle.com/about-us')
predictions = predict(indicators)

for idx, v in enumerate(indicators):
    print("%f - %s" % (predictions[idx], v))
```


## Development and Building
```bash
$ pip install -r dev_requirements.txt
$ python setup.py develop

$ csirtg-urlsml-tf -i http://paypal-ate-my-lunch.com
Using TensorFlow backend.
0.045636 - http://paypal-ate-my-lunch.com

$ csirtg-urlsml-tf -i 'http://paypal.com|https://google.com/about-us|https://g0ogle.com/about-us'
Using TensorFlow backend.
0.632489 - http://paypal.com
0.038573 - https://google.com/about-us
0.040402 - https://g0ogle.com/about-us

$ csirtg-urlsml-tf -i 'http://hospitalregionalcoyhaique.cl/libraries/joomla/web/upgrade/verification/32216DN73N1C35BM7D9M/card.php'
Using TensorFlow backend.
0.990057 - http://hospitalregionalcoyhaique.cl/libraries/joomla/web/upgrade/verification/32216DN73N1C35BM7D9M/card.php
```

# Rebuilding Models

If you want to rebuild the models with your own data:

1. Update `data/whitelist.txt`
1. Update `data/blacklist.txt`
1. Run the `helpers/build.sh` command

```bash
$ bash helpers/build.sh  # this will take a few minutes...

Using TensorFlow backend.
Layer (type)                 Output Shape              Param #
=================================================================
embedding_1 (Embedding)      (None, 2083, 32)          2112
_________________________________________________________________
dropout_1 (Dropout)          (None, 2083, 32)          0
_________________________________________________________________
lstm_1 (LSTM)                (None, 16)                3136
_________________________________________________________________
dropout_2 (Dropout)          (None, 16)                0
_________________________________________________________________
dense_1 (Dense)              (None, 1)                 17
=================================================================
Total params: 5,265
Trainable params: 5,265
Non-trainable params: 0
_________________________________________________________________
None
Train on 31593 samples, validate on 13540 samples
Epoch 1/3
  768/31593 [..............................] - ETA: 4:40 - loss: 0.6932 - acc: 0.4922

```
