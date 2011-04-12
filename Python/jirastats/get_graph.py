from lib import Date, getDatesFromRange, loadStats, buildPlot, buildPie
from config import *

iteration = iters[-1]
iter_range = iteration["range"]
iter_exc = iteration["exclude"]
filename = "%s_%s.yaml" % iter_range
data_first, data_last = iter_range

all_dates = getDatesFromRange(iter_range)
filterstats = lambda a, b: [a[i] for i in range(len(a)) if i not in b]
work_dates = filterstats(all_dates, iter_exc)

struct = loadStats(filename)

pl_sum = un_sum = 0
es_list = list()
pl_list = list()
un_list = list()
to_list = list()
de_list = list()
for d in all_dates:
	day_data = struct.get(d)
	if not day_data:
		continue

	es_value = float(day_data["es"])
	es_list.append(es_value)

	pl_sum += float(day_data["pl"])
	pl_list.append(pl_sum)

	un_sum += float(day_data["un"])
	un_list.append(un_sum)

	to_sum = pl_sum + un_sum
	to_list.append(to_sum)

	de_value = pl_sum + es_value - es_list[0]
	de_list.append(de_value)

es_list, pl_list, un_list, to_list, de_list = \
	map(lambda a: filterstats(a, iter_exc),
	(es_list, pl_list, un_list, to_list, de_list))

lines = [	[es_list, "b", "s", 2, "planned time"],
		[pl_list, "r", "p", 2, "planned time spent"],
		[un_list, "g", "*", 2, "unplanned time spent"],
		[to_list, "c", "o", 2, "total time spent"],
		[de_list, "m", "x", 2, "planned time delta"],
	]

buildPlot(work_dates, lines, "plot.png")

pie_data = loadStats("pie.yaml")
buildPie(pie_data, "pie.png")
