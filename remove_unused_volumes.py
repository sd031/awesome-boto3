import boto3

def delete_unused_volumes(region_name):
    ec2 = boto3.resource('ec2', region_name=region_name)

    volumes = ec2.volumes.filter(
        Filters=[{'Name': 'status', 'Values': ['available']}]
    )

    for volume in volumes:
        v = ec2.Volume(volume.id)
        print(f"Deleting Volume {v.id}")
        v.delete()

def main():
    region_name = 'us-west-2'  # specify your region
    delete_unused_volumes(region_name)

if __name__ == "__main__":
    main()