# coding: utf-8

"""nptable
nptable is a very inefficient container to work with numpy arrays.
It allows to build tables, similar to dictionaries, that have numpy array as values.
Columns can be accessed by using dot notation or standard dictionary notation. Elements can be added with the 
append function as it is common for lists. Single or multiple rows can be extracted.
All the table can be easily sorted using of the column. Data can be filtered my masking.
"""

__author__ = "Andrea Amico (amico.andrea.90@gmail.com)"
__version__ = "1.0.0"
__copyright__ = "Copyright (c) 2018 Andrea Amico"
__license__ = "MIT"

__all__ = ['nptable']



import collections
import csv
import numbers
import numpy as np
import re

class Table(object):

    def __init__(self, *column_names):
        '''Table can be created by the columns name:
        >>> Table('a', 'b')
        <nptable.Table at 0x10b88ae48>

        or by the load staticmethod:
        >>> Table.load(filename=scv_filename, delimiter=',')

        where csv_filename is the path to a csv file.

        Finally by the from_string staticmethod:
        >>> my_data = """
        >>> a b
        >>> 1 2
        >>> 2 4
        >>> 3 9"""
        >>> npt = Table.from_string(my_data)
        >>> print(npt)
        a                   b                   
        ----------------------------------------
        1.0                 2.0                 
        2.0                 4.0                 
        3.0                 9.0                 

        '''

        assert all(isinstance(column_name, str) for column_name in column_names)
        self._column_names = list(column_names)
        self._data = [np.array([]) for _ in column_names]
        
    
    @property
    def as_dict(self):
        '''property: returns dictionary representation on the Table
        '''
        return {key:value for key, value in zip(self._column_names, self._data)}
    
    @property
    def columns(self):
        '''property: returns a list of the columns name of the Table
        '''
        return self._column_names 
    
    @property
    def rows(self):
        '''property: returns a numpy array containing the Table rows data
        ''' 
        return np.array(list(zip(*self.data)))

    @property
    def data(self):
        '''property: returns the data contained in the table, i.e. the list of the columns as numpy arrays
        '''
        return self._data
    
    @property
    def num_columns(self):
        '''property: returns the number of columns in Table
        '''
        return len(self.columns)

    
    def __getattr__(self, key):
        return self.as_dict[key]
    
    def __getitem__(self, key):
        return self.__getattr__(key)
    
    def __setitem__(self, key, value):
        assert len(value)==len(self), "Invalid number of elements"
        if key in self.columns:
            self._data[self.columns.index(key)] = value
        else:
            self._column_names.append(key)
            self._data.append(np.array(value))
            
    def __setattr__(self, key, value):
        if key in ['_column_names', '_data']:
            super().__setattr__(key, value)
        else:
            self.__setitem__(key, value)
    
    def __delitem__(self, key):
        del_index = self.columns.index(key)
        del self._column_names[del_index]
        del self._data[del_index]
        
    def __delattr__(self, key):
        if key in ['_column_names', '_data']:
            pass
        else:
            self.__delitem__(key)
    
    def row(self, row_index):
        '''returns the row_index-th Table row
        '''

        return np.array([d[row_index] for d in self.data])

    def select(self, mask):
        '''returns a new Table that is a copy of the original table but only containing the rows corresponding to True 
        values of the mask.
        >>> npt = Table('a', 'b').aapend(np.)

        '''
        assert len(mask)==len(self.rows), 'The mask length must be the number of rows in the table'
        new_table = Table(*self.columns)
        for index, condition in enumerate(mask):
            if condition:
                new_table.append(*self.row(index))
        return new_table

    def append(self, *new_data):
        assert len(new_data)==len(self.columns), 'Number of new item != number of columns'
        if any(isinstance(x, collections.Iterable) for x in new_data):
            assert all(len(new_data[0])==len(x) for x in new_data), 'Appended item must have the same length'
        for index, new_entry in enumerate(new_data):
            new_entry = np.array(new_entry)
            self._data[index] = np.append(self._data[index], new_entry)
        return self
            
    def delete(self, obj=-1):
        for index in range(self.num_columns):
            self._data[index] = np.delete(self._data[index], obj)
        return self
            
    def sort(self, column_name=None, key=None):
        if not column_name:
            column_name = self.columns[0]
            
        assert column_name in self._column_names, 'Column name not in table'
        index = self._column_names.index(column_name)
        if not key:
            key = lambda x: x[index]
        self._data = list(zip(*sorted(zip(*self._data), key=key)))
        return self
        
    def save(self, filename):
        with open(filename, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(self.columns)
            for row in zip(*self._data):
                writer.writerow(row)
        return self
        
    
    @staticmethod
    def from_string(string):
        string = re.sub(r'\t',' ', string)
        string = re.sub(' +',' ', string)    
        lines = [line for line in string.splitlines() if line]
        new_table = Table(*lines[0].split(' '))
        for line in lines[1:]: 
            new_table.append(*[float(x) for x in line.split(' ')])    
        return new_table

                
    @staticmethod
    def load(filename, delimiter=',', **kwargs):
        with open(filename, mode='r') as csv_file:
            try:
                has_header = csv.Sniffer().has_header(sample=csv_file.read(1024))
            except csv.Error as e:
                has_header = True

            csv_file.seek(0)
            reader = csv.reader(csv_file, delimiter=delimiter, **kwargs)
            
            first_line = reader.__next__()
            if has_header:
                new_table = Table(*first_line)
            else:
                new_table = Table(*[chr(index + 97) for index, _ in enumerate(first_line)])
                new_table.append(*[float(r) for r in first_line])
            for row in reader:
                new_table.append(*[float(r) for r in row])
        return new_table
    
    def __len__(self):
        return len(self.data[0])
    
    def __str__(self):
        row_format ="{:<20}" * (self.num_columns)
        _str = row_format.format(*self.columns) + '\n' + '-'*self.num_columns*20
        for row in zip(*self._data):
            _str = _str + '\n' + row_format.format(*row)
        return _str
    

if __name__ == '__main__':
    t = Table('a', 'b').append(1,2).append([3,4],[5,6]).delete(1)
    print(t, '\n')

    t.append(np.linspace(1,2.5,5), np.linspace(2.5,1,5))
    print(t, '\n')

    t.save('test.csv')

    print(t.row(1), '\n')

    new_t = t.select(t.a>2)
    print(new_t.sort('a'), '\n')

    print(Table.load('test.csv'))




