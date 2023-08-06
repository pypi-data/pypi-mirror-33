import json
import luigi
import requests
import time

class SenpyAnalysis(luigi.Task):
    """
    Template task for analysing data with Senpy.
    """

    @property
    def host(self):
        "Senpy endpoint"
        return 'http://test.senpy.cluster.gsi.dit.upm.es/api/'

    @property
    def algorithm(self):
        "Senpy algorithm"
        return 'sentiment-tass'

    @property
    def fieldName(self):
        "json fieldName to analyse"
        return 'schema:articleBody'

    @property
    def apiKey(self):
        "Senpy apiKey if required"
        return ''

    @property
    def lang(self):
        "Senpy lang if required"
        return 'en'

    @property
    def timeout(self):
        "Time between requests"
        return 1
    
    def run(self):
        """
        Run analysis task 
        """
        with self.input().open('r') as fobj:
            with self.output().open('w') as outfile:
                fobj = json.load(fobj)
                for i in fobj:
                    b = {}
                    b['@id'] = i['@id']
                    b['_id'] = i['@id']
                    b['@type'] = i['@type']
                    r = requests.post(self.host, data={'i':i[self.fieldName], 'apiKey': self.apiKey, 'algo': self.algorithm, 'lang': self.lang})
                    time.sleep(self.timeout)
                    print(r.json())
                    i.update(r.json()["entries"][0])
                    i.update(b)
                    outfile.write(json.dumps(i))
                    outfile.write('\n')

