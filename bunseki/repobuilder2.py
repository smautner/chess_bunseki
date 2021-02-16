import chess.pgn
from copy import deepcopy
from types import SimpleNamespace


import chess
import bunseki.util
import bunseki.util as util
import bunseki.asklichess as ali
from collections import defaultdict 
import argparse

from stockfish import Stockfish 

parser = argparse.ArgumentParser() 
parser.add_argument('-w','--white',dest='COLOR', help= 'is the repertoire for white', type=int, choices=[0,1], required=True)
parser.add_argument('-i','--pgnfile',dest='PGNFILE', help= 'path to pgn file to parse', type=str, default= '')
parser.add_argument('-u','--utilitycut',dest='UTILITYCUT', help= 'determines depth,  ', type=float, default = 1000)
parser.add_argument('-c','--mydb',dest='SHAREDB', help= 'our db is the masterdb, if this is 1 it is the same as the default db', type=int, default = 0)
parser.add_argument('-d','--database',dest='DATABASE', help= '0 = master database 1 = lichess', type=int, default = 0)
parser.add_argument('-s','--lichess_strength',dest='STRENGTH', help= 'select playing strength for lichess db', type=int,nargs='+', default = [1600,1800])
parser.add_argument('-t','--lichess_format',dest='TIMECTL', help= 'select time control for lichess db', type=str,nargs='+', default = ['blitz','rapid'])
parser.add_argument('--min-ply',dest='MINPLY', help= 'dont show alternatives for the first plies', type=int, default = -1)
#parser.add_argument('-m','--choose_most_played',dest='MYMOVE',default = 'best', help= 'criterion for choosing our move most_played,terminate, or best', type=str)



desired= 'd4 Nf3 g3 Bg2 O-O'.split()
depth = 26
stockfish = Stockfish('/home/ikea/projects/strat_game/chess/stockfish209',depth = depth,parameters={"Threads": 8, "Hash":64})
enginecache = util.cacher(f"{depth}")
enginecache2 = util.cacher(f"best{depth}")

def get_eval_uncached(fen):
    stockfish.set_fen_position(fen)
    res= stockfish.get_evaluation()
    return res['value']/100

def get_best_uncached(fen):
    stockfish.set_fen_position(fen)
    res= stockfish.get_best_move()
    return res

def get_eval(fen):
   return  enginecache.call(lambda: get_eval_uncached(fen), fen)

def get_best(fen):
   return  enginecache2.call(lambda: get_best_uncached(fen), fen)




def illegal(san,board):
    try:
        board.push_san(san)
    except:
        return True
    return False



lalala = 65

def main(): 
    args = parser.parse_args()
    masterarg= SimpleNamespace(DATABASE=0)
    game = util.loadpgn(args.PGNFILE) if args.PGNFILE else chess.pgn.Game() 
    game.proba = 1
    fens = {} # known gamenodes

    def getjmp():
        global lalala
        r = f"#{chr(lalala)}#"
        lalala +=1
        return r

    db = ali.lichess(args)
    if args.DATABASE == 1 and args.SHAREDB == 0:
        mydb = ali.lichess(masterarg)
    else:
        mydb = db


    '''
    fen = game.board().fen()
    moves, total_games, openingname = h.call( lambda: ali.ask(fen,args),fen)
    game.proba = 1
    game.openingname = openingname
    if args.COLOR ==0:
        proba_calculation(game, moves, total_games)
    '''

    def myturn(gn):
        return gn.ply()% 2 != args.COLOR



    def visit(gn):
        '''
        a visitation does this:
            1. ask liches whats up (and print status)
            2. decide if we need to add moves 
            3. update probabilities of all children
        '''

        fen = gn.board().fen()
        if fen in fens:
            # seen before, abbort 
            jump = getjmp()
            gn.comment += f"to {jump}"
            other= fens[fen] 
            other.comment += f"from {jump}"
            return []
        else:
            # we see this for the first tims 
            fens[fen]=gn
            

        try:
            moves, movesum, opening = (mydb if myturn(gn) else db).ask(fen)
        except:
            db.end()
            mydb.end()
            assert False, 'sending requests too fast probably'
        if not moves: # to few moves, i guess
            return []

        print(gn.ply())
        print(gn.board().unicode(invert_color=True))


        skip =  gn.ply() < args.MINPLY
        if gn.ply() > 15: 
            return []

        if myturn(gn):
            best_san = util.find_best(moves, gn.ply())

            movenum = int(gn.ply()/2)
            want_move = ''
            if movenum < len(desired):
                want_move = desired[movenum]

            if not gn.variations and not skip:
                    

                    # new logic:
                    # if want move:
                    #    same as best: do it
                    #    illigal: best 
                    #    legal: cmp
                    # else:
                    #    choose engine move


                    if want_move:
                        if want_move == best_san or illegal(want_move, gn.board()):
                            mov = gn.board().push_san(best_san)
                            child = gn.add_variation(mov)
                        else:
                            b1,b2 = gn.board(),gn.board()
                            b1.push_san(best_san)
                            b2.push_san(want_move)
                            f1, f2 = b1.fen(), b2.fen()
                            f1s = get_eval(f1)
                            f2s = get_eval(f2)
                            if f1s > f2s+.35:
                                domove = best_san
                            else:
                                domove = want_move
                            mov = gn.board().push_san(domove)
                            child = gn.add_variation(mov)
                            child.comment  = f'theirs:{f1s}  mine:{f2s}'
                    else:
                        muci = get_best(gn.board().fen())
                        print("MUCI",muci)
                        best_mv = chess.Move.from_uci(muci)
                        #mov = gn.board().push(best_mv)
                        child = gn.add_variation(best_mv)

 
        else:
            second_border = bunseki.util.sumdi(moves[0])*.333
            for move in moves: 
                freq = bunseki.util.sumdi(move)
                if freq > args.UTILITYCUT and freq > second_border: 
                    mov = gn.board().push_san(move['san']) 
                    if not gn.has_variation(mov):
                        if not skip:
                            child = gn.add_variation(mov)
                    
        
        return gn.variations

    # main loop
    nodelist =  [game]
    while nodelist: 
        node = nodelist.pop()
        nodelist+=visit(node)

    db.end()
    mydb.end()
    enginecache.write()
    enginecache2.write()
    print(game)
    
    
    def split_ply(game,where): 
        # find nodes at a certain ply: 
        roots=[]
        def find_n(gn): 
            if gn.ply() == where: 
                roots.append(gn)
            else:
                for v in gn.variations:
                    find_n(v)
        find_n(game) 
        games = [mkgame(game,r) for r in roots]
        return games



    games = split_ply(game,7)
    print (f"where are this many games: {len(games)}")
    for game in games:
        print()
        print (game)


def mkgame(game,r):
    history = util.history(r)
    game = chess.pgn.Game()
    node = game
    print(history[:-1])
    for move in history[:-1]: 
        node = node.add_variation(chess.Move.from_uci(move))
    node.variations = [r]
        
    return game
    




if __name__ == '__main__':
    main()
