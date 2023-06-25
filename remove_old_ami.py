import boto3
from datetime import datetime, timedelta

def get_all_regions():
    client = boto3.client('ec2')
    regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
    return regions

def get_unused_amis(region, days_to_keep):
    ec2 = boto3.resource('ec2', region_name=region)
    instances = ec2.instances.all()

    used_amis = set(instance.image_id for instance in instances)
    all_amis = [image for image in ec2.images.filter(Owners=['self'])]

    unused_amis = [ami for ami in all_amis if ami.id not in used_amis]
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    old_amis = [ami for ami in unused_amis if datetime.strptime(ami.creation_date, '%Y-%m-%dT%H:%M:%S.%fZ') < cutoff_date]

    return old_amis

def deregister_amis(amis, region):
    ec2 = boto3.client('ec2', region_name=region)
    for ami in amis:
        ec2.deregister_image(ImageId=ami.id)
        print(f"Deregistered {ami.id} in {region}")

def main():
    days_to_keep = 0  # number of days to keep AMIs
    regions = get_all_regions()
    for region in regions:
        old_amis = get_unused_amis(region, days_to_keep)
        deregister_amis(old_amis, region)

if __name__ == "__main__":
    main()
