from dbaccs import DBConnection

import config.app_config as appconfig
import status_tracker as tracker
import dateutil as dateutil

import datetime
import configparser
import subprocess
import sys

config = configparser.ConfigParser()
config.read('config/config.ini')

def get_db_config(anapp):
    appattribs = appconfig.apps.get(anapp)
    db_config = config[appattribs["db-config"]]
    return {
        "host": db_config["host"],
        "user": db_config["user"],
        "password": db_config["password"],
        "dbname": db_config["db_name"],
    }


def check_user_folder(user, file_prefix, check_date):
    ftp_host = config['FTPHOST']["host"]
    ftp_users_dir = config['FTPHOST']["users-dir"]
    ckdate = check_date.replace('-', '')
    cmd = "sudo find %s/%s/ -name '%s%s.csv' -printf '%%p %%k KB'" % (ftp_users_dir, user, file_prefix, ckdate)
    print(cmd)
    ssh = subprocess.Popen(["ssh", ftp_host, cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    results = ssh.stdout.readlines()
    if not results:
        error = ssh.stderr.readlines()
        tracker.record_failure(user, file_prefix)
        print(sys.stderr, "ERROR: %s" % error)
    else:
        print(results)
        tracker.record_success(user, file_prefix)


def daily_file_deliver_check(select_app):
    today = datetime.datetime.today().date()
    appattribs = appconfig.apps.get(select_app)
    print(appattribs)
    db_config = get_db_config(select_app)
    db = DBConnection(db_config["host"], db_config["user"], db_config["password"], db_config["dbname"])
    db.query("SELECT * FROM %s WHERE %s = '%s'" % (appattribs["subscriber-table"], appattribs["subscriber-column"],
                                                   appattribs["subscriber-key"]))
    r = db.fetchall()
    should_check_today = False
    if appattribs["delivered-on"] == 'us-trading-days':
        ckdate = dateutil.next_trading_day()
        # check only during the trading dates for US as on wknds & holidays they're not published
        if str(ckdate) == str(today):
            should_check_today = True

    elif appattribs["delivered-on"] == "weekdays":
        nyt_lead = appattribs["nyt-lead"] if "nyt-lead" in appattribs.keys() else 0
        skip_check_days = appattribs["skip-check-days"] if "skip-check-days" in appattribs.keys() else None

        ckdate = dateutil.next_trading_day(nyt_lead)

        # Some files have skip check days since files aren't produced for the next trading day. Have to skip
        # to avoid false calls.
        if skip_check_days is not None and today.weekday() in skip_check_days:
            should_check_today = False
        else:
            should_check_today = True
    else:
        raise Exception("Wrong frequency")

    if should_check_today:
        for x in r:
            check_user_folder(x[0], appattribs["file-prefix"], ckdate)


def daily_file_deliver_check_all():
    allapps = appconfig.apps.keys()
    current_tm = datetime.datetime.now()
    for a in allapps:
        publish_by_str = appconfig.apps[a]["publish-by"]
        publish_by_dt = datetime.datetime.strptime("%s %s:00" % (datetime.datetime.today().date(), publish_by_str),
                                                   '%Y-%m-%d %H:%M:%S')
        if publish_by_dt <= current_tm <= (publish_by_dt + datetime.timedelta(hours=1)):
            daily_file_deliver_check(a)


if __name__ == "__main__":
    daily_file_deliver_check_all()
