import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), 'database.db')
print('DB path:', DB, 'exists?', os.path.exists(DB))
conn = sqlite3.connect(DB)
c = conn.cursor()
try:
    c.execute('SELECT count(*) FROM logs')
    print('rows in logs:', c.fetchone()[0])
    c.execute('SELECT id, username, predicted_sign, timestamp FROM logs ORDER BY id DESC LIMIT 5')
    rows = c.fetchall()
    if rows:
        for r in rows:
            print(r)
    else:
        print('No recent rows')
except Exception as e:
    print('Error querying DB:', e)
conn.close()
