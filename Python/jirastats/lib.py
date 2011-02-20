import SOAPpy
from datetime import datetime, timedelta, date
from pylab import plot, grid, xticks, yticks, title, legend, savefig, clf, pie, figure

from consts import *

class JiraWrapper():
	def __init__(self, user, passwd):
		self.srv = SOAPpy.WSDL.Proxy(jiraurl)
		self.auth = self.srv.login(user, passwd)
		self.count = ISSUES_COUNT

	def getWorkLog(self, key):
		"""
		Get work log from issue key
		"""
		logs = []
		worklogs = self.srv.getWorklogs(self.auth, key)
		for worklog in worklogs.data:
			log = {}
			log[AU] = worklog.author
			log[CO] = worklog.comment
			log[CR] = worklog.created[:3]
			log[TS] = worklog.timeSpentInSeconds / 60
			logs.append(log)
		return logs

	def convertIssue(self, issueObj):
		"""
		Convert issue from object with attrs
		to dictionary
		"""
		data = {}
		data[AS] = issueObj.assignee
		data[KE] = issueObj.key
		data[SU] = issueObj.summary
		data[RE] = issueObj.resolution
		data[ES] = issueObj.estimate / 60
		data[TS] = issueObj.timeSpent / 60
		return data

	def getIssues(self, sstr):
		"""
		Get issues from current date interval
		"""
		add_str = " and assignee in (%s) and project != QA"
		sstr += add_str % ", ".join(atqa)
		objs = self.srv.getIssuesFromJqlSearch(self.auth,
			sstr, self.count).data
		issues = map(self.convertIssue, objs)
		return issues

def getDates(self, duration):
	"""
	Get list of dates in tuple format from duration
	"""
	convert_date = lambda a: datetime(*map(int, a.split("-")))
	date1, date2 = map(convert_date, duration)
	dayscount = (date2 - date1).days
	dates = [date1 + timedelta(i) for i in range(dayscount)]
	dates = [(d.year, d.month, d.day) for d in dates]
	return dates

def buildGraph(lines, dates, iter_range, owners, fname):
	x, y = len(dates), len(dates) * len(owners) * 4 / 6
	plot([0, x], [0, y], "b--", label = "normal speed (4h/day for person)")

	for line in lines:
		plot(line["d"], line["c"], label = line["l"])
		plot(line["d"], line["c"][0])

	ylocs = yticks()[0]
	date_format = lambda a: "%dd(%dh)" % (a, a*6)
	yticks(ylocs, [""] + map(date_format, ylocs)[1:])
	weekdays = map(lambda a: date(*a).strftime("%A")[:3], dates)
	xticks(range(len(weekdays)), weekdays)

	gtitle = "AT QA iter from %s to %s" % iter_range
	if len(owners) == 1:
		gtitle += " (%s)" % owners[0]
	title(gtitle)
	grid(True)
	legend(loc = "upper left")
	savefig(fname)
	clf()

def buildPie(es_data):
	data = es_data.items()
	labels = [l[0] for l in data]
	values = [l[1] for l in data]
	labels = [l + "(%.2fd)" % es_data[l] for l in labels]

	figure(figsize=(8,8))
	pie(values, labels = labels)
	savefig("pie.png")
