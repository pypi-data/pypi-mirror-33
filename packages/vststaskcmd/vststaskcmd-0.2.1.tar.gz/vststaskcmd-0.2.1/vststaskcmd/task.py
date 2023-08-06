import uuid
def setvariable(name, value, secret=False, silent=False):
    secretstring = ''
    logstring = ''
    if secret:
        secretstring = 'issecret=true;'
        logstring = ' as a secret'
    else:
        logstring = " to '{}'".format(value)
    print("##vso[task.setvariable variable={};{}]{}".format(name, secretstring, value))
    if not silent:
        print("VSTS variable '{}' is set{}".format(name,logstring))

def complete(result="Succeeded", comment=None):
    print("##vso[task.complete result={};]{}".format(result,comment))
    print("Current task result set to {}".format(result))

def setpartialsuccess(comment=None):
    complete("SucceededWithIssues", comment)

def setfailed(comment=None):
    complete("Failed", comment)

def logissue(message, issue_type="warning", source_path=None, line_number=None, column_number=None, code=None):
    s = "##vso[task.logissue "
    if (issue_type != "warning") and (issue_type != "error"):
        issue_type = "error"
    s = s + "type=" + issue_type + ';'
    if source_path:
        s = s + "sourcepath=" + str(source_path) + ';'
    if line_number:
        s = s + "linenumber=" + str(line_number) + ';'
    if column_number:
        s = s + "columnnumber=" + str(column_number) + ';'
    if code:
        s = s + "code=" + str(code) + ';'
    s = s + ']' + str(message)
    print(s)

def setprogress(value, message=None):
    if message:
        s = "##vso[task.setprogress value={};]{}".format(str(value), str(message))
    else:
        s = "##vso[task.setprogress value={};]".format(str(value))
    print(s)

def logdetail(guid, parent_id=None, record_type=None, name=None, order=None, start_time=None, finish_time=None, progress=None, state="Unknown", result=None, message=None):
    s = "##vso[task.logdetail id="
    s = s + str(guid) + ';'
    if parent_id:
        s = s + "parentid=" + str(parent_id) + ';'
    if record_type:
        s = s + "type=" + str(record_type) + ';'
    if name:
        s = s + "name=" + str(name) + ';'
    if order:
        s = s + "order=" + str(order) + ';'
    if start_time:
        s = s + "starttime=" + str(start_time) + ';'
    if finish_time:
        s = s + "finishtime=" + str(finish_time) + ';'
    if progress:
        s = s + "progress=" + str(progress) + ';'
    if state:
        s = s + "state=" + str(state) + ';'
    if result:
        s = s + "result=" + str(result) + ';'
    s = s + ']'
    if message:
        s = s + message
    print(s)

def new_timeline_record(name, record_type, order, parent=None, start_time=None, finish_time=None, progress=None, state=None, result=None, message=None, silent=False):
    guid = str(uuid.uuid4)
    logdetail(guid, parent_id=parent, record_type=record_type, name=name, order=order, start_time=start_time, finish_time=finish_time, progress=progress,
        state=state, result=result, message=message)
    if not silent:
        print("Created a new timeline record with GUID: {}".format(guid))
    return guid

def update_timeline_record(guid, parent=None, start_time=None, finish_time=None, progress=None, state=None, result=None, message=None, silent=False):
    logdetail(guid, parent_id=parent, start_time=start_time, finish_time=finish_time, progress=progress, state=state, result=result, message=message)
    if not silent:
        print("Update existing timeline record: {}". format(guid))
    return guid

