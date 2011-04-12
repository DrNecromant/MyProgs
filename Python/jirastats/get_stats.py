from lib import JiraWrapper, Date, loadStats, dumpStats, formatLogWork
from config import *

iteration = iters[-1]
iter_range = iteration["range"]
filename = "%s_%s.yaml" % iter_range
data_first, data_last = iter_range
user = raw_input("Login:")
passwd = raw_input("Password:")
print "\n" * 1000
jira = JiraWrapper(user, passwd)

iter_sstr = ITER_SSTR % (data_first, data_last)
issues_iter = jira.getIssues(iter_sstr)

yesterday = Date().dec(1)
today = Date()
upd_sstr = UPD_SSTR % (yesterday.d_str, today.d_str)
issues_upd = jira.getIssues(upd_sstr)

plan_ts = 0
unplan_ts = 0
es_sum = sum([issue["estimate"] for issue in issues_iter])
for i_upd in issues_upd:
	wls = jira.getWorkLog(i_upd["key"])
	wls = filter(lambda a: a["created"] == yesterday.d_tup, wls)
	if not wls:
		continue
	ts = sum([a["timespent"] for a in wls])
	if i_upd in issues_iter:
		plan_ts += ts
	else:
		unplan_ts += ts

struct = loadStats(filename)
es_sum, plan_ts, unplan_ts = map(formatLogWork, (es_sum, plan_ts, unplan_ts))
struct[today.d_str] = {"es": es_sum, "pl": plan_ts, "un": unplan_ts}
dumpStats(filename, struct)

pie_data = dict()
for i_iter in issues_iter:
	es = i_iter["estimate"]
	if not es:
		continue
	ow = i_iter["assignee"]
	if not ow in pie_data.keys():
		pie_data[ow] = es
	else:
		pie_data[ow] += es
pie_data = dict([(a, formatLogWork(b)) for a, b in pie_data.items()])
dumpStats("pie.yaml", pie_data)
