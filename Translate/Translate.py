import time
import copy
from .FindBugByCluster import *
from .FindBugBySummary import *
from .SliceEvent import *

with open('Cluster/errorHub.json') as f:
    errorhub = json.load(f)

with open('Cluster/errorIntro.json') as f:
    errorIntro = json.load(f)

with open('translate.json') as f:
    translate = json.load(f)

android_event_type = translate['android_event_type']
event_class_type = translate['event_class_type']


def process_OutBounds(OutBounds):
    position_height = ''
    num = re.findall('\d+', OutBounds)
    try:
        left, top, right, bottom = int(num[0]), int(num[1]), int(num[2]), int(num[3])
    except IndexError:
        return ''
    middle_long = 360
    middle_height = 640
    long = right - left
    height = bottom - top
    if left + right > 1440 or top + bottom > 2560:
        return 'In wrong place!'

    if long == 720 and height == 1280:
        position = 'On the current screen'
        return position
    if left > middle_long:
        position_long = 'right'
    elif right < middle_long:
        position_long = 'left'
    else:
        position_long = 'middle'
    if top < middle_height:
        position_height = 'bottom'
    elif top > middle_height:
        position_height = 'top'
    else:
        position_long = ''
    if (top + bottom) / 2 == middle_height and (left + right) / 2 == middle_long:
        position_long = 'center'
        position_height = ''
    return 'In a ' + str(long) + 'px by ' + str(height) + 'px rectangle at the ' + str(position_height) + ' ' + str(
        position_long) + ' of the screen'


def highRiskEventTranslate(slice):
    with open('Summary/error_summary_hub.json') as f:
        error_high_event = json.load(f)
    error_high = error_high_event[0]

    error_hub = []

    for error_key in error_high:
        error_length = len(error_high[error_key])
        slice_length = len(slice)
        if slice_length < error_length or error_length <= 2:
            continue
        else:
            count_list = []
            count = 0
            for i in range(slice_length - error_length):
                for j in range(error_length):
                    if slice[i + j][0] in error_high[error_key]:
                        count += 1
                count_list.append(float(count) / error_length)
                count = 0
            if len(count_list) > 0:
                count_max = max(count_list)
                if count_max >= 0.75:
                    error_hub.append([slice, count_list.index(count_max), error_length, error_key, count_max])
    if len(error_hub) != 0:
        error_hub = sorted(error_hub, key=lambda x: x[3])
        return error_hub[0]
    else:
        return None


def highSummary(sequence):
    report = ''
    timeArray = time.localtime(sequence[0]['SyscTime'] / 1000)
    start_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
    timeArray = time.localtime(sequence[-1]['SyscTime'] / 1000)
    end_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
    all_event_type = []
    all_class_name = []
    for e in sequence:
        if e['EventType'] not in all_event_type:
            all_event_type.append(e['EventType'])
        className = e['Action']['ClassName']
        if className not in all_class_name:
            all_class_name.append(className)
    report += '    During ' + start_formatTime + ' to ' + end_formatTime + ', the user made some actions like'

    for t in [android_event_type[x] for x in all_event_type]:
        report += t + ' '
    report += 'And all is well.\n'
    return report


