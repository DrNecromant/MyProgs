import SOAPpy
from datetime import datetime, timedelta, date
from pylab import plot, grid, xticks, yticks, title, legend, savefig, clf, pie, figure
import yaml, os

from consts import *

formatLogWork = lambda a: "%.2f" % (a / 360.0)

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
		Get issues from search string
		"""
		add_str = " and assignee in (%s) and project != QA"
		sstr += add_str % ", ".join(atqa)
		objs = self.srv.getIssuesFromJqlSearch(self.auth,
			sstr, self.count).data
		issues = map(self.convertIssue, objs)
		return issues

class Date():
	"""
	Class to present date in
	different formats (date, str, tuple)
	"""
	def __init__(self, d = date.today()):
		t = type(d)
		if t == date:
			self.d_dat = d
			self.d_tup = (d.year, d.month, d.day)
			self.d_str = "%s-%s-%s" % self.d_tup
		elif t == str:
			self.d_str = d
			self.d_tup = tuple(map(int, d.split("-")))
			self.d_dat = date(*self.d_tup)
		elif t == tuple:
			self.d_tup = d
			self.d_dat = date(*d)
			self.d_str = "%s-%s-%s" % d
		else:
			raise Exception("Invalid date type to convert")

	def inc(self, x):
		if type(x) != int:
			raise Exception("Invalid delta type to convert")
		self.d_dat += timedelta(x)
		self.d_tup = (self.d_dat.year, self.d_dat.month, self.d_dat.day)
		self.d_str = "%s-%s-%s" % self.d_tup
		return self

	def dec(self, x):
		if type(x) != int:
			raise Exception("Invalid delta type to convert")
		self.d_dat -= timedelta(x)
		self.d_tup = (self.d_dat.year, self.d_dat.month, self.d_dat.day)
		self.d_str = "%s-%s-%s" % self.d_tup
		return self

def getDatesFromRange(daterange):
	"""
	Get list of dates in string format from date range
	"""
	convert_date = lambda a: datetime(*map(int, a.split("-")))
	date1, date2 = map(convert_date, daterange)
	dayscount = (date2 - date1).days
	dates = [date1 + timedelta(i) for i in range(dayscount)]
	dates = ["%s-%s-%s" % (d.year, d.month, d.day) for d in dates]
	return dates

def loadStats(filename):
	"""
	Load data from yaml file
	"""
	if not os.path.exists(filename):
		struct = dict()
	else:
		fd = open(filename)
		struct = yaml.load(fd)
		fd.close()

	return struct

def dumpStats(filename, struct):
	"""
	Save data in yaml file
	"""
	fd = open(filename, "w")
	fd.write(yaml.dump(struct))
	fd.close()

def buildPlot(dates, lines, filename):
	max_x = len(dates)
	max_y = lines[0][0][0]
	plot([0, max_x], [max_y, 0], "b--")
	for line in lines:
		data = line[0]
		color = line[1]
		sign = line[2]
		width = line[3]
		label = line[4]
		plot(data, color, linewidth = width)
		plot(data, "%s%s" % (color, sign), label = label)

	ylocs = yticks()[0]
	date_format = lambda a: "%dd(%dh)" % (a, a*6)
	yticks(ylocs, [""] + map(date_format, ylocs)[1:])
	weekdays = map(lambda a: Date(a).d_dat.strftime("%A")[:3], dates)
	xticks(range(len(weekdays)), weekdays)

	title("%s - %s iteration" % (dates[0], dates[-1]))
	grid(True)
	legend(loc = "upper right")
	savefig(filename)

def buildPie(pie_data, filename):
	labels, values = zip(*[("%s(%sd)" % (a, b), float(b)) \
				for a, b in pie_data.items()])
	figure(figsize=(9,9))
	pie(values, labels = labels)
	savefig(filename)
