import codiaclient as cc

if __name__ == "__main__":
    args = cc.ArgParser().parse_args()
    if args.no_cache: cc.cache_var['cacheOn'] = False
    if cc.cache_var['cacheOn']: cc.cache_load()
    cc.report_var['allow_error_deg'] = args.allow_error_deg
    cc.query_var['lang'] = args.lang
    cc.query_var['eid'] = args.eid
    cc.query_var['pid'] = args.pid
    if args.open:
        cc.query_var['solutioncode'] = args.open.read()
        args.open.close()

    cc.client_login(username = args.username, password = args.passwd, cookie = args.cookie)

    cc.query_var['username'] = cc.logined()
    if args.query_string: print(cc.query(args.query_string.split()), end = '')
    else:
        while True:
            try: print(cc.query(input().split()), end = '')
            except (KeyboardInterrupt, EOFError): break