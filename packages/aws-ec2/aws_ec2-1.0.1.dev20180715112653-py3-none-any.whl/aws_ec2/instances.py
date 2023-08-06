import boto3


ec2 = boto3.resource('ec2')


def search(tags, states=['running']):
    filter_args = list()
    for tag_key, tag_value in tags.items():
        filter_args.append({
            'Name': 'tag:' + tag_key, 'Values': tag_value,
        })
    if states:
        filter_args.append({
            'Name': 'instance-state-name', 'Values': states
        })
    return ec2.instances.filter(Filters=filter_args)
