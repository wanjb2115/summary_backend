from flask import Flask
from flask_restful import Resource, Api
import os
import json
import re
import Levenshtein
import time

with open('errorHub.json') as f:
    errorhub = json.load(f)

with open('errorIntro.json') as f:
    errorIntro = json.load(f)


def bugTest(eventsequence):
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
                        error_list.append([sim, key, l[0], l[1]])
    error_list = sorted(error_list, key=lambda x: x[0], reverse=True)
    if len(error_list) >= 1:
        return error_list[0]
    else:
        return None


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


android_event_type_value = {
    'TYPE_WINDOW_STATE_CHANGED': '0',
    # Represents the event of a change to a visually distinct section of the user interface. These events should only be dispatched from Views that have accessibility pane titles, and replaces TYPE_WINDOW_CONTENT_CHANGED for those sources. Details about the change are available from getContentChangeTypes().

    'TYPE_WINDOW_CONTENT_CHANGED': '1',
    # Represents the event of changing the content of a window and more specifically the sub-tree rooted at the event's source.

    'TYPE_VIEW_FOCUSED': '2',  # Represents the event of setting input focus of a View.

    'TYPE_VIEW_SCROLLED': '3',
    # Represents the event of scrolling a view. This event type is generally not sent directly.

    'TYPE_VIEW_CLICKED': '4',  # Represents the event of clicking on a View like Button, CompoundButton, etc.

    'TYPE_VIEW_TEXT_SELECTION_CHANGED': '5',  # Represents the event of changing the selection in an EditText.

    'TYPE_VIEW_ACCESSIBILITY_FOCUSED': '6',  # Represents the event of gaining accessibility focus.

    'TYPE_VIEW_TEXT_CHANGED': '7',  # Represents the event of changing the text of an EditText.

    'TYPE_VIEW_SELECTED': '8',
    # Represents the event of selecting an item usually in the context of an AdapterView.

    'TYPE_NOTIFICATION_STATE_CHANGED': '9',  # Represents the event showing a Notification.

    'TYPE_ANNOUNCEMENT': 'a',  # Represents the event of an application making an announcement.

    'TYPE_VIEW_ACCESSIBILITY_FOCUS_CLEARED': 'b',  # Represents the event of clearing accessibility focus.

    'TYPE_VIEW_LONG_CLICKED': 'c',
    # Represents the event of long clicking on a View like Button, CompoundButton, etc.

    'TYPE_VIEW_HOVER_ENTER': 'd',  # Represents the event of a hover enter over a View.

    'TYPE_VIEW_HOVER_EXIT': 'e',  # Represents the event of a hover exit over a View.

}
android_event_class_type = {
    'android.widget.ImageButton': '1',
    'com.example.myfristandroid.MainActivity': '2',
    'android.widget.RelativeLayout': '3',
    'com.example.myfristandroid.graphWebShow': '4',
    'android.widget.FrameLayout': '5',
    'com.example.myfristandroid.CustomProgressDialog': '6',
    'com.example.myfristandroid.HuzAlertDialog': '7',
    'android.widget.Button': '8',
    'android.widget.ListView': '9',
    'android.widget.TextView': 'a',
    'android.widget.LinearLayout': 'b',
    'android.support.v4.view.ViewPager': 'c',
    'android.widget.EditText': 'd',
    'android.widget.CheckedTextView': 'e',
    'android.widget.ScrollView': 'f',
    'com.android.org.chromium.content.browser.ContentViewCore': 'g',
    'android.view.View': 'h',
    'android.widget.GridView': 'i',
    'android.webkit.WebView': 'j',
    'com.example.myfristandroid.SplashActivity': 'k',
    'org.chromium.content.browser.ContentViewCore': 'l',
    'android.widget.Image': 'm'
}

app = Flask(__name__)
api = Api(app)


class GetFileNames(Resource):
    def get(self, file_dir):
        result = os.listdir('data/' + file_dir)
        return {'fileNames': result}


class GetFileContent(Resource):
    def get(self, file_dir):
        file_dir = 'data/' + file_dir
        with open(file_dir) as f:
            return {'fileContent': f.read()}


