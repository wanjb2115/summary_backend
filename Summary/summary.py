import json
import fpgrowth
import re

with open('error_full_target.json') as f:
    error_hub = json.load(f)

error = []
error_full = {}
error_sim = {}
error_not = {}
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
    'android.widget.Image': 'm',
    'android.widget.Toast$TN': 'n'
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

    'TYPE_ANNOUNCEMENT': '10',  # Represents the event of an application making an announcement.

    'TYPE_VIEW_ACCESSIBILITY_FOCUS_CLEARED': '11',  # Represents the event of clearing accessibility focus.

    'TYPE_VIEW_LONG_CLICKED': '12',  # Represents the event of long clicking on a View like Button, CompoundButton, etc.

    'TYPE_VIEW_HOVER_ENTER': '13',  # Represents the event of a hover enter over a View.

    'TYPE_VIEW_HOVER_EXIT': '14',  # Represents the event of a hover exit over a View.

}

key = ['IMGSRV  ', 'ViewRootImpl', 'chromium', 'Web Console', 'dalvikvm', 'ion     ', 'webcoreglue', 'Diag_Lib',
       'external/chromium/net/host_resolver_helper/dyn_lib_loader.cc', '        ', 'ZoomManager.java']
txt_all = []
error_not_enough = []
for k in key:
    if len(error_hub[k]) > 5:
        slice_event = error_hub[k]

        event_sequence_all = []
        for s in slice_event:
            event_sequence = []
            for e in s:
                action_class = e['Action']['ClassName']
                event_sequence.append(android_event_type_value[e['EventType']] + android_event_class_type[action_class])
                txt = e['EventType'], action_class, android_event_type_value[e['EventType']], android_event_class_type[
                    action_class]
                if txt not in txt_all:
                    txt_all.append(txt)
            event_sequence_all.append(event_sequence)

        parsedDat = event_sequence_all
        print(k, len(error_hub[k]))
        error_full[k] = []

        n = int(len(event_sequence_all) * 0.8)

        initSet = fpgrowth.createInitSet(parsedDat)
        myFPtree, myHeaderTab = fpgrowth.createFPtree(initSet, n)
        freqItems = []
        for h in myHeaderTab:
            print(h, myHeaderTab[h][0])
            error_full[k].append(h)
        fpgrowth.mineFPtree(myFPtree, myHeaderTab, n, set([]), freqItems)
        for x in freqItems:
            print (x)

        # compute support values of freqItems
        suppData = fpgrowth.calSuppData(myHeaderTab, freqItems, len(parsedDat))
        suppData[frozenset([])] = 1.0
        # for x,v in suppData.items():
        #     print (x,v)

        freqItems = [frozenset(x) for x in freqItems]
        fpgrowth.generateRules(freqItems, suppData)
    else:
        error_not_enough.append(k)

with open('error_all_target.json') as f:
    error_hub = json.load(f)

error_less = []
for k in error_not_enough:
    if len(error_hub[k]) > 5:
        slice_event = error_hub[k]

        event_sequence_all = []
        for s in slice_event:
            event_sequence = []
            for e in s:
                action_class = e['Action']['ClassName']
                event_sequence.append(
                    android_event_type_value[e['EventType']] + android_event_class_type[action_class])
                txt = e['EventType'], action_class, android_event_type_value[e['EventType']], android_event_class_type[
                    action_class]
                if txt not in txt_all:
                    txt_all.append(txt)
            event_sequence_all.append(event_sequence)

        parsedDat = event_sequence_all
        print(k, len(error_hub[k]))
        error_sim[k] = []

        n = int(len(event_sequence_all) * 0.8)

        initSet = fpgrowth.createInitSet(parsedDat)
        myFPtree, myHeaderTab = fpgrowth.createFPtree(initSet, n)
        freqItems = []
        for h in myHeaderTab:
            print(h, myHeaderTab[h][0])
            error_sim[k].append(h)
    else:
        error_less.append(k)
        error_not[k] = []

# for l in error_less:
#     print(l)
#
# for t in txt_all:
#     print(t)

error_summary = [error_full, error_sim, error_not]
with open("error_summary_hub.json", 'w') as f:
    json.dump(error_summary, f, indent=4)
