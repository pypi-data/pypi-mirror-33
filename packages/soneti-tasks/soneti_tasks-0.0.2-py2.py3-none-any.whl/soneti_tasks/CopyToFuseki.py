import json
import luigi
import requests
import time

class CopyToFuseki(luigi.Task):
    """
    Template task for inserting a dataset into Fuseki.
    """

    @property
    def host(self):
        "Fuseki endpoint"
        return 'localhost'

    @property
    def port(self):
        "Fuseki endpoint port"
        return 3030

    @property
    def dataset(self):
        "Fuseki dataset"
        return 'default'

    def run(self):
        """
        Run indexing to Fuseki task 
        """
        f = []

        with self.input().open('r') as infile:
            with self.output().open('w') as outfile:
                for i, line in enumerate(infile):
                    self.set_status_message("Lines read: %d" % i)
                    w = json.loads(line)
                    #print(w)
                    f.append(w)
                f = json.dumps(f)
                self.set_status_message("JSON created")
                #print(f)
                #g = Graph().parse(data=f, format='json-ld')
                r = requests.put('http://{fuseki}:{port}/{dataset}/data'.format(fuseki=self.host,
                                                                                port=self.port, dataset = self.dataset),
                    headers={'Content-Type':'application/ld+json'},
                    data=f)
                self.set_status_message("Data sent to fuseki")
                outfile.write(f)