class SliceEvent(Resource):
    def get(self, file_dir):
        event_sequence_by_time = []

        with open('data/data_process/output/' + file_dir + '/event.json') as f:
            event_list = json.load(f)
        event_little_sequence_by_time = []
        for i in range(len(event_list) - 1):
            tim = event_list[i + 1]['SyscTime'] - event_list[i]['SyscTime']
            if tim < 10000:
                event_little_sequence_by_time.append(event_list[i])
            else:
                event_little_sequence_by_time.append(event_list[i])
                event_sequence_by_time.append(event_little_sequence_by_time)
                event_little_sequence_by_time = []
                continue
        event_little_sequence_by_time.append(event_list[len(event_list) - 1])
        event_sequence_by_time.append(event_little_sequence_by_time)
        event_sequence_all = []

        for event_sequence_by_time_list in event_sequence_by_time:
            if len(event_sequence_by_time_list) >= 3:
                event_sequence = []
                for e in event_sequence_by_time_list:
                    try:
                        action_class = re.findall("ClassName: (.+?);", e['Action'])[0]
                        event_sequence.append(
                            [android_event_type_value[e['EventType']] + android_event_class_type[action_class], e])
                    except TypeError:
                        print(e)
                    except KeyError:
                        event_sequence.append([android_event_type_value[e['EventType']] + '0', e])
                event_sequence_all.append(event_sequence)

        parsedDat = event_sequence_all

        littleList = []
        for middleDat in [x for x in parsedDat]:
            littleList_item = []
            for i in range(0, len(middleDat)):
                if middleDat[i][0] == '02':
                    littleList.append(littleList_item)
                    littleList_item = []
                    littleList_item.append(middleDat[i][1])
                else:
                    littleList_item.append(middleDat[i][1])

        slice_event = [x for x in littleList if len(x) >= 2 and len(x) <= 38]
        return {'data': slice_event}


