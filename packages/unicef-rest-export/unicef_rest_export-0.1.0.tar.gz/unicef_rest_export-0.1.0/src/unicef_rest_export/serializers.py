from rest_framework import serializers
from tablib import Dataset


class ExportSerializer(serializers.ListSerializer):
    """Transforms data into a dataset"""
    read_only = True

    def get_dataset(self, data):
        headers = list(data[0].keys())
        data_list = []
        for d in data:
            data_list.append([v for _, v in d.items()])
        dataset = Dataset(*data_list, headers=headers)
        return dataset

    @property
    def data(self):
        data = super(serializers.ListSerializer, self).data
        if isinstance(data, Dataset) or data:
            return self.get_dataset(data)
        else:
            return Dataset([])
