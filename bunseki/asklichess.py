# we interact with this: https://github.com/niklasf/lila-openingexplorer



import requests as req
from pprint import pprint
import time
import bunseki.util as util

session = req.Session()


class lichess:
    def __init__(self,args):
        self.args=args
        if args.DATABASE == 1:
            hashname = hash((args.DATABASE, tuple(args.STRENGTH), tuple( args.TIMECTL)))
        else:
            hashname = 23
        self.hasher = util.cacher( hashname )
    
    def end(self):
        self.hasher.write()

    def ask(self, fen):
        reply =  self.hasher.call( lambda: self.lookup(fen),fen)
        return reply


    def lookup(self,fen):
        print(".",end='')
        if self.args.DATABASE ==1:
            parm = {'fen':fen, 
                    'topGames': 0,
                    'recentGames':0, 
                    'moves':'15',
                    'variant':"standard",
                    'speeds[]':self.args.TIMECTL,
                    'ratings[]':self.args.STRENGTH}
            res = session.get('https://explorer.lichess.ovh/lichess', params=parm)
        else:
            parm = {'fen':fen, 'topGames': 0, 'moves':'15' }
            res = session.get('https://explorer.lichess.ovh/master', params=parm)

        if  res.status_code == 200:
            js = res.json()
            time.sleep(.8)
            return js['moves'], sumdi(js), js['opening'] or ''
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


def analyze_single(di, mvsum, okmoves):
    # returns percentage, inlist, and display string
    mvcnt = sumdi(di)
    perc = mvcnt/ mvsum
    inlist = di['san'] in okmoves
    description  = f"\t{di['san']}\t{mvcnt}({fmt_stst(mvcnt,mvsum)})\t{'OK' if inlist else '!!'} {fmt_q(di)}"

    return perc, inlist, description, mvcnt


def missvalue(z):
    return max(z)
    if len(z) == 0:
        return 0.01
    return sum(z)/len(z)
    #return sum([i**2 for i in z])/len(z)/1000

def analyse2(move_dict_list,okmoves,minmov, target_share, minperc):

    '''
    move_dict_list: dicts from lichess db
    okmoves: san of the moves we have in our list
    minmov: ignore moves played less than this
    target_share: we want this much coverage
    minperc: move occurange in db
    '''

    sum_moves = sum([ sumdi(di) for di in move_dict_list   ] )

    # for every move -> calculate percentage covered and the indicator string
    all_moves  = [ analyze_single (di,sum_moves,okmoves) for di in move_dict_list ]
    perc_ok =  sum([a[0] for a in all_moves if a[1]])
    if perc_ok > target_share:
        perc_missing = 0
    else:

        # was wollen wir hier? ich will messen wie schlecht wir sind...
        # 5+5+5+5 < 20 ... 
        vls = [ a[0] for a in all_moves if a[0]>minperc and not a[1]]
        perc_missing = missvalue([ a[0] for a in all_moves if  not a[1]])
        #print(vls, perc_missing)
        
        #print(perc_missing, perc_ok, sum([a[0] for a in all_moves if a[0] < 5 and not a[1]]))



    ret = '\n'.join([a[2] for a in all_moves if a[3] > minmov and a[0] > minperc])
    return ret, perc_missing 

