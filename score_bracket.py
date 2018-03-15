import sys
import os
import glob

import numpy as np
import pandas as pd
import sklearn as skl
import re
from collections import Counter

def safe_int(x):
    return int(x) if x.strip() != '' else None


def play_round(round, games, results, teams):
    for game, info in games.iteritems():
        game_in_round = False

        if round == 'play in':
            if game[0] in ['W', 'X', 'Y', 'Z']:
                game_in_round = True
        elif game[0:2] == round:
            game_in_round = True
        elif game[0] in ['W', 'X', 'Y', 'Z']:
            continue
        elif game[0:2] in ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']:
            continue
        else:
            raise ValueError('Unrecognized round: {} {}'.format(round, game))

        try:
            if game_in_round:
                game_pair = tuple(sorted([info['team_0'], info['team_1']]))
                info['winner'] = results[game_pair]
                # print game, '{} vs. {} winner: {}'.format(teams[info['team_0']], teams[info['team_1']], teams[info['winner']])
        except:
            print round
            raise


def play_ranked_round(round, games, bracket, teams):
    for game, info in games.iteritems():
        game_in_round = False

        if round == 'play in':
            if game[0] in ['W', 'X', 'Y', 'Z']:
                game_in_round = True
        elif game[0:2] == round:
            game_in_round = True
        elif game[0] in ['W', 'X', 'Y', 'Z']:
            continue
        elif game[0:2] in ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']:
            continue
        else:
            raise ValueError('Unrecognized round: {} {}'.format(round, game))

        try:
            if game_in_round:
                game_pair = tuple(sorted([info['team_0'], info['team_1']]))
                if bracket[game_pair[0]] < bracket[game_pair[1]]:
                    info['winner'] = game_pair[0]
                else:
                    info['winner'] = game_pair[1]

                # if teams[info['winner']] == 'Northwestern':
                print game, '{} vs. {} winner: {}'.format(teams[info['team_0']], teams[info['team_1']], teams[info['winner']])
        except:
            print round
            raise


def play_predicted_ranked_round(round, games, bracket, teams, game_results):
    points = {'R1': 1,
              'R2': 2,
              'R3': 4,
              'R4': 8,
              'R5': 16,
              'R6': 32}

    points_in_round = 0

    for game, info in games.iteritems():
        game_in_round = False

        if game[0:2] == round:
            game_in_round = True
        elif game[0] in ['W', 'X', 'Y', 'Z']:
            continue
        elif game[0:2] in ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']:
            continue
        else:
            raise ValueError('Unrecognized round: {} {}'.format(round, game))

        try:
            if game_in_round:
                game_pair = tuple(sorted([info['team_0'], info['team_1']]))
                if bracket[game_pair[0]] < bracket[game_pair[1]]:
                    info['winner'] = game_pair[0]
                else:
                    info['winner'] = game_pair[1]

                # if teams[info['winner']] == 'Northwestern':
                if game in game_results:
                    if game_results[game] == info['winner']:
                        points_in_round += points[round]
                        print 'Yay!: {} {} {}'.format(round, points[round], teams[info['winner']])
                    else:
                        print 'Boo!: {} {} {}'.format(round, 0, teams[info['winner']])

                    #print round, game, teams[game_results[game]]
                    # print game, '{} vs. {} winner: {}'.format(teams[info['team_0']], teams[info['team_1']], teams[info['winner']])
                    #print

                # print '|'.join(map(str, [game, info['team_0'], teams[info['team_0']], '', info['team_1'], teams[info['team_1']], '']))
        except:
            print round
            raise

    return points_in_round


def update_bracket(round, games, teams):
    delimiter = '|'
    for game, info in games.iteritems():
        game_in_round = False

        if game[0:2] == round:
            game_in_round = True
        elif game[0] in ['W', 'X', 'Y', 'Z']:
            continue
        elif game[0:2] in ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']:
            continue
        else:
            raise ValueError('Unrecognized round: {} {}'.format(round, game))

        if game_in_round:
            if info['team_0'] is None:
                info['team_0'] = games[info['parent_0']]['winner']

            if info['team_1'] is None:
                info['team_1'] = games[info['parent_1']]['winner']

            # print delimiter.join(map(str, [game, info['team_0'], teams[info['team_0']], '', info['team_1'], teams[info['team_1']], '']))


