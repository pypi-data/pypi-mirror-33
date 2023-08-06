"""
Given a 'new' item/class, with a set of db xrefs and a name, attempt to reconcile it with existing items in wikidata
If an exact match is found, retrieve it. Mark potential matches for intervention.

"""
import requests
from collections import defaultdict


search_string = "Genetic Disorder"
search_string = "Microdontia"

def get_choices(search_string):
    search_results = search_wikidata(search_string)
    wdids = [x['id'] for x in search_results]
    item_props = get_item_props(wdids)
    for search_result in search_results:
        search_result['p'] = item_props[search_result['id']]
    return search_results


def search_wikidata(search_string):
    url = 'https://www.wikidata.org/w/api.php'
    params = {
        'action': 'wbsearchentities',
        'language': 'en',
        'search': search_string,
        'format': 'json'
    }

    results = requests.get(url, params=params).json()

    if results['success'] != 1:
        raise ValueError('WD search failed')
    return results['search']


def get_item_props(wdid):
    """
    given values for properties props
    :param wdid:
    :return:
    """
    if isinstance(wdid, str):
        wdid = [wdid]
    url = 'https://www.wikidata.org/w/api.php'
    params = {
        'action': 'wbgetentities',
        'ids': '|'.join(wdid),
        'props': 'claims',
        'format': 'json'
    }

    api_results = requests.get(url, params=params).json()
    return parse_wdentities(api_results)


def parse_wdentities(api_results):
    results = {}
    for wdid, entity in api_results['entities'].items():
        results[wdid] = parse_wdentity(entity)

    return results


def parse_wdentity(entity):
    obj = defaultdict(set)
    claims = entity['claims']
    for prop_id, prop_claims in claims.items():
        for prop_claim in prop_claims:
            if prop_claim['mainsnak']['datatype'] in {'wikibase-item'}:
                obj[prop_id].add(prop_claim['mainsnak']['datavalue']['value']['id'])
            elif prop_claim['mainsnak']['datatype'] in {'external-id', 'string'}:
                obj[prop_id].add(prop_claim['mainsnak']['datavalue']['value'])
            elif prop_claim['mainsnak']['datatype'] in {'globe-coordinate', 'quantity', 'time', 'commonsMedia'}:
                if prop_id not in obj:
                    obj[prop_id] = {}
    return dict(obj)
