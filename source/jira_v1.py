from jira import JIRA
import csv
import codecs
import datetime

options = {'server': '*'}
jira = JIRA(options, basic_auth=("*", "*"))


project = '*'
#projects = jira.projects()
#for i in projects:
#    print(i)            # prints all of the projects
#print("") 

#for project in projects:
all_issues = jira.search_issues('project="{}"'.format(project))   

issuelist = []       #contains summary, 
workerlist = []
rearranger = []
fullissuelist = []
for i in range(len(all_issues)):                                       
    issue = jira.issue(all_issues[i])
    issuelist.append([issue.fields.summary])
    fullissuelist.append([issue.fields.summary])
    worklogs = jira.worklogs(issue.key)
    for worklog in worklogs:
        author = worklog.author
        time = worklog.timeSpentSeconds
        issuelist[i].append(str(author))
        issuelist[i].append(str(time))
        
        if str(author) not in workerlist:
            workerlist.append(str(author))
            

for i in range(len(workerlist)):
    rearranger.append([workerlist[i]])


for i in range(len(all_issues)):
    for j in range(len(rearranger)):
        rearranger[j].append(0)
    issue = jira.issue(all_issues[i])                           
    issuelist.append([issue.fields.summary])
    worklogs = jira.worklogs(issue.key)
    for worklog in worklogs:
        author = worklog.author
        time = worklog.timeSpentSeconds
        for counter in range(len(rearranger)):
            if str(author) == str(rearranger[counter][0]):
                rearranger[counter][i+1] += time
                
print(rearranger)
workername = ['']
for i in range(len(rearranger)):
    workername.append(rearranger[i][0])

print(fullissuelist)
for i in range(len(fullissuelist)):
    for j in range(len(rearranger)):
        fullissuelist[i].append(rearranger[j][i+1])



totalhourslist = ['']
for i in range(len(rearranger)):
    totalhours = 0
    for j in range(len(rearranger[i])-1):
        totalhours += rearranger[i][j+1]
    totalhourslist.append(totalhours)

print(totalhourslist)

currentlist = []
for i in range(len(fullissuelist)):
    zeros = 0
    for j in range(len(fullissuelist[i])):
        if fullissuelist[i][j] == 0:
            zeros += 1

    if zeros < (len(fullissuelist[i])-1):
        currentlist.append(fullissuelist[i])

print(currentlist)
for i in range(len(currentlist)):
    for j in range(len(currentlist[i])):
        if currentlist[i][j] == 0:
            currentlist[i][j] = "" 
       
print(currentlist)
for i in range(len(all_issues)):                                       
    issue = jira.issue(all_issues[i])
    issuelist.append([issue.fields.summary])
    worklogs = jira.worklogs(issue.key)
    for worklog in worklogs:
        for i in range(len(currentlist)):
            if len(currentlist[i]) < 4:
                if currentlist[i][0] == issue.fields.summary:
                    currentlist[i].append(issue.fields.created)
                    if issue.fields.resolutiondate:
                        resdate = "{}".format(issue.fields.resolutiondate)
                        resdateobj = datetime.datetime.strptime(resdate, '%Y-%m-%d T%H:%M:%S.%f+0000')
                        currentlist[i].append(resdateobj)
                        print(currentlist[i])
                    else:
                        currentlist[i].append("none")

print(currentlist)
workername.append("CreatDate")
workername.append("ResDate")
with open ('test2.csv', mode='w', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow([project])
    writer.writerow(workername)
    for i in range(len(currentlist)):
        writer.writerow((currentlist[i]))
    writer.writerow(totalhourslist)