def initialize_bracket(games, seeds, teams):
    # Initialize bracket

    # set up the play-in games
    for game, info in games.iteritems():
        if game[0] != 'R':
            info['team_0'] = seeds.get(info['parent_0'])
            info['team_1'] = seeds.get(info['parent_1'])
            # print game, '{} vs. {}'.format(teams[info['team_0']], teams[info['team_1']])

    # set up round 1 except for play-in slots
    for game, info in games.iteritems():
        if game[0:2] == 'R1':
            info['team_0'] = seeds.get(info['parent_0'])
            info['team_1'] = seeds.get(info['parent_1'])
            # print game, info


def read_rankings(data_root, season):
    rankings = dict()
    special = ['Rank', 'Team', 'Conf', 'Record', 'Mean', 'Median', 'St.Dev']
    string_cols = ['Team', 'Conf', 'Record']
    float_cols = ['Mean', 'Median', 'St.Dev']
    shift_found = False

    with open(os.path.join(data_root, str(season) + '_composite_rankings.csv'), 'r') as input_data:
        for line_number, line in enumerate(input_data):
            team_properties = dict()
            team_rankings = dict()
            if line_number == 0:
                header_str = line.rstrip('\n')
                header = map(lambda s: s.strip().strip(','), line.split())

                N = len(header_str)
                breaks = [N]
                for loc in range(N - 1, -1, -1):
                    # print loc, header_str[loc], header_str[loc] == ' '
                    is_space = (header_str[loc] == ' ')
                    if is_space:
                        if loc > 0:
                            next_is_space = (header_str[loc - 1] == ' ')
                        else:
                            next_is_space = False

                        if not next_is_space:
                            breaks.append(loc)

                breaks.reverse()
                # print breaks

                # print header_str

            if line.strip() != '' and line.rstrip('\n') != header_str:
                if line_number > -1:
                    # print line.rstrip()
                    data = line.rstrip('\n')
                    team_found = False
                    for loc in range(len(breaks) - 1):
                        left = breaks[loc]
                        right = breaks[loc + 1]

                        if not shift_found:
                            if header[loc] == 'Rank':
                                right = right - len('Rank,')
                                left = right - 4
                                breaks[loc] = left
                                team_properties[header[loc]] = safe_int(data[left:min(right, len(data))])
                                # print 'a', header[loc], int(data[left:min(right, len(data))])
                            elif header[loc] == 'Team':
                                # print '>>>', left, right, data[left:min(right, len(data))]
                                left = left - len('Rank,')
                                right = left + 17
                                breaks[loc] = left
                                team_properties[header[loc]] = data[left:min(right, len(data))].strip()
                                # print 'b', header[loc], data[left:min(right, len(data))].strip()
                            elif header[loc] == 'Conf':
                                # print '>>>', left, right, data[left:min(right, len(data))]
                                left = left - len('Rank, Team,') + 17
                                right = left + 6
                                breaks[loc] = left
                                team_properties[header[loc]] = data[left:min(right, len(data))].strip()
                                # print 'c', header[loc], data[left:min(right, len(data))].strip()
                            elif header[loc] == 'Record':
                                # print '>>>', left, right, data[left:min(right, len(data))]
                                left = left - len('Rank, Team, Conf,') + 17 + 6
                                right = left + 6
                                breaks[loc] = left
                                breaks[loc + 1] = right
                                shift_found = True
                                team_found = True
                                team_properties[header[loc]] = data[left:min(right, len(data))].strip()
                                # print 'd', header[loc], data[left:min(right, len(data))].strip()
                            else:
                                team_rankings[header[loc]] = safe_int(data[left:min(right, len(data))])
                                # print '*', header[loc], int(data[left:min(right, len(data))])
                        else:
                            if header[loc] == 'Record':
                                team_found = True

                            if not (team_found and header[loc] in ['Team', 'Rank']):
                                if header[loc] in string_cols:
                                    team_properties[header[loc]] = data[left:min(right, len(data))].strip()
                                    # print '-', header[loc], data[left:min(right, len(data))].strip()
                                elif header[loc] in float_cols:
                                    team_properties[header[loc]] = float(data[left:min(right, len(data))])
                                    # print '-', header[loc], float(data[left:min(right, len(data))])
                                elif header[loc] != 'Rank':
                                    team_rankings[header[loc]] = safe_int(data[left:min(right, len(data))])
                                    # print '-', header[loc], safe_int(data[left:min(right, len(data))])
                            else:
                                continue

                    team = team_properties['Team']

                    rankings[team] = {'properties': team_properties,
                                      'rankings': team_rankings}

                    # print team, '        \t', rankings[team]

    return rankings


