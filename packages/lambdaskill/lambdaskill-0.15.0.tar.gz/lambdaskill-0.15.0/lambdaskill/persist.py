from contextlib import contextmanager

import boto3


class PersistenceException(Exception):
    pass


class AttributeStore(object):

    def __init__(self, table_name, region_name=None, endpoint_url=None,
                 create_table=False, read_capacity_units=5, write_capacity_units=5):
        self.__dbservice = boto3.resource('dynamodb', region_name=region_name, endpoint_url=endpoint_url)
        self.__attrs = {}
        try:
            self.__table = self.__dbservice.Table(table_name)
        except self.__dbservice.exceptions.ResourceNotFoundException as e:
            if not create_table:
                raise PersistenceException('Persistence table not found.')
            self.__table = self.__dbservice.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'userId',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'deviceId',
                        'KeyType': 'RANGE'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'userId',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'deviceId',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'WriteCapacityUnits': write_capacity_units,
                    'ReadCapacityUnits': read_capacity_units
                }
            )

    def __len__(self):
        return len(self.__attrs)

    def __getitem__(self, item):
        return self.__attrs[item]

    def __setitem__(self, key, value):
        self.__attrs[key] = value

    def __delitem__(self, key):
        del self.__attrs[key]

    def get(self, key, default=None):
        return self.__attrs.get(key, default)

    def load(self, request):
        context = request.j['context']['System']
        userid = context['user']['userId']
        deviceid = context['device']['deviceId']
        try:
            entry = self.__table.get_item(Key={'userId': userid, 'deviceId': deviceid})['Item']
        except KeyError:
            _ = self.__table.put_item(Item={'userId': userid, 'deviceId': deviceid, 'Attributes': {}})
            entry = self.__table.get_item(Key={'userId': userid, 'deviceId': deviceid})['Item']
        self.__attrs.update(entry['Attributes'])

    def save(self, request):
        context = request.j['context']['System']
        userid = context['user']['userId']
        deviceid = context['device']['deviceId']
        _ = self.__table.update_item(Key={'userId': userid, 'deviceId': deviceid},
                                     UpdateExpression='set Attributes = :a',
                                     ExpressionAttributeValues={':a': self.__attrs})

    @contextmanager
    def session(self, request):
        self.load(request=request)
        yield
        self.save(request=request)
