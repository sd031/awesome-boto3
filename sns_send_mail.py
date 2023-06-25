import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Create a new SES resource and specify a region.
client = boto3.client('ses',region_name="us-west-2")

# Try to send the email.
try:
    #Provide the contents of the email.
    response = client.send_email(
        Destination={
            'ToAddresses': [
                'sandip.das.developer@gmail.com',
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': 'This is the body of the email.',
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': 'This is the subject line.',
            },
        },
        Source='contact@sandipdas.in',
    )
# Display an error if something goes wrong. 
except ClientError as e:
    print(e.response['Error']['Message'])
else:
    print("Email sent! Message ID:"),
    print(response['MessageId'])
