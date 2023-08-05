import sys
#import yaml

#y = yaml.load(open(sys.argv[1]))
#
#PORT = y["PORT"]
#USERS = y["USERS"]


PORT = 3256

# name -> secret (32 hex chars)
USERS = {
    "tg":  "0123456789abcdef0123456789abcdef"
}

# Tag for advertising, obtainable from @MTProxybot

AD_TAG = "02b86204e28dfceda581080dd966179c"
#PREFER_IPV6 = False
#FAST_MODE = False
