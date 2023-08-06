import urllib
import urllib.request
import urllib.parse
import time
import json

base_url = 'http://www.ebi.ac.uk/Tools/services/rest/iprscan5'


def rest_request(url, params=None):
    request = urllib.request.Request(url)

    if params is not None:
        params = urllib.parse.urlencode(params)
        params = params.encode(encoding='utf_8', errors='strict')

    response = urllib.request.urlopen(request, params)
    results = str(response.read(), 'utf-8')
    response.close()

    return results


def get_job(email, sequence):
    params = dict()
    params['email'] = email
    params['sequence'] = sequence

    request_url = base_url + '/run/'

    job_id = rest_request(
        request_url,
        params
    )

    return job_id


def get_status(job_id):
    request_url = base_url + '/status/' + job_id
    status = rest_request(request_url)

    return status


def get_result_types(job_id):
    request_url = base_url + '/resulttypes/' + job_id
    result_types = rest_request(request_url)

    return result_types


def get_result(job_id):
    "http://www.ebi.ac.uk/Tools/services/rest/iprscan5/result/iprscan5-R20180703-142444-0789-78686257-p1m/json"
    request_url = base_url + "/result/" + job_id + "/json"
    result = rest_request(request_url)

    return result


def extract_interpro_domains(json_data):
    interpro_domains = set()

    data = json.loads(json_data)

    # TODO: check if len(data['results']) > 1 (Is it possible ?)
    results = data['results'][0]
    matches = results['matches']

    for match in matches:
        signature = match['signature']

        if signature['entry'] is not None:
            interpro_domains.add(signature['entry']['accession'])

    return interpro_domains


def get_interpro_domains_from_sequence(email, sequence):
    job_id = get_job(
        email,
        sequence
    )

    status = 'RUNNING'

    while status == 'RUNNING' or status == 'PENDING':
        time.sleep(10)
        status = get_status(job_id)
        print(status)

    json_data = get_result(job_id)
    interpro_domains = extract_interpro_domains(json_data)

    return interpro_domains