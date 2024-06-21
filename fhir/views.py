import asyncio
from utilities.epic_fhir_endpoints import get_mrn_patient_detail
from django.http import HttpResponse

def patient_from_mrn(request, mrn):
    
    res = asyncio.run(get_mrn_patient_detail(mrn))

    HttpResponse(res)
