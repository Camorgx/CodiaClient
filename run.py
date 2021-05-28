import codiaclient as cc
variables = {
    "origin": False
}
if __name__ == "__main__":
    args = cc.ArgParser().parse_args()
    if args.no_cache: cc.cache_var['cacheOn'] = False
    if args.register: cc.net_var['register'] = True
    if args.origin: variables['origin'] = True
    if cc.cache_var['cacheOn']: cc.cache_load()
    cc.report_var['allow_error_deg'] = args.allow_error_deg
    cc.requests_var['lang'] = args.lang
    cc.requests_var['eid'] = args.eid
    cc.requests_var['pid'] = args.pid
    if args.open:
        cc.requests_var['solutioncode'] = args.open.read()
        args.open.close()

    cc.client_login(username = args.username, password = args.passwd, cookie = args.cookie)

    cc.requests_var['username'] = cc.logined()
    if args.query_string: print(cc.requests(args.query_string.split()), end = '')
    else:
        while True:
            try:
                if not variables['origin']:
                    print(str(cc.requests(input().split())).encode('utf-8').decode('unicode-escape'), end = '')
                else:
                    print(str(cc.requests(input().split())), end = '')
            except (KeyboardInterrupt, EOFError): break
