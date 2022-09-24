cd ~/sandbox/howlucky
/usr/local/bin/python3.9 collect_data.py --store_meta 0 --store_prices 1
/usr/local/bin/python3.9 update_releases.py --find_missing 1
