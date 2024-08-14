import csv
import datetime
import os
import sound_alarm as alarm

SUCCESS_TRACKER = '/tmp/apps-success-tracker-%s.csv' % str(datetime.datetime.today().date())
FAILURE_TRACKER = '/tmp/apps-failure-tracker-%s.csv' % str(datetime.datetime.today().date())


def write_success(user, signal):
    with open(SUCCESS_TRACKER, "a") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([user, signal])


def write_failure(user, signal):
    now = datetime.datetime.now()
    with open(FAILURE_TRACKER, "a") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([str(now), user, signal])


def record_failure(user, signal):
    track_fail = read_failure()
    is_present = False
    now = datetime.datetime.now()
    for t, u, s in track_fail:
        t_dt = datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f')
        delta = (now-t_dt).seconds
        if u == user and s == signal and delta <= 300:
            is_present = True
            break
    if not is_present:
        write_failure(user, signal)
        alarm.sound_alarm("CRITICAL_ERROR: %s Not delivered" % signal, "%s Not delivered " % signal)


def record_success(user, signal):
    track_suc = read_success()
    is_present = False
    for u, s in track_suc:
        if u == user and s == signal:
            is_present = True
            break
    if not is_present:
        write_success(user, signal)


def read_success():
    if not os.path.isfile(SUCCESS_TRACKER):
        open(SUCCESS_TRACKER, 'a').close()

    success_list = list()
    with open(SUCCESS_TRACKER, "r") as f:
        csv_reader = csv.reader(f)
        success_list = list(csv_reader)

    return success_list


def read_failure():
    if not os.path.isfile(FAILURE_TRACKER):
        open(FAILURE_TRACKER, 'a').close()

    failure_list = list()
    with open(FAILURE_TRACKER, "r") as f:
        csv_reader = csv.reader(f)
        failure_list = list(csv_reader)

    return failure_list
