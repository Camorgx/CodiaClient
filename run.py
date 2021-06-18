import codiaclient as cc

variables = {
    "origin": False
}

if __name__ == "__main__":
    args = cc.ArgParser().parse_args()
    cc.ArgInit(args)
    if args.origin: variables['origin'] = True
    cc.client_login(args)

    if args.request_string:
        try:
            if not variables['origin']: print(str(cc.requests(args.request_string.split())).encode('utf-8').decode('unicode-escape'), end = '')
            else: print(str(cc.requests(args.request_string.split())), end = '')
        except (KeyboardInterrupt, EOFError): exit()
    else:
        while True:
            try:
                if not variables['origin']: print(str(cc.requests(input().split())).encode('utf-8').decode('unicode-escape'), end = '')
                else: print(str(cc.requests(input().split())), end = '')
            except (KeyboardInterrupt, EOFError): break
