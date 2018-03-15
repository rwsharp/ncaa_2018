"""
Prepare historical ranking data for training. Create table where, for the ranker publication date in question...
    - each row represents a different team
    - each feature column represents the rank by a different ranker
    - the label column represents the rank by median score of the ranker from THE NEXT WEEK

For rankers that only rank the top N teams (e.g., AP top 25) all lower ranks and filled in by using themedian rank
across the remaining rankers. This can lead to ties, but that's ok.


Only rankers present in all_valid_rankers.txt are used.
This file is produced by ranker_coverage.py and only includes rankers that are consistently published over a number of years
"""

import pandas
import os
import re

output_path = os.path.realpath('data/prepared_data')
data_path = os.path.realpath('data/cb')

ranker_list_file_name = 'all_valid_rankers.txt'
combined_output_file_name = 'combined_rankers.csv'


with open(os.path.join(output_path, ranker_list_file_name), 'r') as input_file:
    ranker_list = map(lambda s: s.strip(), input_file.readlines())

schema = {0: ('season', str),
          1: ('team_id', int),
          2: ('team_name', str),
          3: ('ranker_id', str),
          4: ('ranker_name', str),
          5: ('date', int),
          6: ('rank', int)
          }

col_names = [col[0] for key, col in sorted(schema.iteritems())]
col_types = dict([col for key, col in sorted(schema.iteritems())])
str_cols  = [col[0] for key, col in sorted(schema.iteritems()) if col[1] in (str, )]

# Read the hisgtorical ranking data
output_file_names = list()

threshold = 5
for year in range(2010, 2017+1):

    rankings = pandas.read_csv(os.path.join(data_path, 'cb{}.csv'.format(year)),
                               header=None,
                               names=col_names,
                               dtype=col_types)

    # Strip whitespace from columns
    for col in str_cols:
        rankings[col] = rankings[col].str.strip()

    pub_dates = sorted(rankings['date'].unique())
    train_dates = list()
    for dt in pub_dates[-1 - threshold:-1]:
        train_dates.append(dt)

    for train_date, label_date in zip(train_dates[:-1], train_dates[1:]):

        print 'train date: {}'.format(train_date)
        print 'label date: {}'.format(label_date)

        teams = pandas.DataFrame({'name': rankings['team_name'].unique()})

        for ranker in ranker_list:
            teams = teams.merge(rankings[(rankings['date'] == train_date) & (rankings['ranker_id'] == ranker)][['team_name', 'rank']],
                              left_on='name',
                              right_on='team_name',
                              how='left') \
                         .drop('team_name', axis=1) \
                         .rename(index=str, columns={'rank': ranker})

        teams = teams.dropna(axis=1, how='all')

        print 'Max number of missing ranks: {} out of {} rankers.'.format(teams.isnull().sum(axis=1).max(), len(ranker_list))

        teams['median_rank'] = teams.median(axis=1)

        for ranker in rankings['ranker_id'].unique():
            if ranker in teams:
                teams[ranker] = teams[ranker].fillna(teams['median_rank'])

        # So why are some rankers, like COL, that cleared the ranker_coverage test and apparently rank all teams getting
        # hit with the interpolation technique (evidenced by their type changing to float)?
        #
        # Answer: They didn't actually rank all the teams. For example, COL is missing #259 N Kentucky in the snapshot
        # from 2013-03-10: https://www.masseyratings.com/cb/arch/compare2013-18.htm
        #
        # Yay - the method seems to be doing exactly what it should be.
        #
        # print teams[(teams['name'] == 'North Carolina')][['name', 'AP', 'BOB', 'CMP', 'COL', 'DC', 'median_rank']]

        label = pandas.DataFrame({'name': rankings['team_name'].unique()})

        for ranker in rankings['ranker_id'].unique():
            label = label.merge(rankings[(rankings['date'] == label_date) & (rankings['ranker_id'] == ranker)][['team_name', 'rank']],
                              left_on='name',
                              right_on='team_name',
                              how='left') \
                         .drop('team_name', axis=1) \
                         .rename(index=str, columns={'rank': ranker})

        label = label.dropna(axis=1, how='all')

        label['median_rank'] = label.median(axis=1)

        label = label[['name', 'median_rank']]

        teams = teams.drop('median_rank', axis=1)
        teams = teams.merge(label, on='name', how='left')
        teams = teams.rename(index=str, columns={'median_rank': 'label'})

        output_file_name = os.path.join(output_path, 'labeled_rankers_{}_{}.csv'.format(train_date, label_date))
        output_file_names.append(output_file_name)
        teams.to_csv(output_file_name)

    # print teams.sort_values('label')[:64]

combined = None
for file_name in sorted(output_file_names):
    print os.path.split(file_name)[1]
    dt = int(re.search('_(\d+)_', file_name).groups()[0])

    data = pandas.read_csv(file_name).drop('Unnamed: 0', axis=1)
    data['date'] = dt

    if combined is None:
        combined = data
    else:
        combined = combined.append(data)

combined_output_full_path = os.path.join(output_path, combined_output_file_name)

print 'Combined data shape: {}'.format(combined.shape)
print 'Writing combined data to {}'.format(combined_output_full_path)
combined.to_csv(combined_output_full_path)