def read_teams(history_dir):
    teams = dict()
    with open(os.path.join(history_dir, 'Teams.csv'), 'r') as input_data:
        for line_number, line in enumerate(input_data):
            if line_number > 0:
                data = map(lambda s: s.strip(), line.split(','))
                id = int(data[0])
                team = data[1]

                teams[id] = team

    return teams


def read_games(history_dir, season):
    games = dict()
    with open(os.path.join(history_dir, 'NCAATourneySlots.csv'), 'r') as input_data:
        for line_number, line in enumerate(input_data):
            if line_number > 0:
                data = map(lambda s: s.strip(), line.split(','))
                year = int(data[0])
                game = data[1]
                parent_0 = data[2]
                parent_1 = data[3]

                if year == season:
                    games[game] = {'parent_0': parent_0,
                                   'parent_1': parent_1,
                                   'team_0': None,
                                   'team_1': None,
                                   'winner': None,
                                   'selected_0': None,
                                   'selected_1': None}

    return games


def read_seeds(history_dir, season):
    seeds = dict()
    with open(os.path.join(history_dir, 'NCAATourneySeeds.csv'), 'r') as input_data:
        for line_number, line in enumerate(input_data):
            if line_number > 0:
                data = map(lambda s: s.strip(), line.split(','))
                year = int(data[0])
                seed = data[1]
                team_id = int(data[2])

                if year == season:
                    seeds[seed] = team_id

    return seeds


def read_results(results_file, season):
    results = dict()
    with open(results_file, 'r') as input_data:
        for line_number, line in enumerate(input_data):
            if line_number > 0:
                data = map(lambda s: s.strip(), line.split(','))
                year = int(data[0])
                winner = int(data[2])
                loser = int(data[4])

                if year == season:
                    game_pair = tuple(sorted([winner, loser]))
                    results[game_pair] = winner

    return results


def get_rankers(rankings):
    rankers = dict()
    for team, info in rankings.iteritems():
        for ranker, rank in info['rankings'].iteritems():
            rankers.setdefault(ranker, {'top': None, 'bottom': None, 'exclude': None})
            if rank is not None:
                if rankers[ranker]['top'] is None:
                    rankers[ranker]['top'] = rank
                else:
                    rankers[ranker]['top'] = rank if rank < rankers[ranker]['top'] else rankers[ranker]['top']

                if rankers[ranker]['bottom'] is None:
                    rankers[ranker]['bottom'] = rank
                else:
                    rankers[ranker]['bottom'] = rank if rank > rankers[ranker]['bottom'] else rankers[ranker]['bottom']

                if rankers[ranker]['bottom'] is not None:
                    if rankers[ranker]['bottom'] < 100:
                        rankers[ranker]['exclude'] = True
                    else:
                        rankers[ranker]['exclude'] = False

    included_rankers = list()
    for ranker, info in rankers.iteritems():
        if not info['exclude']:
            included_rankers.append(ranker)

    return included_rankers


def get_mmad_teams(games):
    mmad_teams = list()
    for game, info in games.iteritems():
        if game[0:2] == 'R1':
            mmad_teams.append(info['team_0'])
            mmad_teams.append(info['team_1'])

    return mmad_teams


def get_bracket(ranker, rankings, mmad_teams, teams):
    bracket = dict()
    for team in mmad_teams:
        bracket[team] = rankings[teams[team]]['rankings'][ranker]

    return bracket


def get_voter_bracket(ranker_set, n, rankings, mmad_teams, teams):
    bracket = dict()
    votes = list()

    # Each team is ranked n times by n randomly selected rankers from the ranker_set.
    # final ranking is normalized by n to make brackets comparable if the ranker_set changes size.
    for team in mmad_teams:
        for vote in range(n):
            ranker = np.random.choice(ranker_set)
            votes.append(ranker)
            bracket[team] = rankings[teams[team]]['rankings'][ranker]
        bracket[team] = bracket[team]/float(n)

    return bracket


