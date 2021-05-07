from argparse import ArgumentParser

def filepath(x):
    try: return open(x, encoding = 'utf-8')
    except: raise ValueError

def ArgParser():
	parser = ArgumentParser()
	parser.add_argument("-o", "--open", help = "open code to submit from PATH", metavar = 'PATH', type = filepath)
	parser.add_argument("-e", "--eid", help = "eid of the exercise", metavar = 'EID')
	parser.add_argument("-p", "--pid", help = "pid of the pack", metavar = 'PID')
	parser.add_argument("-l", "--lang", help = "lang of the code", default = 'CPP', metavar = 'LANG', choices = {'CPP', 'C', 'PYTHON'})
	parser.add_argument("-c", "--cookie", help = "cookie of your codia account", metavar = 'COOKIE')
	parser.add_argument("-u", "--username", help = "your codia username")
	parser.add_argument("--passwd", "--password", help = "your codia password")
	parser.add_argument("--no-cache", help = "do not cache or use cached username, password & cookie", action = 'store_true')
	parser.add_argument("--allow-error-deg", help = "allow errors degree", type = int, choices = {0, 1, 2, 3}, default = 2)
	parser.add_argument("-q", "--query-string", help = "your query string", metavar = 'QUERY')
	return parser
