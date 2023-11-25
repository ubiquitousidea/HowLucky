from datetime import datetime
import pandas as pd
import re
logfile = "/var/log/nginx/access.log"
# logfile = "access.log"
log_data = []
R0 = r"^([\d.]+) (\S+) (\S+) \[([\w:/]+\s[+-]\d{4})\] \"(.+?)\" (\d{3}) (\d+) \"([^\"]+)\" \"(.+?)\""
with open(logfile, "r") as f:
    lines = f.readlines()
    for line in lines:
        s = re.search(R0, line)
        log_data.append({
            'ip': s.group(1),
            'timestamp': datetime.strptime(s.group(4).split(' ')[0], '%d/%b/%Y:%H:%M:%S'),
            'request': s.group(5),
            'status': s.group(6),
            'length': s.group(7),
            'host': s.group(8),
            'user_agent': s.group(9)
        })
        
log_data = pd.DataFrame(log_data)

unique_ips = log_data.ip.drop_duplicates().values
print({'unique_ips': unique_ips, 'n': len(unique_ips)})



