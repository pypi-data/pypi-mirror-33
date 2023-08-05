import requests
import json

from senpy.plugins import SentimentPlugin
from senpy.models import Sentiment


class Sentiment140(SentimentPlugin):
    '''Connects to the sentiment140 free API: http://sentiment140.com'''

    author = "@balkian"
    version = '0.2'
    url = "https://github.com/gsi-upm/senpy-plugins-community"
    extra_params = {
        'language': {
            "@id": 'lang_sentiment140',
            'aliases': ['language', 'l'],
            'required': False,
            'default': 'auto',
            'options': ['es', 'en', 'auto']
        }
    }

    maxPolarityValue = 1
    minPolarityValue = 0

    def analyse_entry(self, entry, params):
        lang = params["language"]
        res = requests.post("http://www.sentiment140.com/api/bulkClassifyJson",
                            json.dumps({
                                "language": lang,
                                "data": [{
                                    "text": entry['nif:isString']
                                }]
                            }))
        p = params.get("prefix", None)
        polarity_value = self.maxPolarityValue * int(
            res.json()["data"][0]["polarity"]) * 0.25
        polarity = "marl:Neutral"
        neutral_value = self.maxPolarityValue / 2.0
        if polarity_value > neutral_value:
            polarity = "marl:Positive"
        elif polarity_value < neutral_value:
            polarity = "marl:Negative"

        sentiment = Sentiment(
            prefix=p,
            marl__hasPolarity=polarity,
            marl__polarityValue=polarity_value)
        sentiment.prov__wasGeneratedBy = self.id
        entry.sentiments.append(sentiment)
        entry.language = lang
        yield entry

    def test(self, *args, **kwargs):
        '''
        To avoid calling the sentiment140 API, we will mock the results
        from requests.
        '''
        from senpy.testing import patch_requests
        expected = {"data": [{"polarity": 4}]}
        with patch_requests(expected) as (request, response):
            super(Sentiment140, self).test(*args, **kwargs)
            assert request.called
            assert response.json.called

    test_cases = [
        {
            'entry': {
                'nif:isString': 'I love Titanic'
            },
            'params': {},
            'expected': {
                "nif:isString": "I love Titanic",
                'sentiments': [
                    {
                        'marl:hasPolarity': 'marl:Positive',
                    }
                ]
            }
        }
    ]
