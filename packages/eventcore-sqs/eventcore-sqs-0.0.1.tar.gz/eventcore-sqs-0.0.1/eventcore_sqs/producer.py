import boto3
import json
import uuid

from eventcore import Producer


class SQSProducer(Producer):
    """
    Produce to a SQS queue.
    """

    def __init__(self, region_name, access_key_id, secret_access_key, url):
        sqs = boto3.resource('sqs',
                             region_name=region_name,
                             aws_access_key_id=access_key_id,
                             aws_secret_access_key=secret_access_key)
        self.queue = sqs.Queue(url)

    def produce(self, topic, event, subject, data):
        message_body = {
            'event': event,
            'subject': subject,
            'data': data
        }
        self.queue.send_message(MessageBody=json.dumps(message_body),
                                MessageGroupId=topic,
                                MessageDeduplicationId=str(uuid.uuid4()))
