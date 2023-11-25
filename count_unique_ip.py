from database.database_util import DB_KEYS_POSTGRES
from database.database_util_postgres import DBPostgreSQL
from datetime import datetime, timezone
import pandas as pd
import re

DB = DBPostgreSQL(DB_KEYS_POSTGRES)

logfile = "/var/log/nginx/access.log"
# logfile = "access.log"

log_data = []
R0 = r"^([\d.]+) (\S+) (\S+) \[([\w:/]+\s[+-]\d{4})\] \"(.+?)\" (\d{3}) (\d+) \"([^\"]+)\" \"(.+?)\""
with open(logfile, "r") as f:
    lines = f.readlines()
    for line in lines:
        s = re.search(R0, line)
        ts = datetime.strptime(s.group(4).split(' ')[0], '%d/%b/%Y:%H:%M:%S')
        ts = ts.replace(tzinfo=timezone.utc)
        log_data.append({
            'ip': s.group(1),
            'timestamp': ts,
            'request': s.group(5),
            'status': s.group(6),
            'length': s.group(7),
            'host': s.group(8),
            'user_agent': s.group(9)
        })
        
log_data = pd.DataFrame(log_data)

DB.insert_rows(df=log_data, tbl='nginx', schema='logs')
unique_ips = log_data.ip.drop_duplicates().sort_values().values.tolist()

print({'unique_ips': len(unique_ips)})
print({'ips': unique_ips})



