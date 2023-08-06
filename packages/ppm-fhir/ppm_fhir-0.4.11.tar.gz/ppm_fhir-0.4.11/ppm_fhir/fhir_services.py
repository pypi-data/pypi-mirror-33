from fhirclient.models.patient import Patient
from fhirclient.models.list import List, ListEntry
from fhirclient.models.organization import Organization
from fhirclient.models.researchstudy import ResearchStudy
from fhirclient.models.researchsubject import ResearchSubject
from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.coding import Coding
from fhirclient.models.flag import Flag
from fhirclient.models.fhirreference import FHIRReference
from fhirclient.models.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhirclient.models.period import Period
from fhirclient.models.fhirdate import FHIRDate

from ppm_fhir.fhir_response_processing import (flatten_consent,
                                                flatten_participants,
                                                flatten_questionnaire_response,
                                                flatten_participant,
                                                flatten_list,
                                                flatten_consent_composition,
                                                flatten_research_study,
                                                flatten_enrollment_flag,
                                               flatten_contract)
from ppm_fhir import fhir_resources

import hashlib
import requests
import furl
import base64
import json
from datetime import datetime
import uuid

import logging
logger = logging.getLogger(__name__)


class FHIRServices:

    FHIR_URL = None

    SNOMED_LOCATION_CODE = "SNOMED:43741000"
    SNOMED_VERSION_URI = "http://snomed.info/sct/900000000000207008"

    def __init__(self, fhir_url):
        self.FHIR_URL = fhir_url

    def _query_resources(self, resource_type, query=None):
        """
        This method will fetch all resources for a given type, including paged results.
        :param resource: FHIR resource type
        :type resource: str
        :param query: A dict of key value pairs for searching resources
        :type query: dict
        :return: A list of FHIR resource dicts
        :rtype: list
        """
        logger.debug('Query resource: {}'.format(resource_type))

        # Build the URL.
        url_builder = furl.furl(self.FHIR_URL)
        url_builder.path.add(resource_type)

        # Add query if passed and set a return count to a high number, despite the server
        # probably ignoring it.
        url_builder.query.params.add('_count', 1000)
        if query is not None:
            url_builder.query.params.update(query)

        # Prepare the final URL
        url = url_builder.url

        # Collect them.
        resources = []

        # The url will be set to none on the second iteration if all resources
        # were returned, or it will be set to the next page of resources if more exist.
        while url is not None:

            # Make the request.
            response = requests.get(url)
            response.raise_for_status()

            # Parse the JSON.
            bundle = response.json()
            if bundle.get('total', 0) > 0:
                resources.extend(bundle.get('entry'))

            # Check for a page.
            url = None

            for link in bundle.get('link', []):
                if link['relation'] == 'next':
                    url = link['url']

        return resources

    def _query_resource(self, resource_type, _id):
        logger.debug('Query resource "{}": {}'.format(resource_type, _id))

        # Build the URL.
        url_builder = furl.furl(self.FHIR_URL)
        url_builder.path.add(resource_type)
        url_builder.path.add(_id)

        # Make the request.
        response = requests.get(url_builder.url)
        response.raise_for_status()

        logger.debug('Response: {}'.format(response.status_code))

        return response.json()

    def point_of_care_update(self, email, point_of_care_list):
        """
        Replace current point of care list with submitted list.    

        :param email:
        :param point_of_care:
        :return:
        """
        logger.debug("Patient: {}".format(self.hash_email(email)))

        bundle_url = self.FHIR_URL

        # Retrieve patient identifier.
        patient_record = self.query_patient_record(email)
        patient_identifier = patient_record['entry'][0]['resource']['id']

        # This is a FHIR resources that allows references between resources.
        # Create one for referencing patients.
        patient_reference = FHIRReference()
        patient_reference.reference = "Patient/" + patient_identifier

        # The list will hold Organization resources representing where patients have received care.
        data_list = List()

        data_list.subject = patient_reference
        data_list.status = "current"
        data_list.mode = "working"

        # We use the SNOMED code for location to define the context of items added to the list.
        data_list.code = self.generate_snowmed_codeable(self.SNOMED_LOCATION_CODE)

        # This adds the list of Organization references.
        data_list.entry = self.generate_organization_references(point_of_care_list)

        # Start building the bundle. Bundles are used to submit multiple related resources.
        bundle_entries = []

        org_list = self.generate_organization_list(point_of_care_list)

        # Add Organization objects to bundle.
        for org in org_list:

            bundle_item_org_request = BundleEntryRequest()
            bundle_item_org_request.method = "POST"
            bundle_item_org_request.url = "Organization"

            # Don't recreate Organizations if we can find them by the exact name. No fuzzy matching.
            bundle_item_org_request.ifNoneExist = str(furl.Query({'name:exact': org.name}))

            bundle_item_org = BundleEntry()
            bundle_item_org.resource = org
            bundle_item_org.request = bundle_item_org_request

            bundle_entries.append(bundle_item_org)

        bundle_item_list_request = BundleEntryRequest()
        bundle_item_list_request.url = "List"
        bundle_item_list_request.method = "POST"
        bundle_item_list_request.ifNoneExist = str(furl.Query({'patient:Patient.identifier': 'http://schema.org/email|' + email,
                                                               'code': self.SNOMED_VERSION_URI + "|" + self.SNOMED_LOCATION_CODE,
                                                               'status': 'current'}))

        bundle_item_list = BundleEntry()
        bundle_item_list.resource = data_list
        bundle_item_list.request = bundle_item_list_request

        bundle_entries.append(bundle_item_list)

        # Create and send the full bundle.
        full_bundle = Bundle()
        full_bundle.entry = bundle_entries
        full_bundle.type = "transaction"

        response = requests.post(url=bundle_url, json=full_bundle.as_json())
        logger.debug('Response: {}'.format(response.status_code))

        return response

    def add_point_of_care(self, email, point_of_care):
        """
        Adds a point of care to a Participant's existing list and returns the flattened
        updated list of points of care (just a list with the name of the Organization).
        Will return the existing list if the point of care is already in the list. Will
        look for an existing Organization before creating.

        :param email: The participant's email address
        :param point_of_care: The name of the point of care
        :return: [str]
        """
        logger.debug("Add point of care: {}".format(point_of_care))

        # Get the flattened list
        points_of_care = self.query_list_record(email, flatten_return=True)

        # Check if the name exists in the list already
        for organization in points_of_care:
            if organization == point_of_care:
                logger.debug('Organization is already in List!')

                # Just return the list as is
                return points_of_care

        # Look for it
        organization_url = furl.furl(self.FHIR_URL)
        organization_url.path.add('Organization')
        organization_url.query.params.add('name', point_of_care)

        response = requests.get(organization_url.url)
        response.raise_for_status()

        results = response.json()
        if results['total'] >= 1:
            logger.debug('Found existing organization!')

            # Get the ID
            organization_id = 'Organization/{}'.format(results['entry'][0]['resource']['id'])
            logger.debug('Existing organization: {}'.format(organization_id))

        else:
            logger.debug('No existing organization, creating...')

            # Create the organization
            organization = Organization()
            organization.name = point_of_care

            # Add Organization objects to bundle.
            organization_request = BundleEntryRequest()
            organization_request.method = "POST"
            organization_request.url = "Organization"

            # Create the organization entry
            organization_entry = BundleEntry({'resource': organization.as_json()})
            organization_entry.request = organization_request

            # Validate it.
            bundle = Bundle()
            bundle.entry = [organization_entry]
            bundle.type = 'transaction'

            # Create the organization
            response = requests.post(self.FHIR_URL, json=bundle.as_json())
            response.raise_for_status()
            logger.debug('Organization POST response: {}'.format(response.status_code))

            organization_location = response.json()['entry'][0]['response']['location']
            parts = organization_location.split('/')
            organization_id = '{}/{}'.format(parts[0], parts[1])
            logger.debug('New Organization: {}'.format(organization_id))

        # Add it to the list
        point_of_care_list = self.query_list_record(email)['entry'][0]['resource']
        point_of_care_list['entry'].append({'item': {'reference': organization_id}})
        logger.debug('Updated List: {}'.format(point_of_care_list))

        # Patch it
        url = furl.furl(self.FHIR_URL)
        url.path.add('List')
        url.path.add(point_of_care_list['id'])
        logger.debug('List PUT URL: {}'.format(url.url))

        response = requests.put(url, data=json.dumps(point_of_care_list))
        response.raise_for_status()
        logger.debug('List PUT response: {}'.format(response))

        # Return the flattened list with the new organization
        points_of_care.append(point_of_care)

        return points_of_care

    def research_study_update(self, email, research_study_list):
        """
        Adds research studies for participant

        :param email:
        :param research_study_list:
        :return:
        """
        logger.debug("Patient: {}".format(self.hash_email(email)))

        # Retrieve patient reference.
        patient_record = self.query_patient_record(email)
        patient_identifier = patient_record['entry'][0]['resource']['id']
        patient_reference = FHIRReference()
        patient_reference.reference = "Patient/" + patient_identifier

        # Get or create the studies
        codes = {}
        for research_study_title in research_study_list:

            # Create temp identifier for the study
            research_study_id = uuid.uuid1().urn

            # Create the organization
            research_study = ResearchStudy()
            research_study.title = research_study_title
            research_study.status = 'completed'

            research_study_request = BundleEntryRequest({
                'url': 'ResearchStudy',
                'method': 'POST',
                'ifNoneExist': str(furl.Query({'title:exact': research_study_title}))
            })

            research_study_entry = BundleEntry({
                'resource': research_study.as_json(),
                'fullUrl': research_study_id
            })

            research_study_entry.request = research_study_request

            research_study_reference = FHIRReference()
            research_study_reference.reference = research_study_id

            # Create the subject
            research_subject = ResearchSubject()
            research_subject.study = research_study_reference
            research_subject.individual = patient_reference
            research_subject.status = 'completed'

            # Add Research Subject to bundle.
            research_subject_request = BundleEntryRequest()
            research_subject_request.method = "POST"
            research_subject_request.url = "ResearchSubject"

            # Create the Research Subject entry
            research_subject_entry = BundleEntry({
                'resource': research_subject.as_json()
            })
            research_subject_entry.request = research_subject_request

            # Validate it.
            bundle = Bundle()
            bundle.entry = [research_study_entry, research_subject_entry]
            bundle.type = 'transaction'

            logger.debug("Creating: {}".format(research_study_title))

            try:
                # Create the organization
                response = requests.post(self.FHIR_URL, json=bundle.as_json())
                logger.debug('Response: {}'.format(response.status_code))

                # Add it
                codes[research_study_title] = response.status_code

                response.raise_for_status()

            except Exception as e:
                logger.exception(e)
                logger.error('{} - Could not save research study: {}'
                             .format(self.hash_email(email), research_study_title))

        return codes

    def add_research_study(self, email, research_study):
        """
        Adds a research study to a Participant's existing list and returns the flattened
        updated list of research studies (just a list with the name of the research study).
        Will return the existing list if the point of care is already in the list. Will
        look for an existing ResearchStudy before creating.

        :param email: The participant's email address
        :param research_study: The name of the research study
        :return: [str]
        """
        logger.debug("Add research study: {}".format(research_study))

        # Call the update
        self.research_study_update(email, [research_study])

        # Get the new list
        research_studies = self.query_research_studies(email, flatten_return=True)

        return research_studies

    def query_research_studies(self, participant_email, flatten_return=False):
        logger.debug("Patient: {}".format(self.hash_email(participant_email)))

        # Build the FHIR QuestionnaireResponse URL.
        research_subject_url = furl.furl(self.FHIR_URL)
        research_subject_url.path.add('ResearchSubject')
        research_subject_url.query.params.add('individual:Patient.identifier', 'http://schema.org/email|' + participant_email)

        # Make the FHIR request.
        research_subject_response = requests.get(research_subject_url.url)
        logger.debug('Response: {}'.format(research_subject_response.status_code))

        # Get studies
        research_study_ids = []
        for subject in research_subject_response.json().get('entry', []):

            # Get the ID
            research_study_id = subject['resource']['study']['reference']
            research_study_ids.append(research_study_id)

        logger.debug('Found {} Research Studies'.format(len(research_study_ids)))

        # Ensure we have subjects to query on
        if len(research_study_ids) > 0:

            # Make the query
            research_study_url = furl.furl(self.FHIR_URL)
            research_study_url.path.add('ResearchStudy')
            research_study_url.query.params.add('_id', ','.join(research_study_ids))

            research_study_response = requests.get(research_study_url.url)
            logger.debug('Study response: {}'.format(research_study_response.status_code))

            # Get the IDs
            research_studies = research_study_response.json().get('entry', [])

            # Check for flattening
            if flatten_return:

                # Collect resource dicts
                research_studies_flat = []
                for research_study in research_studies:
                    research_studies_flat.append(flatten_research_study(research_study))

                return research_studies_flat

            else:
                return research_studies

        else:

            # No studies to search for so return empty list
            if flatten_return:
                return []

            # Or return empty FHIR bundle
            else:
                return fhir_resources.bundle([], self.FHIR_URL)

    def generate_snowmed_codeable(self, snomed_code):
        """
        When submitting a code to fire it needs to be in a nested set of resources. This builds them based on a code and URI.
        :param snomed_code:
        :return:
        """
        snomed_coding = Coding()
        snomed_coding.system = self.SNOMED_VERSION_URI
        snomed_coding.code = snomed_code

        snomed_codable = CodeableConcept()
        snomed_codable.coding = [snomed_coding]

        return snomed_codable

    def generate_organization_list(self, point_of_care_list):
        """
        Creates Organization resources with names equal to each item in the passed in list.
        :param point_of_care_list:
        :return:
        """
        org_list = []
        org_number = 1

        for point_of_care in point_of_care_list:

            new_poc = Organization()

            new_poc.id = "org" + str(org_number)
            new_poc.name = point_of_care

            org_list.append(new_poc)
            org_number += 1

        return org_list

    def generate_organization_references(self, point_of_care_list):
        """
        When referencing resources in FHIR you need to create a reference resource.
        Create the reference for Organizations here.
        :param point_of_care_list:
        :return:
        """
        entry_list = []
        org_number = 1

        for point_of_care in point_of_care_list:

            new_org_reference = FHIRReference()
            new_org_reference.reference = "Organization/org" + str(org_number)
            new_list_entry = ListEntry()

            new_list_entry.item = new_org_reference
            entry_list.append(new_list_entry)
            org_number += 1

        return entry_list

    def query_list_record(self, email, code_system=SNOMED_VERSION_URI, code=SNOMED_LOCATION_CODE, flatten_return=False):
        """
        Query the list object which has a patient and a snomed code. If it exists we'll need the URL to update the object later.
        :param email:
        :param code_system:
        :param code:
        :return:
        """
        logger.debug("Patient: {}".format(self.hash_email(email)))

        url = self.FHIR_URL + '/List'

        query = {
            'patient:Patient.identifier': 'http://schema.org/email|' + email,
            'code': code_system + "|" + code,
            'status': 'current',
            '_include': "List:item"
        }

        response = requests.get(url, params=query)
        logger.debug('Response: {}'.format(response.status_code))

        if flatten_return:
            response_json = flatten_list(response.json())
        else:
            response_json = response.json()

        return response_json

    def get_patient_record(self, fhir_id, flatten_return=True):
        logger.debug("Patient: {}".format(fhir_id))

        url = self.FHIR_URL + '/Patient'
        query = {
            '_id': fhir_id,
        }

        response = requests.get(url, params=query)
        logger.debug('Response: {}'.format(response.status_code))

        # Parse it
        response_json = response.json()

        if flatten_return:
            return flatten_participant(response_json)

        return response_json

    def get_patient_everything(self, fhir_id):
        logger.debug("Patient: {}".format(fhir_id))

        url = "{}/Patient/{}/$everything".format(self.FHIR_URL, fhir_id)
        response = requests.get(url).json()
        logger.debug('Response: {}'.format(response.status_code))

        return response

    def query_patient_record(self, email=None, flatten_return=False):
        """ Get the patient record from the FHIR server.

        :param email: A patient's email address.
        :return: JSON Record of Patient
        """
        logger.debug("Patient: {}".format(self.hash_email(email)))

        url = self.FHIR_URL + '/Patient'

        if email is not None:
            logger.debug('Query by email')

            # Search for the patient with the given email
            query = {
                'identifier': 'http://schema.org/email|' + email,
            }

            # Make the request
            response_json = requests.get(url, params=query).json()

            # Check for processing
            if flatten_return:
                return flatten_participant(response_json)

            else:
                return response_json

        else:
            logger.debug('Query all resources')

            # Get all resources.
            resources = self._query_resources('Patient')

            # Check for processing.
            if flatten_return:

                # Flatten and return
                return flatten_participants(resources)

            else:

                # Emulate a bundle of resources
                return fhir_resources.bundle(resources, self.FHIR_URL + '/Patient')

    def query_questionnaire_responses(self, email=None, questionnaire_id=None, flatten_return=False):
        """
        Fetch QuestionnaireResponse and Questionnaire resources for the given patient and questionnaire ID
        :param email: The email of the user for which the Q and QRs should be fetched
        :type email: str
        :param questionnaire_id: The ID of the Questionnaire resource to fetch
        :type questionnaire_id: str
        :param flatten_return: Whether the response should be parsed and trimmed to the relevant bits
        :type flatten_return: bool
        :return: A dict of the full response or the flattened response
        :rtype: dict
        """
        logger.debug("Patient: {}".format(self.hash_email(email)))
        logger.debug('Questionnaire ID: {}'.format(questionnaire_id))

        # Build the FHIR QuestionnaireResponse URL.
        url = self.FHIR_URL + '/QuestionnaireResponse'

        # Get only "proposed" Consent resources
        query = {
            '_include': 'QuestionnaireResponse:questionnaire',
        }

        if email:
            query['source:Patient.identifier'] = 'http://schema.org/email|' + email

        if questionnaire_id:
            query['questionnaire'] = questionnaire_id

        response = requests.get(url, params=query)
        logger.debug('Response: {}'.format(response.status_code))

        if flatten_return:
            response_json = flatten_questionnaire_response(response.json())
        else:
            response_json = response.json()

        return response_json

    def query_document_reference(self, subject=None):
        logger.debug("Subject: {}".format(subject))

        url = self.FHIR_URL + '/DocumentReference'

        query = {}

        if subject:
            query['subject'] = subject

        response = requests.get(url, params=query)
        logger.debug('Response: {}'.format(response.status_code))

        return response.json()

    def query_user_composition(self, user_id, flatten_return=False):
        logger.debug("Patient: {}".format(user_id))

        # Build the FHIR QuestionnaireResponse URL.
        url = self.FHIR_URL + '/Composition'

        query = {
            'patient': user_id,
            '_include': "*"
        }

        # Make the FHIR request.
        response = requests.get(url, params=query)
        logger.debug('Response: {}'.format(response.status_code))

        if flatten_return:
            response_json = flatten_consent_composition(response.json(), self.FHIR_URL)
        else:
            response_json = response.json()

        return response_json

    def query_user_consent(self, email, flatten_return=False):
        """ Ask the FHIR server if this user has completed the questionnaire.

        This will return all Consent resources, with any status. If you are only
        interested in Consent resources that have been approved, filter the results
        by "status == active".
        """
        logger.debug("Patient: {}".format(self.hash_email(email)))

        # Build the FHIR QuestionnaireResponse URL.
        url = self.FHIR_URL + '/Consent'

        # Structure the query so that we don't need to know the user's FHIR id.
        query = {
            'patient:Patient.identifier': 'http://schema.org/email|' + email,
        }

        # Make the FHIR request.
        response = requests.get(url, params=query)
        logger.debug('Response: {}'.format(response.status_code))

        if flatten_return:
            response_json = flatten_consent(response.json())
        else:
            response_json = response.json()

        return response_json

    def query_user_contract(self, participant_email, flatten_return=False):
        logger.debug("Patient: {}".format(self.hash_email(participant_email)))

        # Build the FHIR QuestionnaireResponse URL.
        url = self.FHIR_URL + '/Contract'

        # Structure the query so that we don't need to know the user's FHIR id.
        query = {
            'signer:Patient.identifier': 'http://schema.org/email|' + participant_email,
        }

        # Make the FHIR request.
        response = requests.get(url, params=query)
        logger.debug('Response: {}'.format(response.status_code))

        if flatten_return:
            return flatten_contract(response.json())
        else:
            return response.json()

    def query_guardian_contract(self, participant_email, flatten_return=False):
        logger.debug("Patient: {}".format(self.hash_email(participant_email)))

        # Build the FHIR QuestionnaireResponse URL.
        url = self.FHIR_URL + '/Contract'

        # Structure the query so that we don't need to know the user's FHIR id.
        query = {
            'signer.patient:Patient.identifier': 'http://schema.org/email|' + participant_email,
        }

        # Make the FHIR request.
        response = requests.get(url, params=query)
        logger.debug('Response: {}'.format(response.status_code))

        if flatten_return:
            return flatten_contract(response.json())
        else:
            return response.json()

    def update_FHIR_object(self, object):
        """ Send an updated consent object to the FHIR server.

        :param user_consent: Consent object as it is pulled and updated from the FHIR server.
        :return:
        """

        try:
            # Get the object resource
            resource = object['resource']

            # Get the URL and make sure it's using SSL
            object_url = furl.furl(self.FHIR_URL)
            object_url.path.segments.extend([resource['resourceType'], resource['id']])

            logger.debug('Update object at: {}'.format(object_url.url))

            # Make the FHIR request.
            response = requests.put(object_url.url, json=resource)

            logger.debug('Response: {}'.format(response.status_code))

            try:
                query_status = response.json()['text']['status']
            except (KeyError, IndexError) as e:
                logger.exception(e)
                query_status = "failed"

        except (KeyError, IndexError) as e:
            logger.exception(e)
            query_status = "failed"

        return query_status

    def update_user_consent(self, user_consent):
        """ Send an updated consent object to the FHIR server.

        :param user_consent: Consent object as it is pulled and updated from the FHIR server.
        :return:
        """

        try:
            # Get the URL and make sure it's using SSL
            consent_url = furl.furl(self.FHIR_URL)
            consent_url.path.segments.extend(['Consent', user_consent['resource']['id']])

            logger.debug('Update consent at URL: {}'.format(consent_url.url))

            # Get the resource
            user_data = user_consent['resource']

            # Make the FHIR request.
            response = requests.put(consent_url.url, json=user_data)

            logger.debug('Response: {}'.format(response.status_code))

            try:
                query_status = response.json()['text']['status']
            except (KeyError, IndexError):
                query_status = "failed"
        except (KeyError, IndexError):
            query_status = "failed"

        return query_status

    def query_patients_by_enrollment(self, enroll_status):
        logger.debug('Enroll status: {}'.format(enroll_status))

        # Build the FHIR URL.
        url = furl.furl(self.FHIR_URL)
        url.path.segments.append('Flag')

        # Get all flags with the passed enroll status. Since Flag does not permit searching based
        # on 'code' or 'status' or any other relevant property, we will search based on the whole
        # text description of the resource. This is shaky at best.
        # TODO: Hopefully optimize this with a more concrete method of querying
        query = {
            '_content': enroll_status,
            '_include': 'Flag:patient',
        }

        response = requests.get(url.url, params=query)

        # Setup a list to hold Patient resources.
        patients = []
        try:
            # Parse the response.
            data = response.json()
            if 'entry' in data and len(data['entry']) > 0:

                # Filter out Flags.
                patients = [entry for entry in data['entry'] if entry['resource']['resourceType'] == 'Patient']

        except Exception as e:
            logger.exception('Exception: {}'.format(e))

        finally:
            logger.debug('{} patients returned'.format(len(patients)))
            return patients

    def query_enrollment_flag(self, email, flatten_return=False):
        logger.debug("Patient: {}".format(self.hash_email(email)))

        # Build the FHIR Consent URL.
        url = self.FHIR_URL + '/Flag'

        # Get flags for current user
        query = {
            'subject:Patient.identifier': 'http://schema.org/email|' + email
        }

        try:
            # Make the FHIR request.
            response = requests.get(url, params=query)
            logger.debug('Response: {}'.format(response.status_code))

            if flatten_return:
                return flatten_enrollment_flag(response.json())
            else:
                return response.json()

        except KeyError as e:
            logger.exception(e)

            raise

    def query_enrollment_accepted_date(self, email):
        """ Returns the date that the patient was accepted for enrollment in their current program.
        """
        logger.debug("Patient: {}".format(self.hash_email(email)))

        try:
            # Make the FHIR request.
            response = self.query_enrollment_flag(email)

            # Parse the bundle.
            bundle = Bundle(response)
            if bundle.total > 0:

                # Check flags.
                for flag in [entry.resource for entry in bundle.entry if entry.resource.resource_type == 'Flag']:

                    # Get the code's value
                    approved_date = flag.period.start.date
                    logger.debug('Fetched approved date "{}" for user'.format(approved_date))

                    return approved_date

            else:
                logger.error('No flag found for user!')

            return None

        except KeyError as e:
            logger.exception(e)

            raise

    def get_enrollment_status(self, fhir_id):
        logger.debug("Patient: {}".format(fhir_id))

        try:
            # Build the FHIR Consent URL.
            url = self.FHIR_URL + '/Flag'

            # Get flags for current user
            query = {
                'subject': fhir_id
            }

            # Make the FHIR request.
            response = requests.get(url, params=query)
            logger.debug('Response: {}'.format(response.status_code))

            # Parse the bundle.
            bundle = Bundle(response.json())
            if bundle.total > 0:

                # Check flags.
                for flag in [entry.resource for entry in bundle.entry if entry.resource.resource_type == 'Flag']:

                    # Get the code's value
                    state = flag.code.coding[0].code
                    logger.debug('Fetched state "{}" for user'.format(state))

                    return state

            else:
                logger.error('No flag found for user!')

            return None

        except KeyError as e:
            logger.exception(e)

            return None

    def query_enrollment_status(self, email):
        logger.debug("Patient: {}".format(self.hash_email(email)))

        try:
            # Make the FHIR request.
            response = self.query_enrollment_flag(email)

            # Parse the bundle.
            bundle = Bundle(response)
            if bundle.total > 0:

                # Check flags.
                for flag in [entry.resource for entry in bundle.entry if entry.resource.resource_type == 'Flag']:

                    # Get the code's value
                    state = flag.code.coding[0].code
                    logger.debug('Fetched state "{}" for user'.format(state))

                    return state

            else:
                logger.error('No flag found for user!')

            return None

        except KeyError as e:
            logger.exception(e)

            raise

    def query_consents_by_status(self, status):
        """
        Ask the FHIR server for any Consent resources still pending.
        :param status:
        :return:
        """
        logger.debug("Status: {}".format(status))

        # Build the FHIR Consent URL.
        url = self.FHIR_URL + '/Consent'

        # Get only "proposed" Consent resources
        query = {
            'status': status,
            '_include': 'Consent:patient',
        }

        # Make the FHIR request.
        response = requests.get(url, params=query)
        logger.debug('Response: {}'.format(response.status_code))

        return response.json()

    def query_questionnaire_response_by_status(self, status, questionnaire):
        """
        Ask the FHIR server for any Questionnaire resources still pending.
        :param status: The status of the response
        :param questionnaire: The FHIR id of the questionnaire the responses belong to
        :return:
        """
        logger.debug('Status: {}, Questionnaire ID: {}'.format(status, questionnaire))

        # Build the FHIR Consent URL.
        url = self.FHIR_URL + '/QuestionnaireResponse'

        # Get only "proposed" Consent resources
        query = {
            'status': status,
            'questionnaire': questionnaire,
            '_include': 'QuestionnaireResponse:source',
        }

        # Make the FHIR request.
        response = requests.get(url, params=query)
        logger.debug('Response: {}'.format(response.status_code))

        return response.json()

    def create_user_in_fhir_server(self, form):
        """
        Create a Patient resource in the FHIR server.
        :param form:
        :return:
        """
        logger.debug("Patient: {}".format(self.hash_email(form.get('email'))))

        # Build a FHIR-structured Patient resource.
        patient_data = {
            'resourceType': 'Patient',
            'active': True,
            'identifier': [
                {
                    'system': 'http://schema.org/email',
                    'value': form.get('email'),
                },
            ],
            'name': [
                {
                    'use': 'official',
                    'family': form.get('lastname'),
                    'given': [form.get('firstname')],
                },
            ],
            'address': [
                {
                    'line': [
                        form.get('street_address1'),
                        form.get('street_address2'),
                    ],
                    'city': form.get('city'),
                    'postalCode': form.get('zip'),
                    'state': form.get('state'),
                }
            ],
            'telecom': [
                {
                    'system': 'phone',
                    'value': form.get('phone'),
                },
            ],
        }

        if form.get('contact_email'):
            logger.debug('Adding contact email')
            patient_data['telecom'].append({
                'system': 'email',
                'value': form.get('contact_email'),
            })

        if form.get('how_did_you_hear_about_us'):
            logger.debug('Adding "How did you hear about is"')
            patient_data['extension'] = [
                {
                    "url" : "https://p2m2.dbmi.hms.harvard.edu/fhir/StructureDefinition/how-did-you-hear-about-us",
                    "valueString" : form.get('how_did_you_hear_about_us')
                }
            ]

        # Convert the twitter handle to a URL
        if form.get('twitter_handle'):
            logger.debug('Adding Twitter handle')
            patient_data['telecom'].append({
                'system': 'other',
                'value': 'https://twitter.com/' + form['twitter_handle'],
            })

        try:

            # Create a placeholder ID for the patient the flag can reference.
            patient_id = uuid.uuid1().urn

            # Use the FHIR client lib to validate our resource.
            # "If-None-Exist" can be used for conditional create operations in FHIR.
            # If there is already a Patient resource identified by the provided email
            # address, no duplicate records will be created.
            Patient(patient_data)

            patient_request = BundleEntryRequest({
                'url': 'Patient',
                'method': 'POST',
                'ifNoneExist': str(furl.Query({
                    'identifier': 'http://schema.org/email|' + form.get('email'),
                }))
            })
            patient_entry = BundleEntry({
                'resource': patient_data,
                'fullUrl': patient_id
            })
            patient_entry.request = patient_request

            # Validate.
            flag = Flag(fhir_resources.enrollment_flag(patient_id, 'registered'))
            flag_request = BundleEntryRequest({'url': 'Flag', 'method': 'POST'})
            flag_entry = BundleEntry({'resource': flag.as_json()})
            flag_entry.request = flag_request

            # Validate it.
            bundle = Bundle()
            bundle.entry = [patient_entry, flag_entry]
            bundle.type = 'transaction'

            logger.debug("Creating...")

            # Create the Patient and Flag on the FHIR server.
            # If we needed the Patient resource id, we could follow the redirect
            # returned from a successful POST operation, and get the id out of the
            # new resource. We don't though, so we can save an HTTP request.
            response = requests.post(self.FHIR_URL, json=bundle.as_json())
            logger.debug('Response: {}'.format(response.status_code))

        except Exception as e:
            logger.exception(e)
            raise

    def attach_json_to_participant_record(self, patient_id, json_blob, json_description):
        """

        :param patient_id:
        :param json_blob:
        :param json_description:
        :return:
        """
        logger.debug("Patient: {}".format(patient_id))

        encoded_json = base64.b64encode(json.dumps(json_blob).encode()).decode('utf-8')

        data = {
            'resourceType': 'DocumentReference',
            "subject": {
                "reference": "Patient/" + patient_id
            },
            "type": {
                "text": json_description
            },
            "status": "current",
            "content": [{
               "attachment": {
                   "contentType": "application/json",
                   "language": "en-US",
                   "data": encoded_json
               }
            }]
        }

        url = self.FHIR_URL + "/DocumentReference"
        response = requests.post(url, json=data)
        logger.debug('Response: {}'.format(response.status_code))

        return response

    def update_twitter_handle(self, email, twitter_handle):
        """

        :param email:
        :param twitter_handle:
        :return:
        """
        logger.debug("Patient: {}".format(self.hash_email(email)))

        found_twitter_entry = False

        current_participant_record = self.query_patient_record(email)['entry'][0]

        for telecom in current_participant_record['resource']['telecom']:
            if telecom['system'] == "other" and telecom['value'].startswith("https://twitter.com"):
                telecom['value'] = 'https://twitter.com/' + twitter_handle
                found_twitter_entry = True

        if not found_twitter_entry:
            current_participant_record['resource']['telecom'].append({
                'system': 'other',
                'value': 'https://twitter.com/' + twitter_handle,
            })

        self.update_FHIR_object(current_participant_record)

    def twitter_handle_from_bundle(self, participant_bundle):
        """

        :param participant_bundle:
        :return:
        """
        logger.debug('Getting Twitter handle from bundle...')

        try:
            for telecom in participant_bundle['resource']['telecom']:
                if telecom['system'] == "other" and telecom['value'].startswith("https://twitter.com"):
                    return telecom['value']
        except (KeyError, IndexError):
            print("Twitter Handle not found where expected.")

        return None

    def update_patient_enrollment(self, patient_id, status):
        logger.debug("Patient: {}, Status: {}".format(patient_id, status))

        # Fetch the flag.
        url = furl.furl(self.FHIR_URL)
        url.path.segments.append('Flag')

        query = {
            'subject': 'Patient/{}'.format(patient_id),
        }

        try:
            # Fetch the flag.
            response = requests.get(url.url, params=query)
            flag_entries = Bundle(response.json())

            # Check for nothing.
            if flag_entries.total == 0:
                logger.debug('Creating enrollment flag for patient')

                # Create it.
                return self.create_patient_enrollment('Patient/{}'.format(patient_id), status)

            else:
                logger.debug('Existing enrollment flag found')

                # Get the first and only flag.
                entry = flag_entries.entry[0]
                flag = entry.resource
                code = flag.code.coding[0]

                # Update flag properties for particular states.
                logger.debug('Current status: {}'.format(code.code))
                if code.code != 'accepted' and status == 'accepted':
                    logger.debug('Setting enrollment flag status to "active"')

                    # Set status.
                    flag.status = 'active'

                    # Set a start date.
                    now = FHIRDate(datetime.now().isoformat())
                    period = Period()
                    period.start = now
                    flag.period = period

                elif code.code != 'terminated' and status == 'terminated':
                    logger.debug('Setting enrollment flag status to "inactive"')

                    # Set status.
                    flag.status = 'inactive'

                    # Set an end date.
                    now = FHIRDate(datetime.now().isoformat())
                    flag.period.end = now

                elif code.code == 'accepted' and status != 'accepted':
                    logger.debug('Reverting back to inactive with no dates')

                    # Flag defaults to inactive with no start or end dates.
                    flag.status = 'inactive'
                    flag.period = None

                else:
                    logger.error('Unhandled flag update: {} -> {}'.format(code.code, status))

                # Set the code.
                code.code = status
                code.display = status.title()
                flag.code.text = status.title()

                # Build the URL
                flag_url = furl.furl(self.FHIR_URL)
                flag_url.path.segments.extend(['Flag', flag.id])

                logger.debug('Updating Flag "{}" with code: "{}"'.format(flag_url.url, status))

                # Post it.
                response = requests.put(flag_url.url, json=flag.as_json())
                logger.debug('Response: {}'.format(response.status_code))

                return response

        except Exception as e:
            logger.exception(e)
            raise

    def create_patient_enrollment(self, patient_id, status='registered'):
        """
        Create a Flag resource in the FHIR server to indicate a user's enrollment.
        :param patient_id:
        :param status:
        :return:
        """
        logger.debug("Patient: {}".format(patient_id))

        # Use the FHIR client lib to validate our resource.
        flag = Flag(fhir_resources.enrollment_flag(patient_id, status))

        # Set a date if enrolled.
        if status == 'accepted':
            now = FHIRDate(datetime.now().isoformat())
            period = Period()
            period.start = now
            flag.period = period

        # Build the FHIR Flag destination URL.
        url = furl.furl(self.FHIR_URL)
        url.path.segments.append('Flag')

        logger.debug('Creating flag at: {}'.format(url.url))

        response = requests.post(url.url, json=flag.as_json())
        logger.debug('Response: {}'.format(response.status_code))

        return response

    def remove_patient(self, participant_email, consent_questionnaire_id=None, questionnaire_id=None):
        logger.debug("Patient: {}".format(self.hash_email(participant_email)))
        logger.debug('Consent Questionnaire ID: {}, Questionnaire ID: {}'.format(consent_questionnaire_id, questionnaire_id))

        patient_json = self.query_patient_record(participant_email)

        try:
            patient_id_to_remove = patient_json['entry'][0]['resource']['id']
            logger.debug("Patient ID: {}".format(patient_id_to_remove))
        except (KeyError, IndexError) as e:
            logger.exception(e)
            logger.error('Could not find patient to remove.')
            return

        # Before removing a patient, everything else (if available) must be removed
        self.remove_enrollment_flag(participant_email)
        self.remove_consent(participant_email)
        self.remove_point_of_care_list(participant_email)
        self.remove_questionnaire(participant_email, consent_questionnaire_id)
        self.remove_consent_response(participant_email, questionnaire_id)

        # Build the FHIR Patient URL.
        url = self.FHIR_URL + '/Patient/' + patient_id_to_remove

        # Make the FHIR request.
        response = requests.delete(url)

        return response

    def remove_all(self, source_resource_type, source_resource_id, target_resource_types=[]):
        """
        Removes a source resource and all of its related resources. Delete is done in a transaction
        so if an error occurs, the system will revert to its original state (in theory). This
        seems to bypass dependency issues and will just delete everything with impunity so
        use with caution.
        :param source_resource_type: The FHIR resource type of the source resource (e.g. Patient)
        :type source_resource_type: String
        :param source_resource_id: The FHIR id of the source resource
        :type source_resource_id: String
        :param target_resource_types: The resource types which should all be deleted if related to the source
        resource
        :type target_resource_types: [String]
        :return: Whether the delete succeeded or not
        :rtype: Bool
        """
        logger.debug("Target resource: {}/{}".format(source_resource_type, source_resource_id))
        logger.debug('Target related resources: {}'.format(target_resource_types))

        source_url = furl.furl(self.FHIR_URL)
        source_url.path.add(source_resource_type)
        source_url.query.params.add('_id', source_resource_id)
        source_url.query.params.add('_include', '*')
        source_url.query.params.add('_revinclude', '*')

        # Make the request.
        source_response = requests.get(source_url.url)
        source_response.raise_for_status()

        # Build the initial delete transaction bundle.
        transaction = {
            'resourceType': 'Bundle',
            'type': 'transaction',
            'entry': []
        }

        # Fetch IDs
        entries = source_response.json().get('entry', [])
        for resource in [entry['resource'] for entry in entries
                         if entry.get('resource') is not None
                            and entry['resource']['resourceType'] in target_resource_types]:
            # Get the ID and resource type
            _id = resource.get('id')
            resource_type = resource.get('resourceType')

            # Form the resource ID/URL
            resource_id = '{}/{}'.format(resource_type, _id)

            # Add it.
            logger.debug('Add: {}'.format(resource_id))
            transaction['entry'].append({
                'request': {
                    'url': resource_id,
                    'method': 'DELETE'
                }
            })

        logger.debug('Delete request: {}'.format(json.dumps(transaction)))

        # Do the delete.
        response = requests.post(self.FHIR_URL, headers={'content-type': 'application/json'},
                                 data=json.dumps(transaction))
        response.raise_for_status()

        # Log it.
        logger.debug('Delete response: {}'.format(response.content))
        logger.debug('Successfully deleted all for resource: {}/{}'.format(source_resource_type, source_resource_id))

        return response

    def remove_consent(self, participant_email):
        logger.debug("Patient: {}".format(self.hash_email(participant_email)))

        # We could search by e-mail, but let's grab the participant subject ID here.
        participant_info = self.query_patient_record(participant_email, True)

        # Composition is what we package the consents in. Need to delete it before deleting consent.
        composition_json = self.query_user_composition(participant_info["fhir_id"], flatten_return=False)

        # Grab the consent to remove.
        consent_json = self.query_user_consent(participant_email)

        # Get the contract.
        contract_json = self.query_user_contract(participant_email)

        try:
            composition_id_to_remove = composition_json['entry'][0]['resource']['id']

            # Delete composition record.
            requests.delete(self.FHIR_URL + '/Composition/' + composition_id_to_remove)

        except (KeyError, IndexError):
            logger.debug('Could not find composition to remove.')

        try:
            consent_id_to_remove = consent_json['entry'][0]['resource']['id']

            # Delete consent record.
            requests.delete(self.FHIR_URL + '/Consent/' + consent_id_to_remove)

        except (KeyError, IndexError):
            logger.debug('Could not find consent to remove.')
            return

        try:
            contract_id_to_remove = contract_json['entry'][0]['resource']['id']

            # Delete contract record.
            requests.delete(self.FHIR_URL + '/Contract/' + contract_id_to_remove)

        except (KeyError, IndexError):
            logger.debug('Could not find contract to remove.')
            return

        # Check for guardian contracts.
        guardian_contract_json = self.query_guardian_contract(participant_email)
        if guardian_contract_json.get('entry'):
            for contract in guardian_contract_json['entry']:

                # Get the id.
                try:
                    contract_id_to_remove = contract['resource']['id']

                    # Do the delete.
                    requests.delete(self.FHIR_URL + '/Contract/' + contract_id_to_remove)

                except (KeyError, IndexError):
                    logger.debug('Could not find guardian contract to remove.')

        return

    def remove_point_of_care_list(self, participant_email):
        logger.debug("Patient: {}".format(self.hash_email(participant_email)))

        list_record = self.query_list_record(participant_email)
        try:
            for list_entry in list_record["entry"]:
                if list_entry['resource']['resourceType'] == "List":
                    url = self.FHIR_URL + '/List/' + list_entry['resource']['id']
                    requests.delete(url)
        except (KeyError, IndexError):
            logger.debug('Could not find POC.')
            return
        return

    def remove_consent_response(self, participant_email, questionnaire_id):
        logger.debug("Patient: {}".format(self.hash_email(participant_email)))

        consent_responses = self.query_questionnaire_responses(participant_email, questionnaire_id)
        try:
            for response_consent in consent_responses["entry"]:
                url = self.FHIR_URL + '/QuestionnaireResponse/' + response_consent['resource']['id']
                requests.delete(url)
        except (KeyError, IndexError):
            logger.debug("Could not find consent response to "
                         "remove for questionnaire ID: {}.".format(questionnaire_id))
            return

    def remove_questionnaire(self, participant_email, questionnaire_id):
        logger.debug("Patient: {}".format(self.hash_email(participant_email)))

        questionnaire_responses = self.query_questionnaire_responses(participant_email, questionnaire_id)
        try:
            for questionnaire_response in questionnaire_responses["entry"]:
                if questionnaire_response['resource']['resourceType'] == "QuestionnaireResponse":
                    url = self.FHIR_URL + '/QuestionnaireResponse/' + questionnaire_response['resource']['id']
                    requests.delete(url)
        except (KeyError, IndexError):
            logger.debug("Could not find questionnaire to remove for ID: {}.".format(questionnaire_id))
            return
        return

    def remove_enrollment_flag(self, participant_email):
        logger.debug("Patient: {}".format(self.hash_email(participant_email)))

        flag = self.query_enrollment_flag(participant_email)
        try:
            url = self.FHIR_URL + '/Flag/' + flag['entry'][0]['resource']['id']
            requests.delete(url)
        except (KeyError, IndexError):
            logger.debug('Could not find enrollment flag to remove.')
            return
        return

    @staticmethod
    def hash_email(email, length=8):
        if email:
            return hashlib.sha1(email.encode()).hexdigest()[:length]
        else:
            return '-----'
