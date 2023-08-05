import datetime

import traceback
import boto3

#consider: avoid file scope?
sqs = boto3.client('sqs', )




def add_to_queue(queue_name, message_attributes: dict, message_body=''):
    response = None
    try:
        if not queue_exists(queue_name):
            print('%s queue does not exist. Making a new queue' % queue_name)
            response = sqs.create_queue(
                QueueName=queue_name,
                Attributes={
                    'MessageRetentionPeriod': '345600'  # 4 days
                }
            )
        else:
            response = sqs.get_queue_url(QueueName=queue_name)

        queue_url = response['QueueUrl']

        sqs_message_attributes = {}

        for k, v in message_attributes.items():
            sqs_message_attributes[k] = {
                'DataType': 'String',
                'StringValue': str(v),
            }

        response = sqs.send_message(
            QueueUrl=queue_url,
            DelaySeconds=10,
            MessageAttributes=sqs_message_attributes,
            MessageBody=message_body
        )
    except Exception as e:
        print('ClientError e:', e)
        print('traceback', traceback.format_exc())
        return {'error': str(e)}

    return response


def get_from_queue(queue_name, messages_num=10):
    try:
        response = sqs.get_queue_url(QueueName=queue_name)
        queue_url = response['QueueUrl']

        response = sqs.receive_message(
            QueueUrl=queue_url,
            AttributeNames=[
                'All'
            ],
            MaxNumberOfMessages=messages_num,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )

        return response

    except Exception as e:
        # print('ClientError e:', e)
        print('ClientError e:', e)
        print('traceback', traceback.format_exc())
        return None


def delete_from_queue(queue_name, receipt_handle):
    response = sqs.get_queue_url(QueueName=queue_name)
    sqs.delete_message(
        QueueUrl=response['QueueUrl'],
        ReceiptHandle=receipt_handle
    )


def queue_exists(queue_name):
    try:
        response = sqs.get_queue_url(QueueName=queue_name)

        return response['QueueUrl'] is not None
    except Exception as e:
        print('ClientError e:', e)
        print('traceback', traceback.format_exc())
        return False


if __name__ == '__main__':
    message_attributes = {
        'url': 'https://matrix.crebtools.com/Matrix/Public/Portal.aspx?k=1177309X3H53&p=DE-57004363-968#1'
    }
    message_body = 'URl for pre-scraping, added on: %s' % datetime.datetime.now().isoformat()
    add_to_queue('dev-UrlsForPreScraping', message_attributes, message_body)

    print('add_to_queue', add_to_queue('dev-UrlsForPreScraping', message_attributes, message_body))

    print('get_from_queue()', get_from_queue('dev-UrlsForPreScraping'))
