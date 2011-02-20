import SOAPpy
from datetime import datetime, timedelta, date
from pylab import plot, grid, xticks, yticks, title, legend, savefig, clf, pie, figure

from consts import *
total = None

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
			log[TS] = worklog.timeSpentInSeconds
			log[TS] = int(log[TS] / 60)
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
		data[WL] = self.getWorkLog(data[KE])
		return data

	def getIssues(self, sstr, assignee):
		"""
		Get issues from current date interval
		"""
		add_str = " and assignee in (%s) and project != QA"
		sstr += add_str % ", ".join(assignee)
		objs = self.srv.getIssuesFromJqlSearch(self.auth,
			sstr, self.count).data
		issues = map(self.convertIssue, objs)
		return issues

class JiraStats(JiraWrapper):
	def __init__(self, user, passwd, duration):
		JiraWrapper.__init__(self, user, passwd)
		self.duration = duration

	def getDates(self):
		"""
		Get list of dates in tuple format from duration
		"""
		convert_date = lambda a: datetime(*map(int, a.split("-")))
		date1, date2 = map(convert_date, self.duration)
		dayscount = (date2 - date1).days
		dates = [date1 + timedelta(i) for i in range(dayscount)]
		dates = [(d.year, d.month, d.day) for d in dates]
		return dates

	def getWorkLogs(self, issues):
		"""
		Get all work logs for issues in one list
		"""
		return sum([i[WL] for i in issues], [])

	def filterWorkLogs(self, logs, period):
		"""
		Filter work logs from period if period is date list
		Filter work logs before date if period is date
		The date should has format: (year, month, day)
		"""
		if type(period) == list:
			logs = filter(lambda l: l[CR] in period, logs)
		elif type(period) == tuple:
			logs = filter(lambda l: l[CR] < period, logs)
		else:
			raise Exception("Invalid type: %s" % type(period))
		return filter(lambda l: l[AU] in self.owners, logs)

	def getTimeSum(self, objs, *timeparams):
		"""
		Get time sum of objects timespent from param
		Oblects: worklog, issues
		Params: timespent, estimate
		"""
		s = 0
		for p in timeparams:
			s += sum([obj[p] for obj in objs])
		return s

	def getTimeStats(self, issues, dates, *timeparams):
		"""
		Get time stats in structure:
		[date1: {timeparam1: value1, timeparam2: value2},
		date2: {timeparam1: value3, timeparam2: value4}]
		"""
		stats = dict([(d, dict([(p, 0) for p in timeparams])) \
			for d in dates])
		logs = self.getWorkLogs(issues)
		if TS in timeparams:
			iter_logs = self.filterWorkLogs(logs, dates)
			for log in iter_logs:
				stats[log[CR]][TS] += log[TS]
		if ES in timeparams:
			total_time = self.getTimeSum(issues, TS, ES)
			for d in dates:
				prv_logs = self.filterWorkLogs(logs, d)
				prv_time = self.getTimeSum(prv_logs, TS)
				stats[d][ES] = total_time - \
					prv_time - stats[d][TS]
		return stats

	def getProgress(self, sstr, dates, owners, set_total = False):
		global total
		self.owners = owners
		args = {True: [TS, ES], False: [TS]}[set_total]
		issues = self.getIssues(sstr, atqa)
		times = self.getTimeStats(issues, dates, *args)
		data = [float(times[d][TS]) / 360 for d in dates]
		if set_total:
			if self.owners != atqa:
				issues = self.getIssues(sstr, self.owners)
				times = self.getTimeStats(issues, dates, *args)
			times1 = times[dates[0]]
			total = float(times1[TS] + times1[ES]) / 360
		return [sum(data[:i+1]) for i in range(len(data))]

def buildGraph(lines, dates, iter_range, owners, fname):
	x, y = len(dates), len(dates) * len(owners) * 4 / 6
	plot([0, x], [0, y], "b--", label = "normal speed (4h/day for person)")
	if total:
		plot([0, x], [0, total], "r--", label = "planned iter speed")

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
