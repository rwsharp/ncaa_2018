import pandas
import os

data_path = os.path.realpath('data/prepared_data')
data_file_name = 'combined_rankers.csv'
data_full_path = os.path.join(data_path, data_file_name)

ranker_list_file_name = 'all_valid_rankers.txt'

with open(os.path.join(data_path, ranker_list_file_name), 'r') as input_file:
    ranker_list = map(lambda s: s.strip(), input_file.readlines())

schema = {'name': str,
          'label': float,
          'date': int
          }

schema.update(dict([(rnk, float) for rnk in ranker_list]))

data = pandas.read_csv(data_full_path,
                       header=0,
                       dtype=schema) \
             .drop('Unnamed: 0', axis=1)

# check if there is any missing data
# print data.isnull().sum(axis=1).max()

print data[:5]