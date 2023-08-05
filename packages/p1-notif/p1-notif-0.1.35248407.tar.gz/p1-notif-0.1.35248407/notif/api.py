
import json
import requests

from .constants import K_NOTIF_API_URL


class NotifApi:

    def __init__(self, notif_service_url=K_NOTIF_API_URL):
        self.notif_service_url = notif_service_url

    def bulk_send(self, notifications):
        notification_body_list = []
        attachments = []
        for index, notif in enumerate(notifications):
            notification_body_list += [{
                'data': notif.json(),
                'type': notif.notif_type(),
            }]
            for attachment in notif.attachments():
                attachments += [('attachment_%d' % index, attachment)]
        body = json.dumps(notification_body_list)

        if len(attachments) > 0:
            response = requests.post(
                self.notif_service_url,
                data={'body': body},
                files=attachments
            )
        else:
            response = requests.post(
                self.notif_service_url,
                headers={'Content-Type': 'application/json'},
                data=body,
            )

        if response.status_code != requests.codes.ok:
            raise Exception('failed send bulk notif ' + response.text)

    def send(self, notification):
        self.bulk_send([notification])
