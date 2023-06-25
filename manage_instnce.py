import boto3
import os
import sys
from botocore.exceptions import ClientError

def get_latest_ubuntu_ami(region):
    ec2 = boto3.client('ec2', region_name=region)
    filters = [
        {'Name': 'name', 'Values': ['ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*']},
        {'Name': 'state', 'Values': ['available']},
        {'Name': 'architecture', 'Values': ['x86_64']},
    ]
    response = ec2.describe_images(Filters=filters, Owners=['099720109477'])
    images = response['Images']
    if not images:
        print("No Ubuntu 22 LTS AMI found.")
        sys.exit(1)
    latest_image = max(images, key=lambda x: x['CreationDate'])
    return latest_image['ImageId']

def create_key_pair(ec2, key_name):
    try:
        key_pair_info = ec2.create_key_pair(KeyName=key_name)
        print(f"Created key pair {key_name}")

        # Save the private key to ~/ec2_keys/
        os.makedirs(os.path.expanduser('~/ec2_keys'), exist_ok=True)
        with open(os.path.expanduser(f'~/ec2_keys/{key_name}.pem'), 'w') as f:
            f.write(key_pair_info['KeyMaterial'])
        print(f"Saved private key to ~/ec2_keys/{key_name}.pem")
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidKeyPair.Duplicate':
            print(f"Key pair {key_name} already exists.")
        else:
            raise

def manage_instance(action, key_name=None, instance_id=None, region='us-west-2'):
    ec2 = boto3.client('ec2', region_name=region)

    if action == 'create':
        if not key_name:
            print("The 'create' action requires a key name.")
            sys.exit(1)
        create_key_pair(ec2, key_name)
        image_id = get_latest_ubuntu_ami(region)
        response = ec2.run_instances(
            ImageId=image_id,
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            KeyName=key_name,
        )
        print(f"Created instance {response['Instances'][0]['InstanceId']}, waiting for getting ready")
        instance_id = response['Instances'][0]['InstanceId']
        instance=ec2.start_instances(InstanceIds=[instance_id])
        waiter = ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])
        print("Instance is now up and running")
    elif action in ['start', 'stop', 'reboot', 'terminate']:
        if not instance_id:
            print(f"The action '{action}' requires an instance ID.")
            sys.exit(1)
        if action == 'start':
            ec2.start_instances(InstanceIds=[instance_id])
            print(f"Started instance {instance_id}")
        elif action == 'stop':
            ec2.stop_instances(InstanceIds=[instance_id])
            print(f"Stopped instance {instance_id}")
        elif action == 'reboot':
            ec2.reboot_instances(InstanceIds=[instance_id])
            print(f"Rebooted instance {instance_id}")
        elif action == 'terminate':
            ec2.terminate_instances(InstanceIds=[instance_id])
            print(f"Terminated instance {instance_id}")
    elif action == 'list':
        session = boto3.Session(region_name='us-west-2')
        ec2_resource = session.resource('ec2')
        # Get information for all running instances
        running_instances = ec2_resource.instances.filter(Filters=[{
            'Name': 'instance-state-name',
            'Values': ['running']}])

        for instance in running_instances:
            print("ID: {}, State: {}, Type: {}".format(
                instance.id, instance.state['Name'], instance.instance_type))
    else:
        print(f"Unknown action: {action}")

def main():
    if len(sys.argv) < 2:
        print("Usage: manage_instance.py <action> [<key_name>] [<instance_id>] [<region>]")
        sys.exit(1)

    action = sys.argv[1]
    key_name = sys.argv[2] if len(sys.argv) > 2 else None
    instance_id = sys.argv[3] if len(sys.argv) > 3 else None
    region = sys.argv[4] if len(sys.argv) > 4 else 'us-west-2'
    manage_instance(action, key_name, instance_id, region)

if __name__ == "__main__":
    main()

# Useage
# python manage_instance.py <action> [<key_name>] [<instance_id>] [<region>]
