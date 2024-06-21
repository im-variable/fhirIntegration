import aiohttp
import os
from .epic_fhir_config import get_api_headers

EPIC_ENDPOINT = os.getenv("EPIC_ENDPOINT")

async def make_request(session, url, headers):
    """
    # for making request using session
    """
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            return None
        

async def search_patient(mrn_no, headers):
    """
    ### for add and completing patient
    # for patient.search api with mrn no.
    """
    try:
        mrn_code = "MRN|" + str(mrn_no)
        api_endpoint = EPIC_ENDPOINT + "/api/FHIR/R4/Patient/?identifier=" + mrn_code

        data = {}
        async with aiohttp.ClientSession() as session:
            response = await make_request(session, api_endpoint, headers)

            if response is not None:
                resource = response.get('entry', [{}])[0].get('resource', {})
                data["mrn_no"] = mrn_no
                data["patient_id"] = resource['id'] # in case the patient id is not found i want to throw error 
                data["date_of_birth"] = resource.get('birthDate')
                data["gender"] = resource.get('gender')

                for extension in resource.get('extension'):

                    if 'us-core-race' in extension.get('url'):
                        for item in extension.get('extension'):
                            if 'valueString' in item:
                                data["race"] = item.get('valueString')
                                break

                    elif 'us-core-ethnicity' in extension.get('url'):
                        for item in extension.get('extension'):
                            if 'valueString' in item:
                                data["ethnicity"] = item.get('valueString')
                                break


                for name in resource.get('name'):
                    if 'official' in name['use']:
                        data["first_name"] = ' '.join(name.get('given', []))
                        data["last_name"] = name.get('family')
                        break
                
            return data

    except KeyError as e:
        raise e
    except Exception as e:
        raise e


async def get_mrn_patient_detail(mrn_no):
    """
    for calling all the apis required to fill patient detail
    mrn no - will be the epic patient mrn code
    scope - scope will be 
    add - to get patient detail for adding patient
    complete - to get patient detail when completing  
    """
    try:
        headers = get_api_headers()
        data = {}
        search_patient_res = await search_patient(mrn_no, headers)
        data.update(search_patient_res)

        return data
    except KeyError as e:
        raise e
    except Exception as e:
        raise e
