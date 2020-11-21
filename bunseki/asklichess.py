# we interact with this: https://github.com/niklasf/lila-openingexplorer



import requests as req
from pprint import pprint
import time

session = req.Session()

def ask(fen, args):
    print(".",end='')
    if args.DATABASE ==1:
        parm = {'fen':fen, 
                'topGames': 0,
                'recentGames':0, 
                'moves':'15',
                'variant':"standard",
                'speeds[]':args.TIMECTL,
                'ratings[]':args.STRENGTH}
        res = session.get('https://explorer.lichess.ovh/lichess', params=parm)
    else:
        parm = {'fen':fen, 'topGames': 0, 'moves':'15' }
        res = session.get('https://explorer.lichess.ovh/master', params=parm)

    if  res.status_code == 200:
        js = res.json()
        time.sleep(.5)
        return js['moves'], sumdi(js) 
    else:
        print (res.status_code)
        print(res.text)
        assert False



def sumdi(di):
    return di['black']+di['white']+di['draws']


def fmt_stst(my,al):
    return int((my/al)*100)
def fmt_q(di):
    a= sumdi(di)
    i = lambda x: int(x*100)
    return [ i(di[v]/a) for v in['white','draws','black']   ]

def analyse(lidi,okmoves,minmov,minperc, games_total):
    ret = []
    dirty= False
    sum_moves = sum([ sumdi(di) for di in lidi   ] )

    cum_mv =0 
    aru = 0
    for di in lidi: 
        if cum_mv < minperc*sum_moves: # havent reached 90% yet
            mvcnt = sumdi(di)
            if mvcnt > minmov: # more than minmov played
                cum_mv+= mvcnt 
                freq = f"freq: { (mvcnt*100)/games_total :.2f}"
                if  di['san'] not in okmoves:
                    ret.append( f"\t{di['san']}\t{mvcnt}({fmt_stst(mvcnt,sum_moves)})\t!! {fmt_q(di)}"   )
                    dirty = True
                else:
                    aru+=mvcnt
                    ret.append( f"\t{di['san']}\t{mvcnt}({fmt_stst(mvcnt,sum_moves)})\tOK {fmt_q(di)}"   )
    
    
    if not dirty:
        ret = ''
    else:
        ret = '\n'.join(ret)
    return ret, minperc*sum_moves- aru

