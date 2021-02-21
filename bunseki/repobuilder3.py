import chess.pgn
from copy import deepcopy
from types import SimpleNamespace


import chess
import bunseki.util
import bunseki.util as util
import bunseki.asklichess as ali
from collections import defaultdict 
import argparse


parser = argparse.ArgumentParser() 
parser.add_argument('--black',dest='COLOR', help= 'is the repertoire for white',action='store_false')
parser.add_argument('--pgn',dest='PGNFILE', help= 'path to pgn file to parse', type=str, default= '')
parser.add_argument('--cut',dest='UTILITYCUT', help= 'stop at this many moves played  ', type=float, default = 1000)
parser.add_argument('--min-ply',dest='MINPLY', help= 'dont show alternatives for the first plies', type=int, default = -1)
parser.add_argument('--annotate',dest='NOTE', help= 'annotation only! add no moves',action='store_true')


parser.add_argument('--mydb',dest='mydb', help='', type = str, default = 'master')
parser.add_argument('--aite',dest='aite', help='', type = str, default = 'blitz_rapid_2200_2500')


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
    game = util.loadpgn(args.PGNFILE) #if args.PGNFILE else chess.pgn.Game() 
    fens = {} # known gamenodes

    def getjmp():
        global lalala
        r = f"#{chr(lalala)}#"
        lalala +=1
        return r

    mydb = ali.lichess2(args.mydb)
    if args.aite == args.mydb:
        db = mydb
    else:
        db = ali.lichess2(args.aite)
        

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

        if myturn(gn) and not skip:
                
            best_san = util.find_best(moves, gn.ply())
            best_san_valid = bunseki.util.sumdi(moves[0]) >= 50 # best move has been played at least 50x
            mov = gn.board().push_san(best_san)


            if gn.variations:
                if not gn.has_variation(mov) and best_san_valid:
                    gn.variations[0].comment+=f" better:{best_san}"

            elif best_san_valid and not args.NOTE:
                gn.add_variation(mov)
        elif not skip:
            second_border = bunseki.util.sumdi(moves[0])*.2
            for move in moves: 
                freq = bunseki.util.sumdi(move)
                if freq > args.UTILITYCUT and freq > second_border: 
                    mov = gn.board().push_san(move['san']) 
                    if not gn.has_variation(mov):
                        # move is not yet in the list and noteworthy
                        if args.NOTE:
                            gn.comment+=f" -> {move['san']}"
                        else:
                            gn.add_variation(mov)
        
        return gn.variations

    # main loop
    nodelist =  [game]
    while nodelist: 
        node = nodelist.pop()
        nodelist+=visit(node)

    db.end()
    mydb.end()
    print(game)
    
    '''
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
    '''


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
