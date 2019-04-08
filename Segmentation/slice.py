import json
import re

android_event_type = {
    'TYPE_WINDOW_STATE_CHANGED': [],
    # Represents the event of a change to a visually distinct section of the user interface. These events should only be dispatched from Views that have accessibility pane titles, and replaces TYPE_WINDOW_CONTENT_CHANGED for those sources. Details about the change are available from getContentChangeTypes().

    'TYPE_WINDOW_CONTENT_CHANGED': [],
    # Represents the event of changing the content of a window and more specifically the sub-tree rooted at the event's source.

    'TYPE_VIEW_FOCUSED': [],  # Represents the event of setting input focus of a View.

    'TYPE_VIEW_SCROLLED': [],
    # Represents the event of scrolling a view. This event type is generally not sent directly.

    'TYPE_VIEW_CLICKED': [],  # Represents the event of clicking on a View like Button, CompoundButton, etc.

    'TYPE_VIEW_TEXT_SELECTION_CHANGED': [],  # Represents the event of changing the selection in an EditText.

    'TYPE_VIEW_ACCESSIBILITY_FOCUSED': [],  # Represents the event of gaining accessibility focus.

    'TYPE_VIEW_TEXT_CHANGED': [],  # Represents the event of changing the text of an EditText.

    'TYPE_VIEW_SELECTED': [],  # Represents the event of selecting an item usually in the context of an AdapterView.

    'TYPE_NOTIFICATION_STATE_CHANGED': [],  # Represents the event showing a Notification.

    'TYPE_ANNOUNCEMENT': [],  # Represents the event of an application making an announcement.

    'TYPE_VIEW_ACCESSIBILITY_FOCUS_CLEARED': [],  # Represents the event of clearing accessibility focus.

    'TYPE_VIEW_LONG_CLICKED': [],  # Represents the event of long clicking on a View like Button, CompoundButton, etc.

    'TYPE_VIEW_HOVER_ENTER': [],  # Represents the event of a hover enter over a View.

    'TYPE_VIEW_HOVER_EXIT': [],  # Represents the event of a hover exit over a View.
}
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

    'TYPE_VIEW_SELECTED': '8',  # Represents the event of selecting an item usually in the context of an AdapterView.

    'TYPE_NOTIFICATION_STATE_CHANGED': '9',  # Represents the event showing a Notification.

    'TYPE_ANNOUNCEMENT': 'a',  # Represents the event of an application making an announcement.

    'TYPE_VIEW_ACCESSIBILITY_FOCUS_CLEARED': 'b',  # Represents the event of clearing accessibility focus.

    'TYPE_VIEW_LONG_CLICKED': 'c',  # Represents the event of long clicking on a View like Button, CompoundButton, etc.

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


def sliceEvent(file_dir):
    event_sequence_by_time = []

    with open('Preprocessing/output/' + file_dir + '/event.json') as f:
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
                    action_class = e['Action']['ClassName']
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
                if len(littleList_item) != 0:
                    littleList.append(littleList_item)
                littleList_item = []
                littleList_item.append(middleDat[i][1])
            else:
                if len(littleList_item) != 0:
                    littleList_item.append(middleDat[i][1])

    slice_event = [x for x in littleList if len(x) >= 2 and len(x) <= 38]
    return {'data': slice_event}

