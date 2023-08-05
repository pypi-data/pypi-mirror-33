import json
from collections import Counter,OrderedDict

class DomainCountAggregator(object):

    def __init__(self, input_file):
        self.input_file = input_file
        self.data = None
        self.result = None

    def _load_input_file(self):
        """
        Load the contents of the input file, line per line

        :return:
            (list): each line representing a dictionary in the format
                used by the pipeline.
        """

        with open(self.input_file, 'r') as fd:
             return fd.readlines()

    @staticmethod
    def _get_domain_from_url(url):
        """
        Returns the domain name for a given URL.

        :args:
            url (str): the given URL

        :return:
            (str): the domain name
        """

        # TODO: improve how we get the domain form a given URL. There might be
        # many corner cases on this approach.

        domain = url.split('/')[2].split('?')[0].strip()

        try:
            return domain.strip()
        except IndexError:
            # we ignore it
            pass


    def get_result(self):
        """
        Prepare the result based on the input data and the product
        requirement.

        :return:
            result (dict): an OrderedDict that contains the domain name
                as a key and the amount of ocurences as value.url
        """
        domain_list = []

        data = self._load_input_file()

        for item in data:
            domain_list.append(self._get_domain_from_url(item))

        self.result = sorted(
                            Counter(domain_list).items(),
                            key=lambda t: t[1],
                            reverse=True
                        )

        return self.result
