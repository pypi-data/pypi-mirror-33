import warnings
from os import path

import numpy as np
import pandas as pd
import h5py


class DataFrame(object):

    def __init__(self):
        self.cnt = 0
        self.data = []

    def __len__(self):
        return self.cnt

    def __getitem__(self, item):
        return self.data[item]

    def __iter__(self):
        self.iter_cnt = 0
        return self

    def __next__(self):
        if self.iter_cnt >= self.cnt:
            raise StopIteration
        else:
            ret = self.data[self.iter_cnt]
            self.iter_cnt += 1
            return ret

    def append(self, name, data, **kwargs):
        self.cnt += 1
        assert isinstance(data, np.ndarray)
        if 'maxshape' not in kwargs:
            max_shape = list(data.shape)
            max_shape[0] = None
            max_shape = tuple(max_shape)
            kwargs['maxshape'] = max_shape
        if data.dtype is np.dtype('O'):
            if isinstance(data[0], str):
                kwargs['dtype'] = h5py.special_dtype(vlen=str)
            if isinstance(data[0], np.ndarray):
                kwargs['dtype'] = h5py.special_dtype(vlen=data[0].dtype)

        self.data.append({'name': name, 'data': data, 'kwargs': kwargs})
        return self

    def extend(self, df):
        assert isinstance(df, DataFrame)
        self.data.extend(df.data)
        self.cnt += df.cnt


class DataSet(object):

    def __init__(self, file):
        self.file = file

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def remove(self, df):
        if isinstance(df, str):
            names = [df]
        elif isinstance(df, list):
            names = df
            for name in names:
                assert isinstance(name, str)
        else:
            assert isinstance(df, DataFrame)
            names = [item['name'] for item in df]

        with h5py.File(self.file, 'a') as f:
            for name in names:
                if name in f.keys():
                    del f[name]
                else:
                    warnings.warn('{} not in {}'.format(name, self.file),
                                  UserWarning)

    def create(self, df):
        assert isinstance(df, DataFrame)
        with h5py.File(self.file, 'a') as f:
            for item in df:
                name = item['name']
                data = item['data']
                kwargs = item['kwargs']

                if name in f.keys():
                    del f[name]

                dset = f.create_dataset(name=name, data=data, **kwargs)

    def append(self, df):
        assert isinstance(df, DataFrame)
        with h5py.File(self.file, 'a') as f:
            for item in df:

                name = item['name']
                data = item['data']
                kwargs = item['kwargs']

                if name not in f.keys():
                    self.create(DataFrame().append(name, data, **kwargs))
                else:
                    dset = f[name]
                    old_shape = dset.shape
                    data_shape = data.shape
                    assert data_shape[1:] == old_shape[1:]
                    dset.resize((old_shape[0] + data_shape[0],) + old_shape[1:])
                    dset[old_shape[0]:] = data

    def show(self):
        if path.exists(self.file):
            with h5py.File(self.file, 'r') as f:
                for key in f.keys():
                    print(key)
        else:
            print('file {} not exists'.format(self.file))

    def __getitem__(self, item):
        with h5py.File(self.file, 'r') as f:
            if item in f.keys():
                return f[item][:]
            else:
                warnings.warn('{} not in {}'.format(item, self.file),
                              UserWarning)

    @staticmethod
    def from_csv(file, csv):
        d = DataSet(file)
        pdf = pd.read_csv(csv)
        df = DataFrame()
        for name in pdf.columns.values.tolist():
            data = np.array(pdf[name])
            df.append(name, data)
        d.create(df)
        return d

    @staticmethod
    def create_dataset(file, df):
        d = DataSet(file)
        d.append(df)
        return d

