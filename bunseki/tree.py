# we interact with this: https://github.com/niklasf/lila-openingexplorer



import requests as req
import time
import bunseki.util as util

session = req.Session()



class lichess:
    def __init__(self,dbstring):
        self.hasher = util.cacher( dbstring )
        # letd parse the dbstring...
        self.master = 'master' in dbstring
        self.STRENGTH = [item  for item in '1600 1800 2000 2200 2500'.split() if item in dbstring   ]
        self.TIMECTL = [item  for item in 'blitz rapid bullet classical'.split() if item in dbstring   ]
    
    def end(self):
        self.hasher.write()

    def ask(self, fen):
        reply =  self.hasher.call( lambda: self.lookup(fen),fen)
        return reply


    def lookup(self,fen):
        print(".",end='')
        if not self.master:
            parm = {'fen':fen, 
                    'topGames': 0,
                    'recentGames':0, 
                    'moves':'15',
                    'variant':"standard",
                    'speeds[]':self.TIMECTL,
                    'ratings[]':self.STRENGTH}
            res = session.get('https://explorer.lichess.ovh/lichess', params=parm)
        else:
            parm = {'fen':fen, 'topGames': 0, 'moves':'15' }
            res = session.get('https://explorer.lichess.ovh/master', params=parm)

        if  res.status_code == 200:
            js = res.json()
            time.sleep(1)
            return js['moves'], sumdi(js), js['opening'] or ''
        else:
            print (res.status_code)
            print(res.text)
            assert False

def get_databases(args):
    pass


def sumdi(di):
    return di['black']+di['white']+di['draws']
