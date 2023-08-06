import shodan
from robot.api import logger
import json

class RoboShodan(object):

    def __init__(self, shodan_api_key):
        self.shodan_api_key = shodan_api_key
        self.shodan_api = shodan.Shodan(self.shodan_api_key)

    def run_shodan_scan(self, results_path, target):
        self.results_path = results_path
        self.target = target
        result = self.shodan_api.host(self.target)
        file_name = 'shodan_{0}_result.json'.format(''.join(self.target.split('.')))
        with open('{0}/{1}'.format(self.results_path, file_name), 'w') as f:
            json.dump(result, f)
        logger.info("Successfully ran Shodan against the target. Please find the *.json file in the results directory")
