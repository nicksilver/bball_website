import sqlite3
import datetime
import fantasybball as fb
import pandas as pd
import numpy as np

# ESPN fantasy bball website url
url = 'http://games.espn.go.com/fba/standings?leagueId=72928&seasonId=2016'

# Today's date
date = str(datetime.date.today())

# Connect to sqlite database
conn = sqlite3.connect('../stats.sqlite')
cur = conn.cursor()

# Calculate daily rank and stats per game played
ranks, stats = fb.statspergame(url)

# Add date to database
print "Adding data to database..."
cur.execute('''INSERT OR IGNORE INTO Dates (date) VALUES (?)''', (date, ))
cur.execute('''SELECT id FROM Dates WHERE date = ?''', (date, ))
date_id = cur.fetchone()[0]

# Add data to team Table
for team in ranks.index:
    name = team
    THREES_r = ranks.loc[name]['3PM']
    AST_r = ranks.loc[name]['AST']
    BLK_r = ranks.loc[name]['BLK']
    FG_r = ranks.loc[name]['FG']
    FT_r = ranks.loc[name]['FT']
    PTS_r = ranks.loc[name]['PTS']
    REB_r = ranks.loc[name]['REB']
    STL_r = ranks.loc[name]['STL']
    TOTAL = ranks.loc[name]['TOTAL']
    THREES_s = stats.loc[name]['3PM']
    AST_s = stats.loc[name]['AST']
    BLK_s = stats.loc[name]['BLK']
    FG_s = stats.loc[name]['FG']
    FT_s = stats.loc[name]['FT']
    PTS_s = stats.loc[name]['PTS']
    REB_s = stats.loc[name]['REB']
    STL_s = stats.loc[name]['STL']
    cur.execute('''INSERT OR IGNORE INTO Teams (name) VALUES (?)''', (name, ))
    cur.execute('''SELECT id FROM Teams WHERE name = ?''', (name, ))
    team_id = cur.fetchone()[0]
    cur.execute('''INSERT OR IGNORE INTO Pergame_rank
                (date_id, team_id, THREES, AST, BLK, FG, FT, PTS, REB, STL,
                TOTAL) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (date_id, team_id, THREES_r, AST_r, BLK_r, FG_r, FT_r, PTS_r,
                    REB_r, STL_r, TOTAL))
    cur.execute('''INSERT OR IGNORE INTO Pergame_stats
                (date_id, team_id, THREES, AST, BLK, FG, FT, PTS, REB, STL)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (date_id, team_id, THREES_s, AST_s, BLK_s, FG_s, FT_s, PTS_s,
                    REB_s, STL_s))

    # Calculate change data
    if date_id > 1:
        # Selects date_id from the previous day
        cur.execute('''SELECT id FROM Dates ORDER BY id DESC LIMIT 1, 1''')
        date_p = cur.fetchone()[0]

        # Selects stats from previous day
        cur.execute('''SELECT THREES, AST, BLK, FG, FT, PTS, REB, STL FROM
            Pergame_stats WHERE team_id = ? AND date_id = ?''',
                    (team_id, date_p))
        thr_p, ast_p, blk_p, fg_p, ft_p, pts_p, reb_p, stl_p = cur.fetchone()

        # Selects total rank from previous day
        cur.execute('''SELECT TOTAL FROM Pergame_rank WHERE team_id = ? AND
            date_id = ?''', (team_id, date_p))
        total_p = cur.fetchone()[0]

        # Calculates change from previous stats
        thr_c = np.around(THREES_s - thr_p, 2)
        ast_c = np.around(AST_s - ast_p, 2)
        blk_c = np.around(BLK_s - blk_p, 2)
        fg_c = np.around(FG_s - fg_p, 2)
        ft_c = np.around(FT_s - ft_p, 2)
        pts_c = np.around(PTS_s - pts_p, 2)
        reb_c = np.around(REB_s - reb_p, 2)
        stl_c = np.around(STL_s - stl_p, 2)
        total_c = np.around(TOTAL - total_p, 2)
    else:
        thr_c = 0
        ast_c = 0
        blk_c = 0
        fg_c = 0
        ft_c = 0
        pts_c = 0
        reb_c = 0
        stl_c = 0
        total_c = 0

    # Inserts change stats into database
    cur.execute('''INSERT OR IGNORE INTO Change_stats
            (date_id, team_id, THREES, AST, BLK, FG, FT, PTS, REB, STL, TOTAL)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (date_id, team_id, thr_c, ast_c, blk_c, fg_c, ft_c, pts_c,
                    reb_c, stl_c, total_c))

print "Committing to database..."
conn.commit()
conn.close()
