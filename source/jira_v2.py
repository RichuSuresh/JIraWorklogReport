from jira import JIRA
import csv
import codecs
import datetime

options = {'server': '*'}
jira = JIRA(options, basic_auth=("*", "*"))



projects = jira.projects() # list containing all projects

# loop to print all of the projects
for i in projects:
    print(i)                   
print("")

# Clears the CSV file before writing reports to it
with open('test3.csv', mode='w') as file:
    pass


all_worker_names = [] # holds the names of all workers
csv_header = []  # header of the csv file
print('loading worker names...')
# Used to append all of workers that existed in any project into both the csv_header and all_worker_names
for project in projects:
        print(project)
        all_issues = jira.search_issues('project="{}"'.format(project))    #list which contains all issues in a project
        # obtains worker names from each issue in each project
        for i in range(len(all_issues)):
            issue = jira.issue(all_issues[i])
            worklogs = jira.worklogs(issue.key)   #list of all of the worklegs in an issue
            for worklog in worklogs:
                author = worklog.author   #gets the name of the worklog authors
                if str(author) not in all_worker_names: # avoiding repeated names from being added to the lists
                    all_worker_names.append(str(author))
                    csv_header.append(str(author))

print('worker names have been fully loaded')
print("")

projectcount = 0  # used to indicate the number of projects that have been loaded into the file, this is so the header only gets written once
print('writing reports to csv file...')

# loops through each project to get reports
for projectname in projects:
    print(projectname)
    all_issues = jira.search_issues('project="{}"'.format(projectname))    #list which contains all issues in a project

    issue_list = []       #contains the summary of the issues, the names of workloggers and the time they logged
    worker_name_list = []       #contains the names of the workers that have worked on the project
    WorkerAndTS = []       #will become a 2D list which contains the names of the workers and the times they've worked on each issue
    fullissuelist = []    #this list will contain the summaries of each issue as well as the total amount of hours worked on an issue by each person in the worker_name_list

    #this loop is used to bring down the issue names and the worklogs on each issue
    for i in range(len(all_issues)):
        issue = jira.issue(all_issues[i])
        issue_list.append([issue.fields.summary])  #issue.fields.summary represents the summary of the issue each issue will be put in a 2D list so I can apppend time values to it as well
        fullissuelist.append([issue.fields.summary])
        worklogs = jira.worklogs(issue.key)   #list of all of the worklegs in an issue
        for worklog in worklogs:
            author = worklog.author   #gets the name of the worklog authors
            time = worklog.timeSpentSeconds #gets the amount of time that has been logged by the authors
            issue_list[i].append(str(author))   #through each iteration, the issue_list will fill up with worklogs and issue names
            issue_list[i].append(str(time))
            
            #the issue_list at this point will contain names of all issue authors, this include repeated names of the same author. this if statement serves as a function
            #to remove duplicate names from the issue_list by appending them to a new list (worker_name_list)
            if str(author) not in worker_name_list:    
                worker_name_list.append(str(author))

     
    #this function baically splits each item in the worker_name_list, so each worker gets their own nested list, this will be used in order to tie the time spent to the worker who spent it
    for i in range(len(worker_name_list)):  
        WorkerAndTS.append([worker_name_list[i]])


    #Looping through all of the issues again in order to add time values to the rearrangedlist
    for i in range(len(all_issues)):
        for j in range(len(WorkerAndTS)): #adds the number 0 to each list in WorkerAndTS for each issue in a project. 
            WorkerAndTS[j].append(0)      #These 0s represent the amount of hours worked on each project by the worker, based on their worklog
        issue = jira.issue(all_issues[i])                           
        
        worklogs = jira.worklogs(issue.key)
        for worklog in worklogs:
            author = worklog.author
            time = worklog.timeSpentSeconds
            
            #this for loop compares the author that the main for loop is looking at against the the worker name in WorkerAndTS 
            for counter in range(len(WorkerAndTS)):   
                if str(author) == str(WorkerAndTS[counter][0]):  
                    WorkerAndTS[counter][i+1] += time   #if the author being looked at
                    
    # ties the issue to the time spent on the issue by each other
    for i in range(len(fullissuelist)):
        for j in range(len(WorkerAndTS)):
            fullissuelist[i].append(WorkerAndTS[j][i+1])

    # This list will only hold issues that have times logged on them, this for loop appends the issues which contain issues that don't have all zeros
    currentlist = []  
    for i in range(len(fullissuelist)):
        zeros = 0  # tally of the amount of zeros in an issue
        for j in range(len(fullissuelist[i])):
            if fullissuelist[i][j] == 0:
                zeros += 1  # adds 1 to the tally when a 0 is found

        # compared the amount of zeros to the number of items in the nested list which contains the issue
        if zeros < (len(fullissuelist[i])-1): # since the fullissuelist will only contain the issue summary right now, we only need to detect whether the amount of zeros is equivalent to the length of list without the summary
            currentlist.append(fullissuelist[i]) # if the amount of zeros is less than the length of the list without the summary, this means a worker has logged time on the issue, this means the issue will get appended to the currentlist

    # aesthetic purposes, replaces the 0s in each nested list in currentlist with blank spaces
    for i in range(len(currentlist)):
        for j in range(len(currentlist[i])):
            if currentlist[i][j] == 0:
                currentlist[i][j] = "" 
          
    # obtains the length of each nested list in currentlist, this will be used when appending time
    length_list = []
    for i in range(len(currentlist)):
        length_list.append(len(currentlist[i]))

    # appends the time created and time resolved into the currentlist        
    for i in range(len(all_issues)):                                       
        issue = jira.issue(all_issues[i])
        
        for i in range(len(currentlist)):
            if len(currentlist[i]) == length_list[i]: # this checks whether the length of the nested list is equal to the length of the list before the created time and resolve time were added
                                                      # this is used in case some of the issues have the same names but different creation dates and resolve dates
                
                if currentlist[i][0] == issue.fields.summary:# checks to see if the summary in the nested list is the same as the one being looked at by the main loop

                    # this section obtains the date the issue was created and puts it into a traditional day/month/year format
                    date = "{}".format(issue.fields.created)
                    date_obj = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f%z')
                    year = date_obj.strftime("%Y")
                    month = date_obj.strftime("%m")
                    day = date_obj.strftime("%d")
                    timestring = (day+"/"+month+"/"+year)
                    currentlist[i].insert(1, timestring)

                    # this section similar to the creation date formatting, it finds the date of when an issue was resolved
                    if issue.fields.resolutiondate:
                        date = "{}".format(issue.fields.resolutiondate)
                        date_obj = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f%z')
                        year = date_obj.strftime("%Y")
                        month = date_obj.strftime("%m")
                        day = date_obj.strftime("%d")
                        timestring = (day+"/"+month+"/"+year)
                        
                        currentlist[i].insert(2, timestring)

                    # as some issue have not been resolved, they won't have a resolved date, in which case their resolved date will be marked as 'none' in the csv file
                    else:
                        currentlist[i].insert(2, "none")


    # inserts the issue key into the nested list which contains the corresponding issue by matching it with the summary
    for i in range(len(all_issues)):
        issue = jira.issue(all_issues[i])
        summary = issue.fields.summary
        
        for j in range(len(currentlist)):
            if summary == currentlist[j][0]:
                currentlist[j].insert(0, issue.key)

    # inserts the project name into the nested lists           
    for i in range(len(currentlist)):
        currentlist[i].insert(0, projectname)

    # creates a new list which will be used to rearrange the 2D list so it can written to the csv file in the given format
