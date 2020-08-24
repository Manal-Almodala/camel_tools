
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright 2018-2019 New York University Abu Dhabi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""This module contains the CAMeL Tools sentiment analyzer component.
"""


import torch
import torch.nn.functional as torch_fun
from transformers import BertTokenizer, BertForSequenceClassification

from camel_tools.data import get_dataset_path


_DEFAULT_DATA_PATH = get_dataset_path('SentimentAnalysis')
_LABELS = ('positive', 'negative', 'neutral')


class SentimentAnalyzer:
    """A class for running a fine-tuned sentiment analysis model to predict
    the sentiment of given sentences.
    """

    def __init__(self, model_path):
        if model_path is None:
            model_path = _DEFAULT_DATA_PATH

        self.model = BertForSequenceClassification.from_pretrained(model_path)
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.labels_map = {i: label for i, label in enumerate(_LABELS)}

    @staticmethod
    def pretrained(model_name=None):
        """Load a pre-trained model provided with camel_tools.

        Args:
            model_name (:obj:`str`, optional): Name of pre-trained model to
                load.
                Two models are available: 'arabert' and 'mbert'.
                If None, the default model ('arabert') will be loaded.
                Defaults to None.

        Returns:
            :obj:`SentimentAnalyzer`: Instance with loaded pre-trained model.
        """

        model_path = str(get_dataset_path('SentimentAnalysis', model_name))
        return SentimentAnalyzer(model_path)

    @staticmethod
    def labels():
        """Get the list of possible sentiment labels returned by predictions.

        Returns:
            :obj:`list` of :obj:`str`: List of sentiment labels.
        """

        return list(_LABELS)

    def predict_sentence(self, sentence):
        """Predict the sentiment label of a single sentence.

        Args:
            sentence (:obj:`str`): Input sentence.

        Returns:
            :obj:`str`: The predicted sentiment label for given sentence.
        """

        # Add special tokens takes care of adding [CLS], [SEP] tokens
        input_ids = torch.tensor(
            self.tokenizer.encode(sentence, add_special_tokens=True,
                                  max_length=512)).unsqueeze(0)
        # input_ids shape: [1, len(input_ids)]

        self.model.eval()
        with torch.no_grad():
            outputs = self.model(input_ids)
            # outputs is a tuple of (logits, )

        predictions = torch_fun.softmax(outputs[0].squeeze(), dim=0)
        # predictions shape: [config.num_labels]
        max_prediction = torch.argmax(predictions, dim=0)
        predicted_label = self.labels_map[max_prediction.item()]

        return predicted_label

    def predict(self, sentences):
        """Predict the sentiment labels of a list of sentences.

        Args:
            sentences (:obj:`list` of :obj:`str`): Input sentences.

        Returns:
            :obj:`list` of :obj:`str`: The predicted sentiment labels for given
            sentences.
        """

        self.model.eval()
        predicted_labels = []
        with torch.no_grad():
            for i, sentence in enumerate(sentences):
                # Add special tokens takes care of adding [CLS], [SEP] tokens
                input_ids = torch.tensor(
                    self.tokenizer.encode(sentence, add_special_tokens=True,
                                          max_length=512)).unsqueeze(0)
                outputs = self.model(input_ids)
                predictions = torch_fun.softmax(outputs[0].squeeze(), dim=0)
                # predictions shape: [config.num_labels]
                max_prediction = torch.argmax(predictions, dim=0)
                predicted_label = self.labels_map[max_prediction.item()]
                predicted_labels.append(predicted_label)

        return predicted_labels
