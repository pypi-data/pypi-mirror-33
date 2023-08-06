import requests

from json import loads

NEWS_API_ENDPOINT = "https://newsapi.org/v1/"
ARTICLES_API = "articles"

#defineconstant
CNN = 'cnn'
DEFAULT_SOURCE = [CNN]
SORT_BY_TOP = 'top'

class NewsAPIClient:
    def __init__(self, apiKey, endPoint=NEWS_API_ENDPOINT, apiName=ARTICLES_API):
        self.api_key = apiKey
        self.url = self._buildUrl(endPoint, apiName)

    def _buildUrl(self, endPoint, apiName):
        return endPoint + apiName

    def getNewsFromSource(self, sources=DEFAULT_SOURCE, sortBy=SORT_BY_TOP):
        articles = []

        # get news from each source
        for source in sources:
            payload = {
                'apiKey': self.api_key,
                'source': source,
                'sortBy': sortBy
            }
            response = requests.get(self.url, params=payload)
            # response.content is a binary
            res_json = loads(response.content.decode('utf-8'))
            print ('# of news received from news api: ', len(res_json))
            # Extract info from response
            if (res_json is not None and
                res_json['status'] == 'ok' and
                res_json['source'] is not None):
                # populate news source in each articles
                for news in res_json['articles']:
                    news['source'] = res_json['source']
                    # join two list into one list
                    articles.extend(res_json['articles'])

        return articles
