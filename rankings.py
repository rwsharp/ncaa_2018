import pandas
import os

output_path = os.path.realpath('data/prepared_data')
data_path = os.path.realpath('data/cb')

rankings = pandas.read_csv(os.path.join(data_path, 'cb2016.csv'),
                           header=None,
                           names=['season', 'team_id', 'team_name', 'ranker_id', 'ranker_name', 'date', 'rank'])

for col in ['team_name', 'ranker_id']:
    rankings[col] = rankings[col].str.strip()

print 'Rankings publish dates'
pub_dates = sorted(rankings['date'].unique())
train_dates = list()
for dt in pub_dates:
    print '    {}'.format(dt)
    if dt > 20160000:
        train_dates.append(dt)
print


output_file_names = list()
for train_date, label_date in zip(train_dates[:-1], train_dates[1:]):

    print 'train date: {}'.format(train_date)
    print 'label date: {}'.format(label_date)

    teams = pandas.DataFrame({'name': rankings['team_name'].unique()})

    for ranker in rankings['ranker_id'].unique():
        teams = teams.merge(rankings[(rankings['date'] == train_date) & (rankings['ranker_id'] == ranker)][['team_name', 'rank']],
                          left_on='name',
                          right_on='team_name',
                          how='left') \
                     .drop('team_name', axis=1) \
                     .rename(index=str, columns={'rank': ranker})

    teams = teams.dropna(axis=1, how='all')

    print 'Max number of missing ranks: {} out of {} rankers.'.format(teams.isnull().sum(axis=1).max(), len(rankings['ranker_id'].unique()))

    teams['median_rank'] = teams.median(axis=1)

    for ranker in rankings['ranker_id'].unique():
        if ranker in teams:
            teams[ranker] = teams[ranker].fillna(teams['median_rank'])


    label = pandas.DataFrame({'name': rankings['team_name'].unique()})

    for ranker in rankings['ranker_id'].unique():
        label = teams.merge(rankings[(rankings['date'] == label_date) & (rankings['ranker_id'] == ranker)][['team_name', 'rank']],
                          left_on='name',
                          right_on='team_name',
                          how='left') \
                     .drop('team_name', axis=1) \
                     .rename(index=str, columns={'rank': ranker})

    label = label.dropna(axis=1, how='all')

    label['median_rank'] = teams.median(axis=1)

    label = label[['name', 'median_rank']]

    teams = teams.drop('median_rank', axis=1)
    teams = teams.merge(label, on='name', how='left')
    teams = teams.rename(index=str, columns={'median_rank': 'label'})

    output_file_name = os.path.join(output_path, 'labeled_rankers_{}_{}.csv'.format(train_date, label_date))
    output_file_names.append(output_file_name)
    teams.to_csv(output_file_name)

print teams.sort_values('label')[:64]

combined = None
for file_name in output_file_names:
    data = pandas.read_csv(file_name)
    if combined is None:
        combined = data
    else:
        combined = combined.append(data)

print combined