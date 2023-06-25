import boto3
from datetime import datetime, timedelta, timezone

def remove_old_snapshots():
    ec2 = boto3.client('ec2')

    # Get a list of all snapshots
    response = ec2.describe_snapshots(OwnerIds=['self'])
    snapshots = response['Snapshots']

    # Calculate the date 30 days ago in UTC timezone
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

    # Find snapshots older than 30 days
    # old_snapshots = [snapshot for snapshot in snapshots if snapshot['StartTime'] < thirty_days_ago]
    old_snapshots = [snapshot for snapshot in snapshots]
    # Delete old snapshots
    for snapshot in old_snapshots:
        snapshot_id = snapshot['SnapshotId']
        print(f"Deleting snapshot {snapshot_id}...")
        ec2.delete_snapshot(SnapshotId=snapshot_id)
        print(f"Snapshot {snapshot_id} deleted.")

if __name__ == '__main__':
    remove_old_snapshots()