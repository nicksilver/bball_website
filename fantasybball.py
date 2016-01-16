import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
import datetime


def statspergame(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")

    # scrape team names
    teams = soup.find_all('td', class_='sortableTeamName')
    team_names = []
    for team in teams:
        lis = team.a
        name = lis['title'].split(" (")[0]
        team_names.append(name)

    def get_stats(stat_name):
        """function to scrape stats"""
        stats = soup.find_all('td', class_=stat_name)
        lis = []
        for stat in stats:
            n = float(stat.find(text=True))
            lis.append(n)
        return lis

    # scrape stats
    fg = get_stats('precise sortableStat19')  # field goal percentages
    ft = get_stats('precise sortableStat20')  # free throw percentages
    tpm = get_stats('precise sortableStat17')  # three pointers made
    reb = get_stats('precise sortableStat6')  # rebounds
    ast = get_stats('precise sortableStat3')  # assists
    stl = get_stats('precise sortableStat2')  # steals
    blk = get_stats('precise sortableStat1')  # blocks
    pts = get_stats('precise sortableStat0')  # points
    gp = get_stats('sortableGP')  # games played
    moves = get_stats('sortableMoves')  # number of moves

    # create dataframe
    dic = {'FG': fg, 'FT': ft, '3PM': tpm, 'REB': reb, 'AST': ast, 'STL': stl,
           'BLK': blk, 'PTS': pts, 'GP': gp, 'MOVES': moves}
    df = pd.DataFrame(dic, index=team_names)

    # calculate stats per games played
    df_new = df.div(df.GP, axis='index')
    df_new.FG = df.FG
    df_new.FT = df.FT
    df_new.GP = df.GP
    df_new.MOVES = df.MOVES

    # rescore and rank
    df_ranks = df_new.rank(axis=0, method='average')
    del df_ranks['MOVES']
    del df_ranks['GP']
    df_ranks['TOTAL'] = df_ranks.sum(axis=1)
    df_new['TOTAL'] = df_ranks['TOTAL']
    del df_new['MOVES']
    del df_new['GP']
    df_new = np.around(df_new, 2)

    ranks = df_ranks.sort('TOTAL', ascending=False)
    stats = df_new.sort('TOTAL', ascending=False)

    return ranks, stats.drop('TOTAL', 1)


def injurylist():
    url = 'http://www.rotoworld.com/teams/injuries/nba/all/'
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    this_year = str(datetime.datetime.now().year)

    # scrape team names
    tables = soup.find_all('table')
    players = []
    dates = []
    status = []
    for row in tables:
        for guy in row.findAll('tr')[1:]:
            player = guy.findAll('a')[0].text
            player = player.encode('ascii', 'ignore').decode('ascii')
            players.append(player)
            date = guy.findAll('div', class_='date')[0].text
            date = this_year + date.encode('ascii', 'ignore').decode('ascii')
            dates.append(date)
            stat = guy.findAll('div', class_="impact")[0].text
            stat = stat.encode('ascii', 'ignore').decode('ascii')
            status.append(stat)

    d = {'Date': dates, 'Player': players, 'Status': status}
    data = pd.DataFrame(d)
    data['Date'] = pd.to_datetime(data['Date'], format="%Y%b%d")

    # Correct year in dates. This will need to be changed each season.
    pd.options.mode.chained_assignment = None  # default='warn'
    data.Date[data.Date.dt.month > 7] = data.Date[data.Date.dt.month > 7].map(lambda x: x.replace(year=2015))

    return data.sort('Date', ascending=False)
