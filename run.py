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
    cc.requests_var['l'] = args.lang
    cc.requests_var['e'] = args.eid
    cc.requests_var['p'] = args.pid
    if args.open:
        cc.requests_var['sc'] = args.open.read()
        args.open.close()

    cc.client_login(username = args.username, password = args.passwd, cookie = args.cookie)

    if args.request_string:
        try:
            if not variables['origin']:
                print(str(cc.requests(args.request_string.split())).encode('utf-8').decode('unicode-escape'), end = '')
            else:
                print(str(cc.requests(args.request_string.split())), end = '')
        except (KeyboardInterrupt, EOFError): exit()
    else:
        while True:
            try:
                if not variables['origin']:
                    print(str(cc.requests(input().split())).encode('utf-8').decode('unicode-escape'), end = '')
                else:
                    print(str(cc.requests(input().split())), end = '')
            except (KeyboardInterrupt, EOFError): break
