import logging
import json
import boto3
from ask_amy.core.object_dictionary import ObjectDictionary

logger = logging.getLogger()


class DefaultHomeSkill(ObjectDictionary):
    def __init__(self, dialog_dict=None):
        super().__init__(dialog_dict)
        self._event = None
        self._intent_name = None
        self._sc_application_id = self.get_value_from_dict(['applicationId'])

    def begin(self, event_dict):
        logger.debug("**************** entering Dialog.begin")
        access_token = event_dict['payload']['accessToken']
        if event_dict['header']['namespace'] == 'Alexa.ConnectedHome.Discovery':
            return self.handle_discovery(event_dict)
        elif event_dict['header']['namespace'] == 'Alexa.ConnectedHome.Control':
            return self.handle_control(event_dict)

    def handle_discovery(self, event):
        header = {
            "namespace": "Alexa.ConnectedHome.Discovery",
            "name": "DiscoverAppliancesResponse",
            "payloadVersion": "2"
        }

        if event['header']['name'] == 'DiscoverAppliancesRequest':
            payload = {'discoveredAppliances': self._obj_dict['discoveredAppliances']}

            return {"header": header, "payload": payload}

    def handle_control(self, event):
        reply = {}
        device_id = event['payload']['appliance']['applianceId']
        message_id = event['header']['messageId']

        if event['header']['name'] == 'TurnOnRequest':
            self.on_off_request(device_id, True)
            reply = self.generate_response("TurnOnConfirmation", message_id, {})

        if event['header']['name'] == 'TurnOffRequest':
            self.on_off_request(device_id, False)
            reply = self.generate_response("TurnOffConfirmation", message_id, {})

        return reply

    def generate_response(self, name, message_id, payload):
        return {"header": {
            "messageId": message_id,
            "name": name,
            "namespace": "Alexa.ConnectedHome.Control",
            "payloadVersion": "2"},
            "payload": payload
        }

    def on_off_request(self, device_id, prop):
        client = boto3.client('iot-data', region_name='us-east-1')

        response = client.publish(
            topic=self._obj_dict['communication']['topic'],
            qos=self._obj_dict['communication']['qos'],
            payload=json.dumps({"state": {"desired": {device_id: prop}}})
        )