def goTranslate(file_name, event_list, slice_event, logcat_list):
    complete_whole = 0
    high_risk_whole = 0
    complete_whole_list = []
    high_risk_whole_list = []
    suspected_whole_list = []
    suspected_test_actions_list = []
    normal_list = []

    report_overall = '''
        Test person：person_name
        Test software：software_name
        Test statistics：
            The test data was captured by Kikbug tool. The test duration is total test_time seconds and  event_count event logs are captured. 
            There are sequence_count analyzable event sequences are segmented by S-CAT frame.And there are repeat_count event sequences including same test action.
            So unique_count event sequences are analysed as followed.There are complete_count confirmed bugs,high_risk_count high risk bugs and suspected_count suspected bug. 
            The following is detailed summary of the segmented event sequence. 
        Test report：
            '''
    person_name = re.findall('\d+_\d+', file_name)[0]
    software_name = event_list[0]['PackageName']
    test_time = str((event_list[-1]['SyscTime'] - event_list[0]['SyscTime']) / 1000)
    event_count = str(len(event_list))
    sequence_count = len(slice_event)
    refer_repeat_sequence_pre = findRepeatSequence(slice_event)
    for key in refer_repeat_sequence_pre:
        refer_repeat_sequence_pre[key].append(key)
        refer_repeat_sequence_pre[key] = sorted(refer_repeat_sequence_pre[key])
    refer_repeat_sequence = list(refer_repeat_sequence_pre.values())
    slice_event = returnNoneRepeatSequence(slice_event, refer_repeat_sequence)

    sequence_norepeat_count = len(slice_event)
    repeat_sequence_count = sequence_count - sequence_norepeat_count
    for sequence in slice_event:
        bugfind = findBugByCluster(sequence)
        confirmed_find = find_confirmed(sequence, logcat_list)
        if find_confirmed(sequence, logcat_list):
            complete_whole += 1
        elif bugfind:
            high_risk_whole += 1
            errorText = errorIntro[bugfind[1]]

    suspected = theCountOfRepeatEvent(summaryByRepeat(makeUpFormat(slice_event)))

    report_overall = report_overall.replace('person_name', person_name)
    report_overall = report_overall.replace('software_name', software_name)
    report_overall = report_overall.replace('test_time', test_time)
    report_overall = report_overall.replace('event_count', event_count)
    report_overall = report_overall.replace('sequence_count', str(sequence_count))
    report_overall = report_overall.replace('repeat_count', str(repeat_sequence_count))
    report_overall = report_overall.replace('unique_count', str(sequence_norepeat_count))
    report_overall = report_overall.replace('complete_count', str(complete_whole))
    report_overall = report_overall.replace('high_risk_count', str(high_risk_whole))
    report_overall = report_overall.replace('suspected_count', str(suspected))
    suspected_whole = 0

    report_confirmed = ''
    report_high_risk = ''
    report_suspected_repeat = ''
    report_suspected_event = ''
    report_normal = ''
    refer = summaryByRepeat(makeUpFormat(slice_event))
    num = 0
    # if complete_whole != 0:
    #     report_confirmed +='                                                             -------------------------Confirmed bug-------------------------\n'
    for r in range(len(refer)):
        sequence = slice_event[r]

        refer_repeat = refer_repeat_sequence[r]
        repeat = ''
        if len(refer_repeat) > 1:
            for p in refer_repeat[1:]:
                repeat += '( Sequence ' + str(p + 1)
            repeat += ' contains the same test actions.)'
        translate_refer = refer[r]

        bugfind = findBugByCluster(sequence)
        confirmed_find = find_confirmed(sequence, logcat_list)
        complete = 0
        suspected = theCountOfRepeatEventBySlice(summaryByRepeatBySlice(makeUpFormatBySlice(sequence)))

        if confirmed_find:
            complete_whole_list.append(str(refer_repeat[0] + 1))
            report_confirmed += '  ' + str(num + 1) + '.Sequence ' + str(
                refer_repeat[0] + 1) + ' of events: ' + repeat + '\n'

            report_confirmed += '    i.Start time：' + time.strftime("%Y/%m/%d %H:%M:%S",
                                                                    time.localtime(sequence[0][
                                                                                       'SyscTime'] / 1000)) + '\n'
            report_confirmed += '    ii.End Time： ' + time.strftime("%Y/%m/%d %H:%M:%S",
                                                                    time.localtime(sequence[-1][
                                                                                       'SyscTime'] / 1000)) + '\n'
            report_confirmed += '    iii.Category：Confirmed bug!\n'
            report_confirmed += '    iv.Detailed description：\n'
            n = 0
            for tr in range(len(translate_refer)):
                refer_length = len(translate_refer[tr])
                for i in range(refer_length):
                    translate_refer[tr][i] = sequence[n]
                    n += 1
            for tr in range(len(translate_refer)):
                refer_length = len(translate_refer[tr])
                if refer_length == 1:
                    e = translate_refer[tr][0]
                    # isFullpre = -1
                    timeArray = time.localtime(e['SyscTime'] / 1000)
                    formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                    try:
                        outBounds = "In " + e['OutBounds'] + '.'
                    except KeyError:
                        outBounds = ''
                    if makeEventFormat(e) == '02':
                        report_confirmed += '    ' + formatTime + ' The user enter the main application.' + '\n'
                        continue
                    className = e['Action']['ClassName']
                    Text = e['Action']['Text']
                    Text = Text.replace('[', '')
                    Text = Text.replace(']', '')

                    if len(Text) > 1:
                        Text = "The text is " + Text + '.'
                    else:
                        Text = ''

                    report_confirmed += '    ' + formatTime + ' ' + process_OutBounds(outBounds) + ', ' + \
                                        android_event_type[e[
                                            'EventType']] + "Related class name is " + className + '.' + Text + '\n'
                elif refer_length < 4:
                    timeArray = time.localtime(translate_refer[tr][0]['SyscTime'] / 1000)
                    start_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                    timeArray = time.localtime(translate_refer[tr][-1]['SyscTime'] / 1000)
                    end_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                    className = translate_refer[tr][0]['Action']['ClassName']
                    report_confirmed += '    ' + start_formatTime + ' - ' + end_formatTime + ' ' + str(
                        len(translate_refer[tr])) + ' times of' + android_event_type[translate_refer[tr][0][
                        'EventType']] + "Related class name is " + className + '.\n'
                elif refer_length >= 4:
                    timeArray = time.localtime(translate_refer[tr][0]['SyscTime'] / 1000)
                    start_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                    timeArray = time.localtime(translate_refer[tr][-1]['SyscTime'] / 1000)
                    end_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                    className = translate_refer[tr][0]['Action']['ClassName']
                    report_confirmed += 'Suspect bug!        ' + start_formatTime + ' - ' + end_formatTime + ' ' + str(
                        len(translate_refer[tr])) + ' times of' + android_event_type[translate_refer[tr][0][
                        'EventType']] + "Related class name is " + className + '.\n'
            if confirmed_find:
                report_confirmed += 'Confirmed bug!  -----Confirmed bug logcat information:\n'
                start_time = sequence[0]['SyscTime']
                end_time = sequence[-1]['SyscTime']
                logcat_error_log = {}

                for l in logcat_list:
                    if int(l['SyscTime']) >= int(start_time) and int(l['SyscTime']) <= int(end_time) + 1000 and l[
                        'priority'] == 'E':
                        if l['message'] not in logcat_error_log:
                            logcat_error_log[l['message']] = {}
                            logcat_error_log[l['message']]['tag'] = l['tag']
                            logcat_error_log[l['message']]['time'] = []
                        logcat_error_log[l['message']]['time'].append(l['SyscTime'])
                for e in logcat_error_log:
                    report_confirmed += '    ' + time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(
                        logcat_error_log[e]['time'][0] / 1000)) + '-' + time.strftime("%Y/%m/%d %H:%M:%S",
                                                                                      time.localtime(
                                                                                          logcat_error_log[e]['time'][
                                                                                              -1] / 1000)) + ' The logcat throw ' + str(
                        len(logcat_error_log[e]['time'])) + ' ERROR logs continuous of ' + logcat_error_log[e][
                                            'tag'] + '.And the message is' + e + '\n'
            report_confirmed += ' \n'
            num += 1
    # if high_risk_whole != 0:
    #     report_high_risk += '                                                             -------------------------High risk bug-------------------------\n'
    for r in range(len(refer)):
        sequence = slice_event[r]
        refer_repeat = refer_repeat_sequence[r]
        repeat = ''
        if len(refer_repeat) > 1:
            for p in refer_repeat[1:]:
                repeat += '( Sequence ' + str(p + 1)
            repeat += ' contains the same test actions.)'
        translate_refer = refer[r]
        bugfind = findBugByCluster(sequence)
        confirmed_find = find_confirmed(sequence, logcat_list)
        high_risk = 0
        if bugfind:
            if bugfind[0] == 0.95:
                pass
            else:
                high_risk += 1
                errorText = errorIntro[bugfind[1]]
        if high_risk != 0 and not confirmed_find:
            high_risk_whole_list.append(str(refer_repeat[0] + 1))
            report_high_risk += '  ' + str(num + 1) + '.Sequence ' + str(
                refer_repeat[0] + 1) + ' of events: ' + repeat + '\n'

            report_high_risk += '    i.Start time：' + time.strftime("%Y/%m/%d %H:%M:%S",
                                                                    time.localtime(sequence[0][
                                                                                       'SyscTime'] / 1000)) + '\n'
            report_high_risk += '    ii.End Time： ' + time.strftime("%Y/%m/%d %H:%M:%S",
                                                                    time.localtime(sequence[-1][
                                                                                       'SyscTime'] / 1000)) + '\n'
            report_high_risk += '    iii.Category：High-risk bug!\n'
            if high_risk != 0:
                report_high_risk += '%.2f' % (float(bugfind[
                                                        0]) * 100) + '% bug!    The bug message might be:' + errorText + '.The accuracy is ' + "%.4f" % float(
                    bugfind[0]) + '\n'

            report_high_risk += '    iv.Detailed description：\n'
            n = 0
            for tr in range(len(translate_refer)):
                refer_length = len(translate_refer[tr])
                for i in range(refer_length):
                    translate_refer[tr][i] = sequence[n]
                    n += 1
            for tr in range(len(translate_refer)):
                refer_length = len(translate_refer[tr])
                if refer_length == 1:
                    e = translate_refer[tr][0]
                    # isFullpre = -1
                    timeArray = time.localtime(e['SyscTime'] / 1000)
                    formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                    try:
                        outBounds = "In " + e['OutBounds'] + '.'
                    except KeyError:
                        outBounds = ''
                    if makeEventFormat(e) == '02':
                        report_high_risk += '    ' + formatTime + '， The user enter the main application.\n'
                        continue
                    className = e['Action']['ClassName']
                    Text = e['Action']['Text']
                    Text = Text.replace('[', '')
                    Text = Text.replace(']', '')

                    if len(Text) > 1:
                        Text = "The text is " + Text + '.'
                    else:
                        Text = ''

                    report_high_risk += '    ' + formatTime + ' ' + process_OutBounds(outBounds) + ', ' + \
                                        android_event_type[e[
                                            'EventType']] + "Related class name is " + className + '.' + Text + '\n'
                elif refer_length < 4:
                    timeArray = time.localtime(translate_refer[tr][0]['SyscTime'] / 1000)
                    start_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                    timeArray = time.localtime(translate_refer[tr][-1]['SyscTime'] / 1000)
                    end_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                    className = translate_refer[tr][0]['Action']['ClassName']
                    report_high_risk += '    ' + start_formatTime + ' - ' + end_formatTime + ' ' + str(
                        len(translate_refer[tr])) + ' times of ' + android_event_type[translate_refer[tr][0][
                        'EventType']] + "Related class name is " + className + '.\n'
                elif refer_length >= 4:
                    timeArray = time.localtime(translate_refer[tr][0]['SyscTime'] / 1000)
                    start_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                    timeArray = time.localtime(translate_refer[tr][-1]['SyscTime'] / 1000)
                    end_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                    className = translate_refer[tr][0]['Action']['ClassName']
                    report_high_risk += 'Suspect bug!  ' + start_formatTime + ' - ' + end_formatTime + ' ' + str(
                        len(translate_refer[tr])) + ' times of ' + android_event_type[translate_refer[tr][0][
                        'EventType']] + "Related class name is " + className + '.\n'
            report_high_risk += ' \n'
            num += 1
    # if suspected_whole != 0:
    #     report_suspected_repeat +='                                                             -------------------------Suspected bug-------------------------\n'
    for r in range(len(refer)):
        sequence = slice_event[r]
        refer_repeat = refer_repeat_sequence[r]
        repeat = ''
        if len(refer_repeat) > 1:
            for p in refer_repeat[1:]:
                repeat += '( Sequence ' + str(p + 1)
            repeat += ' contains the same test actions.)'
        translate_refer = refer[r]
        bugfind = findBugByCluster(sequence)
        confirmed_find = find_confirmed(sequence, logcat_list)
        high_risk = 0
        suspected = theCountOfRepeatEventBySlice(summaryByRepeatBySlice(makeUpFormatBySlice(sequence)))

        if suspected != 0 and not confirmed_find:
            suspected_whole += 1
            suspected_whole_list.append(str(refer_repeat[0] + 1))
            report_suspected_repeat += '  ' + str(num + 1) + '.Sequence ' + str(
                refer_repeat[0] + 1) + ' of events: ' + repeat + '\n'

            report_suspected_repeat += '    i.Start time：' + time.strftime("%Y/%m/%d %H:%M:%S",
                                                                           time.localtime(sequence[0][
                                                                                              'SyscTime'] / 1000)) + '\n'
            report_suspected_repeat += '    ii.End Time： ' + time.strftime("%Y/%m/%d %H:%M:%S",
                                                                           time.localtime(sequence[-1][
                                                                                              'SyscTime'] / 1000)) + '\n'
            report_suspected_repeat += '    iii.Category：Suspected bug!' + '\n'
            if high_risk != 0:
                report_suspected_repeat += '%.2f' % (float(bugfind[
                                                               0]) * 100) + '% bug!    The bug message might be: ' + errorText + '.The accuracy is ' + "%.4f" % float(
                    bugfind[0]) + '\n'

            report_suspected_repeat += '    iv.Detailed description：' + '\n'
            n = 0
            for tr in range(len(translate_refer)):
                refer_length = len(translate_refer[tr])
                for i in range(refer_length):
                    translate_refer[tr][i] = sequence[n]
                    n += 1
            for tr in range(len(translate_refer)):
                refer_length = len(translate_refer[tr])
                if refer_length == 1:
                    e = translate_refer[tr][0]
                    # isFullpre = -1
                    timeArray = time.localtime(e['SyscTime'] / 1000)
                    formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                    try:
                        outBounds = "In " + e['OutBounds'] + '.'
                    except KeyError:
                        outBounds = ''
                    if makeEventFormat(e) == '02':
                        report_suspected_repeat += '    ' + formatTime + ' The user enter the main application.' + '\n'
                        continue
                    className = e['Action']['ClassName']
                    Text = e['Action']['Text']
                    Text = Text.replace('[', '')
                    Text = Text.replace(']', '')

                    if len(Text) > 1:
                        Text = "The text is " + Text + '.'
                    else:
                        Text = ''

                    report_suspected_repeat += '    ' + formatTime + ' ' + process_OutBounds(outBounds) + ', ' + \
                                               android_event_type[e[
                                                   'EventType']] + "Related class name is " + className + '.' + Text + '\n'
                elif refer_length < 4:
                    timeArray = time.localtime(translate_refer[tr][0]['SyscTime'] / 1000)
                    start_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                    timeArray = time.localtime(translate_refer[tr][-1]['SyscTime'] / 1000)
                    end_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                    className = translate_refer[tr][0]['Action']['ClassName']
                    report_suspected_repeat += '    ' + start_formatTime + ' - ' + end_formatTime + ' ' + str(
                        len(translate_refer[tr])) + ' times of' + android_event_type[translate_refer[tr][0][
                        'EventType']] + "Related class name is " + className + '.\n'
                elif refer_length >= 4:
                    timeArray = time.localtime(translate_refer[tr][0]['SyscTime'] / 1000)
                    start_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                    timeArray = time.localtime(translate_refer[tr][-1]['SyscTime'] / 1000)
                    end_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                    className = translate_refer[tr][0]['Action']['ClassName']
                    report_suspected_repeat += 'Suspect bug!  ' + start_formatTime + ' - ' + end_formatTime + ' ' + str(
                        len(translate_refer[tr])) + ' times of ' + android_event_type[translate_refer[tr][0][
                        'EventType']] + "Related class name is " + className + '.\n'
            report_suspected_repeat += ' \n'
            num += 1
    suspected_test_actions_count = 0
    for r in range(len(refer)):
        sequence = slice_event[r]
        refer_repeat = refer_repeat_sequence[r]
        repeat = ''
        if len(refer_repeat) > 1:
            for p in refer_repeat[1:]:
                repeat += '( Sequence ' + str(p + 1)
            repeat += ' contains the same test actions.)'
        translate_refer = refer[r]
        bugfind = findBugByCluster(sequence)
        confirmed_find = find_confirmed(sequence, logcat_list)
        complete = 0
        high_risk = 0
        suspected = theCountOfRepeatEventBySlice(summaryByRepeatBySlice(makeUpFormatBySlice(sequence)))

        if bugfind:
            if bugfind[0] == 1.0:
                complete += 1
            else:
                high_risk += 1
        if suspected + high_risk + complete == 0 and not confirmed_find:
            highRisk = highRiskEventTranslate(translate_refer)
            if highRisk:
                suspected_test_actions_list.append(str(refer_repeat[0] + 1))
                suspected_test_actions_count += 1
                report_suspected_event += '  ' + str(num + 1) + '.Sequence ' + str(
                    refer_repeat[0] + 1) + ' of events: ' + repeat + '\n'

                report_suspected_event += '    i.Start time：' + time.strftime("%Y/%m/%d %H:%M:%S",
                                                                              time.localtime(sequence[0][
                                                                                                 'SyscTime'] / 1000)) + '\n'
                report_suspected_event += '    ii.End Time： ' + time.strftime("%Y/%m/%d %H:%M:%S",
                                                                              time.localtime(sequence[-1][
                                                                                                 'SyscTime'] / 1000)) + '\n'
                report_suspected_event += '    iii.Category：Suspected high risk test actions.\n'
                report_suspected_event += '    iv.Detailed description：\n'
                n = 0
                pre_high_risk = translate_refer[0:highRisk[1]]
                in_high_risk = translate_refer[highRisk[1]:highRisk[1] + highRisk[2]]
                after_high_risk = translate_refer[highRisk[1] + highRisk[2]:]
                fact_length_pre = sum([len(x) for x in pre_high_risk])
                fact_length_in = sum([len(x) for x in in_high_risk])
                fact_length_after = sum([len(x) for x in after_high_risk])
                sequence_pre = sequence[0:fact_length_pre]
                sequence_after = sequence[fact_length_pre + fact_length_in:]
                pre_report = ''
                center_report = ''
                after_report = ''
                if len(pre_high_risk) > 0:
                    pre_report = highSummary(sequence_pre)
                if len(after_high_risk) > 0:
                    after_report = highSummary(sequence_after)
                translate_refer_center = copy.deepcopy(in_high_risk)
                n += sum([len(x) for x in pre_high_risk]) - 1
                for tr in range(len(translate_refer_center)):
                    refer_length = len(translate_refer_center[tr])
                    for i in range(refer_length):
                        translate_refer_center[tr][i] = sequence[n]
                        n += 1
                for tr in range(len(translate_refer_center)):
                    refer_length = len(translate_refer_center[tr])
                    if refer_length == 1:
                        e = translate_refer_center[tr][0]
                        # isFullpre = -1
                        timeArray = time.localtime(e['SyscTime'] / 1000)
                        formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                        try:
                            outBounds = "In " + e['OutBounds'] + '.'
                        except KeyError:
                            outBounds = ''
                        if makeEventFormat(e) == '02':
                            center_report += '    ' + formatTime + ' ' + 'The user enter the main application.\n'
                            continue
                        className = e['Action']['ClassName']
                        Text = e['Action']['Text']
                        Text = Text.replace('[', '')
                        Text = Text.replace(']', '')

                        if len(Text) > 1:
                            Text = "The text is " + Text + '.'
                        else:
                            Text = ''

                        center_report += '    ' + formatTime + ' ' + process_OutBounds(outBounds) + ', ' + \
                                         android_event_type[e[
                                             'EventType']] + "Related class name is " + className + '.' + Text + '\n'
                    elif refer_length < 4:
                        timeArray = time.localtime(translate_refer_center[tr][0]['SyscTime'] / 1000)
                        start_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                        timeArray = time.localtime(translate_refer_center[tr][-1]['SyscTime'] / 1000)
                        end_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                        className = translate_refer_center[tr][0]['Action']['ClassName']
                        center_report += '    ' + start_formatTime + ' - ' + end_formatTime + ' ' + str(
                            len(translate_refer_center[tr])) + '  times of' + android_event_type[
                                             translate_refer_center[tr][0][
                                                 'EventType']] + " Related class name is " + className + '.\n'
                    elif refer_length >= 4:
                        timeArray = time.localtime(translate_refer_center[tr][0]['SyscTime'] / 1000)
                        start_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                        timeArray = time.localtime(translate_refer_center[tr][-1]['SyscTime'] / 1000)
                        end_formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                        className = translate_refer_center[tr][0]['Action']['ClassName']
                        center_report += 'Suspect bug!        ' + start_formatTime + ' - ' + end_formatTime + ' ' + str(
                            len(translate_refer_center[tr])) + ' times of' + android_event_type[
                                             translate_refer_center[tr][0][
                                                 'EventType']] + "Related class name is " + className + '.\n'
                report_suspected_event += pre_report
                report_suspected_event += '    ---------Suspected test actions start\n'
                report_suspected_event += center_report
                report_suspected_event += '    ---------Suspected test actions end\n'
                report_suspected_event += after_report + '\n'
                num += 1
    normal_count = 0
    for r in range(len(refer)):
        sequence = slice_event[r]
        refer_repeat = refer_repeat_sequence[r]
        repeat = ''
        if len(refer_repeat) > 1:
            for p in refer_repeat[1:]:
                repeat += '( Sequence ' + str(p + 1)
            repeat += ' contains the same test actions.)'
        translate_refer = refer[r]
        bugfind = findBugByCluster(sequence)
        confirmed_find = find_confirmed(sequence, logcat_list)
        complete = 0
        high_risk = 0
        suspected = theCountOfRepeatEventBySlice(summaryByRepeatBySlice(makeUpFormatBySlice(sequence)))

        if bugfind:
            if bugfind[0] == 1.0:
                complete += 1
            else:
                high_risk += 1
        if suspected + high_risk + complete == 0 and not highRiskEventTranslate(translate_refer) and not confirmed_find:
            normal_list.append(str(refer_repeat[0] + 1))
            report_pre = '  ' + str(num + 1) + '.Sequence ' + str(
                refer_repeat[0] + 1) + ' of events: ' + repeat + '\n'
            report = highSummary(sequence)
            report_normal += report_pre + report + '\n'
            num += 1
            normal_count += 1
    data = {
        'test_person': person_name,
        'test_app': software_name,
        'test_time': test_time,
        'event_count': event_count,
        'sequence_count': sequence_count,
        'unique_sequence_count': sequence_norepeat_count,
        'confirmed_bug_count': complete_whole,
        'high_risk_count': high_risk_whole,
        'suspected_bug': suspected_whole,
        'suspected_test_actions': suspected_test_actions_count,
        'normal_count': normal_count,
        'confirmed_bug_list': complete_whole_list,
        'high_risk_list': high_risk_whole_list,
        'suspected_bug_list': suspected_whole_list,
        'suspected_test_actions_list': suspected_test_actions_list,
        'normal_count_list': normal_list,
        'confirmed_report': report_confirmed,
        'high_risk_report': report_high_risk,
        'suspected_bug_report': report_suspected_repeat,
        'suspected_actions_report': report_suspected_event,
        'normal_report': report_normal
    }
    return data
    # print(report_overall)
    # print(report_confirmed)
    # print(report_high_risk)
    # print(report_suspected_repeat)
    # print(report_suspected_event)
    # print(report_normal)


