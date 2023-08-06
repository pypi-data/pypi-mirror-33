import json
import luigi
import requests
import time

class GSICrawlerScraper(luigi.Task):
    """
    Template task for retrieving data with GSICrawler.
    """

    @property
    def host(self):
        "GSICrawler endpoint"
        return 'http://gsicrawler.cluster.gsi.dit.upm.es/api/v1'

    @property
    def source(self):
        "GSICrawler source"
        return 'twitter'

    @property
    def query(self):
        "query to retrieve results about"
        return 'gsiupm'

    @property
    def number(self):
        "Number of documents to retrieve"
        return 10

    @property
    def taskoutput(self):
        "output: json or elasticsearch"
        return 'json'

    @property
    def esendpoint(self):
        "elasticsearch endpoint"
        return None
    @property
    def index(self):
        "elasticsearch index"
        return None
    @property
    def querytype(self):
        "query type"
        return 'search'
    @property
    def doctype(self):
        "elasticsearch doctype"
        return None
    
    def run(self):
        """
        Run analysis task 
        """
        with self.output().open('w') as outfile:
            url = '{host}/scrapers/{source}/?query={query}&number={number}&output={output}&esendpoint={esendpoint}&index={index}&doctype={doctype}&querytype={querytype}'.format(
                query=self.query,number=self.number,output=self.taskoutput,esendpoint=self.esendpoint, index=self.index, doctype=self.doctype, host=self.host,source=self.source, querytype=self.querytype)
            print(url)
            r = requests.get(url) 
            print(r.json())
            if 'results' in r.json():
                outfile.write(json.dumps(r.json()["results"]))
            else:
                url = self.host+'/tasks/'+r.json()['result'].split(" ")[1]
                while(type(r.json()['result']) is not list):
                    print(url)
                    print(len(r.json()['result'].split(" ")))
                    time.sleep(10)
                    r = requests.get(url)
                outfile.write(json.dumps(r.json()["result"]))

