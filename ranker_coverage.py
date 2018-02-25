"""
Comb through the historical rankings files. Determine which rankers produced scores in a given set of weeks leading up
to the NCAA Tourney. Combine results across the years to find the rankers that were consistently present over time.
"""

import numpy
import pandas
import os
import subprocess

base_path = os.path.realpath('./')
output_path = os.path.realpath('data/prepared_data')
data_path = os.path.realpath('data/cb')

output_files = list()

for year in range(2000, 2100):
    input_file_name = 'cb{}.csv'.format(year)
    output_file_name = 'valid_rankers_{}.txt'.format(year)

    input_file_full_path = os.path.join(data_path, input_file_name)
    output_file_full_path = os.path.join(output_path, output_file_name)

    if os.path.isfile(input_file_full_path):

        rankings = pandas.read_csv(input_file_full_path,
                                   header=None,
                                   names=['season', 'team_id', 'team_name', 'ranker_id', 'ranker_name', 'date', 'rank'])

        for ranker in sorted(rankings['ranker_id'].unique()):
            print ranker

        for col in ['team_name', 'ranker_id']:
            rankings[col] = rankings[col].str.strip()

        print 'Rankings publish dates'
        pub_dates = sorted(rankings['date'].unique())
        train_dates = list()
        for dt in pub_dates:
            print '    {}'.format(dt)
            # the second half of the season, excluding the final post-tourney date (because many rankers do not publish an update)
            if int('{}0000'.format(year)) < dt < int('{}0401'.format(year)):
                train_dates.append(dt)
        print

        threshold = 3

        all_rankers = None
        for i, dt in enumerate(train_dates[-threshold:]):

            rankers_present_on_date = sorted(rankings[(rankings['date'] == dt)]['ranker_id'].unique())
            rankers = pandas.DataFrame({'ranker': rankers_present_on_date})
            rankers['dt_{}'.format(dt)] = 1

            if all_rankers is None:
                all_rankers = rankers
            else:
                all_rankers = all_rankers.merge(rankers, on='ranker', how='outer')

        all_rankers['n_dates_present'] = all_rankers.drop('ranker', axis=1).sum(axis=1)

        rankers_to_use = list()

        for i in range(all_rankers.shape[0]):
            ranker = all_rankers.sort_values('n_dates_present').iloc[i]['ranker']
            ndp = all_rankers.sort_values('n_dates_present').iloc[i]['n_dates_present']

            ser = all_rankers.sort_values('n_dates_present').drop(['ranker', 'n_dates_present'], axis=1).iloc[i]

            dates = all_rankers.drop(['ranker', 'n_dates_present'], axis=1).columns

            s_last = None
            s_max = 0
            for s, dt in reversed(zip(ser, dates)):
                if s_last is None:
                    s_next = s
                else:
                    s_next = s + s_last

                if not numpy.isnan(s_next):
                    s_max = s_next

                s_last = s_next

                #if ranker in ('LMC'):
                #    print dt, ranker, s, s_next, s_max

            print '{:3} {:3.0f} {:3.0f}'.format(ranker, ndp, s_max)

            if s_max >= threshold:
                rankers_to_use.append(ranker)

        with open(output_file_full_path, 'w') as output_file:
            for ranker in sorted(rankers_to_use):
                print >> output_file, ranker
        output_files.append(output_file_full_path)

script = os.path.join(base_path, 'combine_valid_rankers.sh')
subprocess.call([script])