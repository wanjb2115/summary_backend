from flask import Flask
from flask_restful import Resource, Api
import os
import json
import re
import time

from

app = Flask(__name__)
api = Api(app)


class GetFileNames(Resource):
    def get(self, file_dir):
        result = os.listdir('1-Preprocessing/' + file_dir)
        return {'fileNames': result}


class GetFileContent(Resource):
    def get(self, file_dir):
        file_dir = '1-Preprocessing/' + file_dir
        with open(file_dir) as f:
            return {'fileContent': f.read()}


class SliceEvent(Resource):
    def get(self, file_dir):
        return


class Translate(Resource):
    def get(self, file_dir):
        with open('1-Preprocessing/output/' + file_dir + '/event.json') as f:
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
