import boto3


class AwsBase(object):
    def __init__(self, aws_ctx, org):
        self.ctx = aws_ctx
        self.org = org

    @classmethod
    def client(cls, name, aws_ctx):
        return boto3.client(name, region_name=aws_ctx.region)

    @classmethod
    def resource(cls, name, aws_ctx):
        return boto3.resource(name, region_name=aws_ctx.region)

    @classmethod
    def dict_to_tuple_array(cls, data, key='Key', value='Value'):
        return [{key: k, value: v} for k, v in data.items()]

    @classmethod
    def tuple_array_do_dict(cls, data, key='Key', value='Value'):
        return {x[key]: x[value] for x in data}
