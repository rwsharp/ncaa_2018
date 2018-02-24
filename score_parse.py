from lxml import html
import requests
import pandas

def get_teams(url):
    page = requests.get(url)

    tree = html.fromstring(page.content)

    teams = tree.xpath('/html/body/p/text()')[0].split('\n')

    team_data = {'team': list(),
                 'name': list()}

    for line in teams:
        if line.strip() != '':
            try:
                row = map(lambda s: s.strip(), line.split(','))
            except:
                print 'ERROR:', line
                raise

            team_data['team'].append(int(row[0]))
            team_data['name'].append(row[1])

    teams = pandas.DataFrame(team_data)

    return teams


def get_games(url):
    page = requests.get(url)

    tree = html.fromstring(page.content)

    scores = tree.xpath('/html/body/p/text()')[0].split('\n')

    game_data = {'game': list(),
                 'date': list(),
                 'team1_loc': list(),
                 'team1': list(),
                 'team1_score': list(),
                 'team2_loc': list(),
                 'team2': list(),
                 'team2_score': list()}

    for line in scores:
        if line.strip() != '':
            try:
                row = map(lambda s: int(s.strip()), line.split(','))
            except:
                print 'ERROR:', line
                raise

            game_data['game'].append(row[0])
            game_data['date'].append(row[1])
            game_data['team1'].append(row[2])
            game_data['team1_loc'].append(row[3])
            game_data['team1_score'].append(row[4])
            game_data['team2'].append(row[5])
            game_data['team2_loc'].append(row[6])
            game_data['team2_score'].append(row[7])

    games = pandas.DataFrame(game_data)

    return games


mr_pages = {2008: 74994,
            2009: 87798,
            2010: 97288,
            2011: 101140,
            2012: 179268,
            2013: 193573,
            2014: 203290,
            2015: 267615,
            2016: 284067,
            2017: 292154,
            2018: 298892}

for year, id in  mr_pages.iteritems():
    print 'Getting data for {}.'.format(year)

    teams_page = 'https://www.masseyratings.com/scores.php?s={}&sub=11590&all=1&mode=3&sch=on&exhib=on&format=2'.format(id)
    games_page = 'https://www.masseyratings.com/scores.php?s={}&sub=11590&all=1&mode=3&sch=on&exhib=on&format=1'.format(id)

    teams = get_teams(teams_page)
    games = get_games(games_page)

    games.to_csv('data/games_{}.csv'.format(year))
    teams.to_csv('data/teams_{}.csv'.format(year))


"""
#/html/body/pre/a[682]

https://www.masseyratings.com/scores.php?s=298892&sub=11590&all=1&mode=3&sch=on&exhib=on&format=1

1= home
-1 = away
0 = neutral

ID, date, team1, team1_loc, team1score, team2, team2_loc, team2score
736990,20171023,    86,  1,  94,   112, -1,  78
736994,20171027,   241, -1,  73,   200,  1,  70
736995,20171028,   234,  1,  94,   124, -1,  72
736996,20171029,    80, -1,  76,   228,  1,  70
736997,20171030,   138,  1,  92,   179, -1,  67
736999,20171101,   344,  1,  69,   210, -1,  38
737000,20171102,    51,  1,  83,   243, -1,  69
737001,20171103,    77,  1,  80,   120, -1,  67
737003,20171105,    55,  1,  83,   185, -1,  79
737003,20171105,   292,  0,  84,   198,  0,  54
737003,20171105,   286, -1,  71,    49,  1,  67
737003,20171105,   328, -1,  86,   265,  1,  67
737004,20171106,   212, -1,  92,   105,  1,  85
737008,20171110,     4,  0,  82,   164,  0,  70
737008,20171110,    26,  1,  85,   155, -1,  65
737008,20171110,   208, -1,  65,    27,  1,  59


https://www.masseyratings.com/scores.php?s=298892&sub=11590&all=1&mode=3&sch=on&exhib=on&format=2

1, Abilene_Chr
2, Air_Force
3, Akron
4, Alabama
5, Alabama_A & M
6, Alabama_St
7, Albany_NY
8, Alcorn_St
9, American_Univ
10, Appalachian_St
11, Arizona
12, Arizona_St






# 2008
'https://www.masseyratings.com/scores.php?s=74994&sub=11590'
# 2009
'https://www.masseyratings.com/scores.php?s=87798&sub=11590'
# 2010
'https://www.masseyratings.com/scores.php?s=97288&sub=11590'
# 2011
'https://www.masseyratings.com/scores.php?s=101140&sub=11590'
# 2012
'https://www.masseyratings.com/scores.php?s=179268&sub=11590'
# 2013
'https://www.masseyratings.com/scores.php?s=193573&sub=11590'
# 2014
'https://www.masseyratings.com/scores.php?s=203290&sub=11590'
# 2015
'https://www.masseyratings.com/scores.php?s=267615&sub=11590&all=1&mode=3&sch=on&exhib=on&format=1'
# NCAA Dev 1 2016
teams_page = requests.get('https://www.masseyratings.com/scores.php?s=284067&sub=11590&all=1&mode=3&sch=on&exhib=on&format=2')
games_page = requests.get('https://www.masseyratings.com/scores.php?s=284067&sub=11590&all=1&mode=3&sch=on&exhib=on&format=1')
# NCAA Dev 1 2017
teams_page = requests.get('https://www.masseyratings.com/scores.php?s=292154&sub=11590&all=1&mode=3&sch=on&exhib=on&format=2')
games_page = requests.get('https://www.masseyratings.com/scores.php?s=292154&sub=11590&all=1&mode=3&sch=on&exhib=on&format=1')
# NCAA Dev 1 2018
teams_page = requests.get('https://www.masseyratings.com/scores.php?s=298892&sub=11590&all=1&mode=3&sch=on&exhib=on&format=2')
games_page = requests.get('https://www.masseyratings.com/scores.php?s=298892&sub=11590&all=1&mode=3&sch=on&exhib=on&format=1')


"""