def get_randomized_bracket(ranker, noise_magnitude, rankings, mmad_teams, teams):
    bracket = dict()

    # Each team is ranked n times by n randomly selected rankers from the ranker_set.
    # final ranking is normalized by n to make brackets comparable if the ranker_set changes size.
    for team in mmad_teams:
        bracket[team] = rankings[teams[team]]['rankings'][ranker] + np.random.normal(loc=0, scale=noise_magnitude)

    return bracket


def get_mascot_randomized_bracket(ranker, mascot_noise, rankings, mmad_teams, teams):
    bracket = dict()

    # Each team is ranked n times by n randomly selected rankers from the ranker_set.
    # final ranking is normalized by n to make brackets comparable if the ranker_set changes size.
    for team in mmad_teams:
        noise = mascot_noise[team]
        bracket[team] = rankings[teams[team]]['rankings'][ranker] + noise

    return bracket


def set_selections(games, ranking):
    # set selections given R1 teams
    for game, info in games.iteritems():
        if game[0:2] == 'R1':
            info['selected_0'] = info['team_0']
            info['selected_1'] = info['team_1']

    # choose winners by rank in subsequent rounds
    for round in ['R2', 'R3', 'R4', 'R5', 'R6']:
        for game, info in games.iteritems():
            if game[0:2] == round:
                p0 = games[info['parent_0']]
                p1 = games[info['parent_1']]

                info['selected_0'] = p0['selected_0'] if ranking[p0['selected_0']] < ranking[p0['selected_1']] else p0['selected_1']
                info['selected_1'] = p1['selected_0'] if ranking[p1['selected_0']] < ranking[p1['selected_1']] else p1['selected_1']


def score_bracket(games, ranking):

    points = {'R1': 1,
              'R2': 2,
              'R3': 4,
              'R4': 8,
              'R5': 16,
              'R6': 32}

    score = 0
    possible = 0

    for game, info in games.iteritems():
        if game[0] != 'R':
            round = 'play in'
            continue
        else:
            round = game[0:2]
            selected_winner = info['selected_0'] if ranking[info['selected_0']] < ranking[info['selected_1']] else info['selected_1']
            if info['winner'] == selected_winner:
                p = points[round]
            else:
                p = 0

            score += p
            possible += points[round]

    return score, possible


def compute_single_ranker_records(season_range_low, season_range_high, rankers, rankings, mmad_teams, teams, games):
    # set brackets
    season_range = range(season_range_low, season_range_high + 1)

    records = dict()
    for season in season_range:
        for ranker in rankers[season]:
            records.setdefault(ranker, dict())

            bracket = get_bracket(ranker, rankings[season], mmad_teams[season], teams)
            set_selections(games[season], bracket)
            score, possible = score_bracket(games[season], bracket)

            records[ranker][season] = score
            # print '{}: {} ({})'.format(ranker, score, possible)

    delimiter = '|'
    header = ['Ranker'] + [str(season) for season in season_range]
    print delimiter.join(header)
    for ranker, record in records.iteritems():
        print_data = [ranker] + [record.get(season, '') for season in season_range]
        print delimiter.join(map(str, print_data))


def compute_pair_ranker_records(season_range_low, season_range_high, votes, rankers, rankings, mmad_teams, teams, games):
    # set brackets
    season_range = range(season_range_low, season_range_high + 1)

    records = dict()

    for season in season_range:
        print season
        n_rankers = len(rankers[season])
        n_pairs = n_rankers*(n_rankers - 1)/2 - n_rankers
        ranker_pairs = set()
        pair_n = 0
        for ranker_1 in rankers[season]:
            for ranker_2 in rankers[season]:
                if ranker_1 != ranker_2:
                    ranker_pair = tuple(sorted([ranker_1, ranker_2]))
                    if ranker_pair not in ranker_pairs:
                        ranker_pairs.add(ranker_pair)
                        pair_n += 1
                        # print '     {} ({}/{}) {}'.format(ranker_pair, pair_n, n_pairs, n_rankers)
                        records.setdefault(ranker_pair, dict())

                        bracket = get_voter_bracket(ranker_pair, votes, rankings[season], mmad_teams[season], teams)
                        set_selections(games[season], bracket)
                        score, possible = score_bracket(games[season], bracket)

                        records[ranker_pair][season] = score

    return records


