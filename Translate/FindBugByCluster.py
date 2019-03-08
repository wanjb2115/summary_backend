import json
import re
import Levenshtein

with open('Cluster/errorHub.json') as f:
    errorhub = json.load(f)

with open('Cluster/errorIntro.json') as f:
    errorIntro = json.load(f)


def findBugByCluster(eventsequence):
    error_words = ''
    error_list = []
    for e in eventsequence:
        error_words += e['PackageName'] + ' ' + e['EventType'] + ' ' + \
                       re.findall(' ClassName: (.+?); ', e['Action'])[0]
        try:
            text = re.findall(' Text: \[(.+)\]; ', e['Action'])[0]
            error_words += text
        except IndexError:
            error_words += ' '
            pass
    for e in errorhub:
        for key, value in e.items():
            for little in value:
                for l in little:
                    e_words = ''
                    for e in l[0]:
                        e_words += e['PackageName'] + ' ' + e['EventType'] + ' ' + \
                                   re.findall(' ClassName: (.+?); ', e['Action'])[0]
                        try:
                            text = re.findall(' Text: \[(.+)\]; ', e['Action'])[0]
                            e_words += text
                        except IndexError:
                            e_words += ' '
                            pass

                    sim = Levenshtein.ratio(e_words, error_words)
                    if sim > 0.98:
                        error_list.append([sim*l[1], key, l[0], l[1]])
    error_list = sorted(error_list, key=lambda x: x[0], reverse=True)
    if len(error_list) >= 1:
        return error_list[0]
    else:
        return None

