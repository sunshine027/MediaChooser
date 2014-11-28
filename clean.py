import os

for r, d, f in os.walk('.'):
	for i in f:
		if not i.endswith('.pyc'):
			continue
		tmpfn = os.path.join(r, i)
		print tmpfn
		os.remove(tmpfn)
pass