def compute_random_ranker_score(votes, ranker_set, rankings, mmad_teams, teams, games):
    bracket = get_voter_bracket(ranker_set, votes, rankings, mmad_teams, teams)
    set_selections(games, bracket)
    score, possible = score_bracket(games, bracket)

    return score


def randomized_ranker_score(ranker, noise_magnitude, rankings, mmad_teams, teams, games):
    bracket = get_randomized_bracket(ranker, noise_magnitude, rankings, mmad_teams, teams)
    set_selections(games, bracket)
    score, possible = score_bracket(games, bracket)

    return score


def main():
    season      = 2017
    data_root   = os.path.expanduser('~/Dropbox/Uncertain Principles/Articles/NCAA bracketeering/NCAA Bracket 2017/')
    #history_dir = os.path.join(data_root, 'march-machine-learning-mania-2017')
    history_dir = 'data/kaggle_2018/DataFiles'

    bracket_name = 'from file'
    # bracket_name = 'RPI'

    games = dict()
    seeds = dict()
    mmad_teams = dict()

    teams = read_teams(history_dir)

    #######################################################
    # Score Existing Bracket On In-Progress Tourney Results
    #######################################################

    # set up the slots insert teams by seed into play-in and first round games
    games[season] = read_games(history_dir, season)
    seeds[season] = read_seeds(history_dir, season)
    initialize_bracket(games[season], seeds[season], teams)

    bracket_file = 'bracket.poll_of_polls.test.csv'
    # bracket_file = '/Users/rsharp/PROJECTS/march_madness/data/brackets/bracket.ranker_BIH.stdev_4.0.89.csv'
    # bracket_file = '/Users/rsharp/PROJECTS/march_madness/data/brackets/bracket.ranker_STH.stdev_4.0.6.csv'
    # bracket_file = '/Users/rsharp/PROJECTS/march_madness/data/brackets/bracket.ranker_RPI.stdev_6.0.36.csv'
    # bracket_file = '/Users/rsharp/PROJECTS/march_madness/data/brackets/bracket.ranker_SAG.mascot_14.csv'

    # game_results_file = os.path.join(data_root, '2017_TourneyCompactResults.csv')
    # game_results = read_results(game_results_file, season)
    game_results = dict()
    with open(os.path.join(data_root, '2017_results.csv'), 'r') as input_file:
        for line_number, line in enumerate(input_file):
            if line_number > 0:
                game, team1, name1, score1, team2, name2, score2, Numot = line.strip().split(',')[:8]

                if (score1.strip() != '') and (score2.strip() != ''):
                    if int(score1) > int(score2):
                        Wteam = team1
                        Wscore = score1
                        Lteam = team2
                        Lscore = score2
                    elif int(score1) < int(score2):
                        Lteam = team1
                        Lscore = score1
                        Wteam = team2
                        Wscore = score2
                    else:
                        raise ValueError('ERROR - I thought you couldn\'t have ties')

                    game_results[game] = int(Wteam)

    if bracket_name == 'from file':
        bracket = dict()
        with open(bracket_file, 'r') as input_file:
            for line_number, line in enumerate(input_file):
                team, rank = line.strip().split()
                bracket[int(team)] = float(rank)

    # set the winners of the play-in games
    for game in ['W11', 'W16', 'Y16', 'Z11']:
        games[2017][game]['winner'] = game_results[game]

    rankings = read_rankings(data_root, season)

    total_points = 0
    for r in [1, 2, 3, 4, 5, 6]:
        round = 'R' + str(r)
        update_bracket(round, games[season], teams)
        if round == 'R1':
            mmad_teams = get_mmad_teams(games[season])
            if bracket_name == 'RPI':
                bracket = get_bracket(bracket_name, rankings, mmad_teams, teams)

        points_in_round = play_predicted_ranked_round(round, games[season], bracket, teams, game_results)
        total_points += points_in_round
        print bracket_name, round, points_in_round, total_points


    print 'Champion:', sorted([(rank, teams[team]) for team, rank in bracket.iteritems()])[:10]

    print bracket

if __name__ == '__main__':
    main()