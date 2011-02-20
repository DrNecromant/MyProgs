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
			log[TS] = int(worklog.timeSpentInSeconds / 60)
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
		data[ES] = int(issueObj.estimate / 60)
		data[TS] = int(issueObj.timeSpent / 60)
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

def getDatesFromRange(daterange):
	"""
	Get list of dates in tuple format from date range
	"""
	convert_date = lambda a: datetime(*map(int, a.split("-")))
	date1, date2 = map(convert_date, daterange)
	dayscount = (date2 - date1).days
	dates = [date1 + timedelta(i) for i in range(dayscount)]
	dates = [(d.year, d.month, d.day) for d in dates]
	return dates