class Translate(Resource):
    def get(self, file_dir):
        with open('data/data_process/output/' + file_dir + '/event.json') as f:
            event_list = json.load(f)
        slice_event = SliceEvent().get(file_dir)['data']

        complete = 0
        high_risk = 0
        suspected = 0
        for sequence in slice_event:
            bugfind = bugTest(sequence)
            if bugfind:
                if bugfind[0] == 1.0:
                    complete += 1
                    errorText = errorIntro[bugfind[1]]
                    errorSimEvent = bugfind[2]
                    errorEventSim = bugfind[3]
                else:
                    high_risk += 1
                    errorText = errorIntro[bugfind[1]]
                    errorSimEvent = bugfind[2]
                    errorEventSim = bugfind[3]
        report = '''
                    Test person：person_name
                    Test software：software_name
                    Test statistics：
                        This test data is captured by Kikbug tool. The test duration is total test_time seconds and  event_count event logs are captured. 
                        There are sequence_count analyzable event sequences are segmented by S-CAT frame. 
                        There are complete_count complete bugs,high_risk_count high risk bugs and suspected_count suspected bugs. 
                        The following is detailed summary of the segmented event sequence. 
                    Test report：
                '''
        person_name = re.findall('\d+_\d+', file_dir)[0]
        software_name = event_list[0]['PackageName']
        test_time = str((event_list[-1]['SyscTime'] - event_list[0]['SyscTime']) / 1000)
        event_count = str(len(event_list))
        sequence_count = str(len(slice_event))

        report = report.replace('person_name', person_name)
        report = report.replace('software_name', software_name)
        report = report.replace('test_time', test_time)
        report = report.replace('event_count', event_count)
        report = report.replace('sequence_count', sequence_count)
        report = report.replace('complete_count', str(complete))
        report = report.replace('high_risk_count', str(high_risk))
        report = report.replace('suspected_count', str(suspected))

        with open('translate.json') as f:
            translate = json.load(f)

        android_event_type = translate['android_event_type']
        event_class_type = translate['event_class_type']

        num = 1
        for sequence in slice_event:
            bugfind = bugTest(sequence)
            complete = 0
            high_risk = 0
            suspected = 0
            if bugfind:
                if bugfind[0] == 1.0:
                    complete += 1
                    errorText = errorIntro[bugfind[1]]
                    errorSimEvent = bugfind[2]
                    errorEventSim = bugfind[3]
                else:
                    high_risk += 1
                    errorText = errorIntro[bugfind[1]]
                    errorSimEvent = bugfind[2]
                    errorEventSim = bugfind[3]
            report += '            ' + str(num) + '.Sequence ' + str(num) + ' of events:' + '\n'
            report += '                i.Start time：' + time.strftime("%Y/%m/%d %H:%M:%S",
                                                                      time.localtime(
                                                                          sequence[0]['SyscTime'] / 1000)) + '\n'
            report += '                ii.End Time： ' + time.strftime("%Y/%m/%d %H:%M:%S",
                                                                      time.localtime(
                                                                          sequence[-1]['SyscTime'] / 1000)) + '\n'
            report += '                iii.statistics：Complete bug ' + str(complete) + ', high-risk bug ' + str(
                high_risk) + ', suspected bug ' + str(suspected) + '\n'
            if complete != 0 or high_risk != 0:
                report += '                    The bug message might be:', errorText, '.The accuracy is ', float(
                    bugfind[0]) * float(errorEventSim) + '\n'

            report += '                iv.Detailed description：' + '\n'
            for e in sequence:
                isFullpre = -1
                timeArray = time.localtime(e['SyscTime'] / 1000)
                formatTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
                try:
                    outBounds = "In " + e['OutBounds'] + '.'
                except KeyError:
                    outBounds = ''
                className = re.findall('ClassName:(.+?);', e['Action'])[0]
                Text = re.findall('Text:(.+?);', e['Action'])[0]
                Text = Text.replace('[', '')
                Text = Text.replace(']', '')

                if len(Text) > 1:
                    Text = "The text is" + Text + '.'
                else:
                    Text = ''
                others = ''
                ContentDescription = re.findall('ContentDescription:(.+?);', e['Action'])[0]  #: null;
                if ContentDescription != ' null':
                    others += 'ContentDescription is' + ContentDescription + '.'
                ItemCount = re.findall('ItemCount:(.+?);', e['Action'])[0]  #: -1;
                if ItemCount != ' -1':
                    others += 'ItemCount is' + ItemCount + '.'
                CurrentItemIndex = re.findall('CurrentItemIndex:(.+?);', e['Action'])[0]  #: -1;
                if CurrentItemIndex != ' -1':
                    others += 'CurrentItemIndex is' + CurrentItemIndex + '.'
                IsEnabled = re.findall('IsEnabled:(.+?);', e['Action'])[0]  #: true;
                if IsEnabled != ' true':
                    others += 'IsEnabled is' + IsEnabled + '.'
                IsPassword = re.findall('IsPassword:(.+?);', e['Action'])[0]  #: false;
                if IsPassword != ' false':
                    others += 'IsPassword is' + IsPassword + '.'
                IsChecked = re.findall('IsChecked:(.+?);', e['Action'])[0]  #: false;
                if IsChecked != ' false':
                    others += 'IsChecked is' + IsChecked + '.'
                IsFullScreen = re.findall('IsFullScreen:(.+?);', e['Action'])[0]  #: true;
                if isFullpre == -1:
                    isFullpre = IsFullScreen
                if IsFullScreen != isFullpre:
                    others += "FullScreen changes and now FullScreen is" + IsFullScreen
                isFullpre = IsFullScreen

                Scrollable = re.findall('Scrollable:(.+?);', e['Action'])[0]  #: false;
                if Scrollable != ' false':
                    others += 'Scrollable is' + Scrollable + '.'
                BeforeText = re.findall('BeforeText:(.+?);', e['Action'])[0]  #: null;
                if BeforeText != ' null':
                    others += 'BeforeText is' + BeforeText + '.'
                FromIndex = re.findall('FromIndex:(.+?);', e['Action'])[0]  #: -1;
                if FromIndex != ' -1':
                    others += 'FromIndex is' + FromIndex + '.'
                ToIndex = re.findall('ToIndex:(.+?);', e['Action'])[0]  #: -1;
                if ToIndex != ' -1':
                    others += 'ToIndex is' + ToIndex + '.'
                ScrollX = re.findall('ScrollX:(.+?);', e['Action'])[0]  #: -1;
                if ScrollX != ' -1':
                    others += 'ScrollX is' + ScrollX + '.'
                ScrollY = re.findall('ScrollY:(.+?);', e['Action'])[0]  #: -1;
                if ScrollY != ' -1':
                    others += 'ScrollY is' + ScrollY + '.'
                MaxScrollX = re.findall('MaxScrollX:(.+?);', e['Action'])[0]  #: -1;
                if MaxScrollX != ' -1':
                    others += 'MaxScrollX is' + MaxScrollX + '.'
                MaxScrollY = re.findall('MaxScrollY:(.+?);', e['Action'])[0]  #: -1;
                if MaxScrollY != ' -1':
                    others += 'MaxScrollY is' + MaxScrollY + '.'
                AddedCount = re.findall('AddedCount:(.+?);', e['Action'])[0]  #: -1;
                if AddedCount != ' -1':
                    others += 'AddedCount is' + AddedCount + '.'
                RemovedCount = re.findall('RemovedCount:(.+?);', e['Action'])[0]  #: -1;
                if RemovedCount != ' -1':
                    others += 'RemovedCount is' + RemovedCount + '.'
                ParcelableData = re.findall('ParcelableData:(.+)\]', e['Action'])[0]  #: null
                if ParcelableData != ' null ':
                    others += 'ParcelableData is' + ParcelableData + '.'
                report += '                    ' + formatTime + process_OutBounds(outBounds) + android_event_type[
                    e['EventType']] + "Related action class name is" + className + '.' + Text + others + '\n'
            report += '                    --------------------------------------------' + '\n'
            num += 1
        return {"data": report}


api.add_resource(GetFileNames, '/GetFileNames/<path:file_dir>')
api.add_resource(GetFileContent, '/GetFileContent/<path:file_dir>')
api.add_resource(SliceEvent, '/SliceEvent/<path:file_dir>')
api.add_resource(Translate, '/Translate/<path:file_dir>')

if __name__ == '__main__':
    app.run(debug=True)
