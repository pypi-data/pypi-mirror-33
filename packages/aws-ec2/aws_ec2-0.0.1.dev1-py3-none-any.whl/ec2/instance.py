import boto3

ec2 = boto3.client("ec2")


def count_instances():
    res = ec2.describe_instances()
    i = 0
    for instance in res["Reservations"]:
        i += 1
    return i
