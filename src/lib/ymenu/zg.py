#!/usr/bin/env python

from datetime import date
try:
    from zeitgeist import client, datamodel
    try:
        iface = client.ZeitgeistDBusInterface()
    except RuntimeError:
        print "Error: Could not connect to Zeitgeist."
        iface = None
except:
    iface = None



def _get(name,maxres, result_type):
    min_days_ago = 14
    time_range = datamodel.TimeRange.from_seconds_ago(min_days_ago * 3600 * 24)
    max_amount_results = maxres

    event_template = datamodel.Event()
    event_template.set_actor('application://%s'%name)

    results = iface.FindEvents(
        time_range, # (min_timestamp, max_timestamp) in milliseconds
        [event_template, ],
        datamodel.StorageState.Any,
        max_amount_results,
        result_type
    )

    # Pythonize the result
    results = [datamodel.Event(result) for result in results]
    return results

def get_recent_for_app(name,maxres):
    if iface == None:
        return []
    return _get(name,maxres, datamodel.ResultType.MostRecentSubjects)

def get_most_used_for_app(name,maxres):
    if iface == None:
        return []
    return _get(name,maxres, datamodel.ResultType.MostPopularSubjects)


if __name__ == "__main__":
    print "Testing with gedit.desktop"
    results = get_recent_for_app("gedit.desktop")
    for event in results:
        timestamp = int(event.timestamp) / 1000 # Zeitgeist timestamps are in msec
        print date.fromtimestamp(timestamp).strftime("%d %B %Y")
        for subject in event.get_subjects():
            print " -", subject.text, ":", subject.uri