def find_confirmed(sequence, logcatlist):
    start_time = sequence[0]['SyscTime']
    end_time = sequence[-1]['SyscTime']
    for logcat in logcatlist:
        if logcat['priority'] == 'E' and logcat['SyscTime'] > start_time and logcat['SyscTime'] < end_time + 1000:
            return 1

    return 0


def translate(file_name):
    with open('Preprocessing/output/' + file_name + '/event.json') as f:
        event_list = json.load(f)
    with open('Preprocessing/output/' + file_name + '/logcat.json') as f:
        logcat_list = json.load(f)
    slice_event = sliceEvent(event_list)
    if len(slice_event) > 0:
        return goTranslate(file_name, event_list, slice_event, logcat_list)

    # highRiskEventTranslate(slice_event)

# others = ''
# ContentDescription = re.findall('ContentDescription:(.+?);', e['Action'])[0]  #: null;
# if ContentDescription != ' null':
#     others += 'ContentDescription is' + ContentDescription + '.'
# ItemCount = re.findall('ItemCount:(.+?);', e['Action'])[0]  #: -1;
# if ItemCount != ' -1':
#     others += 'ItemCount is' + ItemCount + '.'
# CurrentItemIndex = re.findall('CurrentItemIndex:(.+?);', e['Action'])[0]  #: -1;
# if CurrentItemIndex != ' -1':
#     others += 'CurrentItemIndex is' + CurrentItemIndex + '.'
# IsEnabled = re.findall('IsEnabled:(.+?);', e['Action'])[0]  #: true;
# if IsEnabled != ' true':
#     others += 'IsEnabled is' + IsEnabled + '.'
# IsPassword = re.findall('IsPassword:(.+?);', e['Action'])[0]  #: false;
# if IsPassword != ' false':
#     others += 'IsPassword is' + IsPassword + '.'
# IsChecked = re.findall('IsChecked:(.+?);', e['Action'])[0]  #: false;
# if IsChecked != ' false':
#     others += 'IsChecked is' + IsChecked + '.'
# IsFullScreen = re.findall('IsFullScreen:(.+?);', e['Action'])[0]  #: true;
# if isFullpre == -1:
#     isFullpre = IsFullScreen
# if IsFullScreen != isFullpre:
#     others += "FullScreen changes and now FullScreen is" + IsFullScreen
# isFullpre = IsFullScreen
#
# Scrollable = re.findall('Scrollable:(.+?);', e['Action'])[0]  #: false;
# if Scrollable != ' false':
#     others += 'Scrollable is' + Scrollable + '.'
# BeforeText = re.findall('BeforeText:(.+?);', e['Action'])[0]  #: null;
# if BeforeText != ' null':
#     others += 'BeforeText is' + BeforeText + '.'
# FromIndex = re.findall('FromIndex:(.+?);', e['Action'])[0]  #: -1;
# if FromIndex != ' -1':
#     others += 'FromIndex is' + FromIndex + '.'
# ToIndex = re.findall('ToIndex:(.+?);', e['Action'])[0]  #: -1;
# if ToIndex != ' -1':
#     others += 'ToIndex is' + ToIndex + '.'
# ScrollX = re.findall('ScrollX:(.+?);', e['Action'])[0]  #: -1;
# if ScrollX != ' -1':
#     others += 'ScrollX is' + ScrollX + '.'
# ScrollY = re.findall('ScrollY:(.+?);', e['Action'])[0]  #: -1;
# if ScrollY != ' -1':
#     others += 'ScrollY is' + ScrollY + '.'
# MaxScrollX = re.findall('MaxScrollX:(.+?);', e['Action'])[0]  #: -1;
# if MaxScrollX != ' -1':
#     others += 'MaxScrollX is' + MaxScrollX + '.'
# MaxScrollY = re.findall('MaxScrollY:(.+?);', e['Action'])[0]  #: -1;
# if MaxScrollY != ' -1':
#     others += 'MaxScrollY is' + MaxScrollY + '.'
# AddedCount = re.findall('AddedCount:(.+?);', e['Action'])[0]  #: -1;
# if AddedCount != ' -1':
#     others += 'AddedCount is' + AddedCount + '.'
# RemovedCount = re.findall('RemovedCount:(.+?);', e['Action'])[0]  #: -1;
# if RemovedCount != ' -1':
#     others += 'RemovedCount is' + RemovedCount + '.'
# ParcelableData = re.findall('ParcelableData:(.+)\]', e['Action'])[0]  #: null
# if ParcelableData != ' null ':
#     others += 'ParcelableData is' + ParcelableData + '.'
