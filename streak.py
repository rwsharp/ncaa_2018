import pandas

season = 2015

games = pandas.read_csv('data/game_scores/games_{}.csv'.format(season))
teams = pandas.read_csv('data/game_scores/teams_{}.csv'.format(season))

games = games.drop('Unnamed: 0', axis=1)
teams = teams.drop('Unnamed: 0', axis=1)

games = games.merge(teams, left_on='team1', right_on='team') \
             .drop('team', axis=1) \
             .rename(index=str, columns={'name': 'team1_name'}) \
             .merge(teams, left_on='team2', right_on='team') \
             .drop('team', axis=1) \
             .rename(index=str, columns={'name': 'team2_name'})

games = games.sort_values('date')

for tm in teams['name']:
    team_record = games[(games['team1_name'] == tm) | (games['team2_name'] == tm)]

    all_rows = (team_record['date'] > 0)
    team_record.loc[all_rows, 'outcome'] = '-'

    outcome = (team_record['team1_name'] == tm) & (team_record['team1_score'] > team_record['team2_score'])
    team_record.loc[outcome, 'outcome'] = 'W'
    outcome = (team_record['team2_name'] == tm) & (team_record['team1_score'] < team_record['team2_score'])
    team_record.loc[outcome, 'outcome'] = 'W'
    outcome = (team_record['team1_name'] == tm) & (team_record['team1_score'] < team_record['team2_score'])
    team_record.loc[outcome, 'outcome'] = 'L'
    outcome = (team_record['team2_name'] == tm) & (team_record['team1_score'] > team_record['team2_score'])
    team_record.loc[outcome, 'outcome'] = 'L'

    outcome = (team_record['team1_name'] == tm) & (team_record['team1_score'] > team_record['team2_score'])
    team_record.loc[outcome, 'outcome2'] = 1
    outcome = (team_record['team2_name'] == tm) & (team_record['team1_score'] < team_record['team2_score'])
    team_record.loc[outcome, 'outcome2'] = 1
    outcome = (team_record['team1_name'] == tm) & (team_record['team1_score'] < team_record['team2_score'])
    team_record.loc[outcome, 'outcome2'] = 0
    outcome = (team_record['team2_name'] == tm) & (team_record['team1_score'] > team_record['team2_score'])
    team_record.loc[outcome, 'outcome2'] = 0


    team_record = team_record[team_record['date'] <= 20180220]

    # print the team's record as of the date above
    # print team_record.groupby('outcome').count()['game']

    n_games = 4
    team_record.loc[all_rows, 'streak'] = team_record['outcome2'].rolling(window=n_games).sum()
    team_record.loc[all_rows, 'on_streak'] = (team_record['streak'] >= n_games - 1)

    # print team_record[['date', 'team1_name', 'team1_score', 'team2_name', 'team2_score', 'outcome', 'streak', 'on_streak']]

    print tm, team_record['on_streak'][-1]