# csv format is | Projectid | issueid | issue_desc | CreateDate | ResDate | all worker names with their own cell |
    # this for loop adds the project names, the creation date and the resolve date to the new_currentlist
    new_current = []
    for i in range(len(currentlist)):
        new_current.append([currentlist[i][0]])
        for j in range(4):
            new_current[i].append(currentlist[i][j+1])
   

    # this for loop appends the number 0 for the amount of workers in all_worker_names. This 0 represents the amount of time a worker has worked on the each project in the issues in new_currentlist
    for i in range(len(new_current)):
        for j in range(len(all_worker_names)):
            new_current[i].append(0)

    # this for loops connects the location of the worker in the worker name list with a 0 in the new_currentlist
    for i in range(len(all_issues)):                                       
        issue = jira.issue(all_issues[i])
        
        worklogs = jira.worklogs(issue.key)
        for worklog in worklogs:
            author = worklog.author
            time = worklog.timeSpentSeconds
            for j in range(len(all_worker_names)):
                
                if str(author) == all_worker_names[j]:
                    # it obtains the index location of the worker in all_worker_names and then adds the amount of time they logged to the 0 which matches the index inside the new_currentlist
                    for counter in range(len(new_current)):
                        if new_current[counter][2] == issue.fields.summary:
                            new_current[counter][j+5] += time # I add 5 to avoid any of the list items before the 0s

  
    # aesthetic purposes, replaces the 0s in each nested list inside new_currentlist with blank spaces
    for i in range(len(new_current)):
        for j in range(len(new_current[i])):
            if new_current[i][j] == 0:
                new_current[i][j] = ""

    # if the current project is the first project being written to the csv file, write the headers into the file 
    # csv header will only contain the names of the workers at this point, so this section adds the rest of the headers into that list
    if projectcount == 0:
        csv_header.insert(0, 'Resdate')
        csv_header.insert(0, 'Createdate')
        csv_header.insert(0, 'issue_desc')
        csv_header.insert(0, 'issueid')
        csv_header.insert(0, 'Projectid')


    with open ('test3.csv', mode='a', encoding='utf-8') as file: # encoding is used to write characters that the ascii codec cannot encode
        writer = csv.writer(file, delimiter=",", quoting=csv.QUOTE_ALL)
        if projectcount == 0:
            writer.writerow(csv_header)
        
        for i in range(len(new_current)):
            writer.writerow((new_current[i])) # writes thew new_currentlist which contains the project id, issue id, issue summary. creation date, resolution date and the workers names in that order

    print(projectname, "has been loaded into the file")
    projectcount += 1 # adds 1 to the project counter to say that the first project has been full loaded, this is to avoid the header being written more than once

print('report is ready ^_^')
