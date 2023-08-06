import requests


def query_single_edge(_input, _output, _value):
    """
        Retrieve results using one API call from input to output.
        :param _input: the input prefix, for a list of input prefix in BioThings Explorer, visit: http://biothings.io/explorer/api/v2/metadata/bioentities
        :param _output: the output prefix, for a list of output prefix in BioThings Explorer, visit: http://biothings.io/explorer/api/v2/metadata/bioentities
        :_value: The value of the input
        :return:
    """
    doc = requests.get('http://biothings.io/explorer/api/v2/directinput2output?input_prefix={{input}}&output_prefix={{output}}&input_value={{value}}&format=translator'.
                      replace("{{input}}", _input).replace("{{output}}", _output).replace("{{value}}", _value)).json()
    return doc