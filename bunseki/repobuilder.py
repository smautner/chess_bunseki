import chess.pgn
from types import SimpleNamespace

import bunseki.util
import bunseki.util as util
import bunseki.asklichess as ali
from collections import defaultdict 
import argparse



parser = argparse.ArgumentParser() 
parser.add_argument('-w','--white',dest='COLOR', help= 'is the repertoire for white', type=int, choices=[0,1], required=True)
parser.add_argument('-i','--pgnfile',dest='PGNFILE', help= 'path to pgn file to parse', type=str, required=True)
parser.add_argument('-u','--utilitycut',dest='UTILITYCUT', help= 'cutoff based on utility..i.e. probability that the top move is on board', type=float, default = 2)
parser.add_argument('-c','--mydb',dest='SHAREDB', help= 'our db is the masterdb, if this is 1 it is the same as the default db', type=int, default = 0)
parser.add_argument('-d','--database',dest='DATABASE', help= '0 = master database 1 = lichess', type=int, default = 0)
parser.add_argument('-s','--lichess_strength',dest='STRENGTH', help= 'select playing strength for lichess db', type=int,nargs='+', default = [1600,1800])
parser.add_argument('-t','--lichess_format',dest='TIMECTL', help= 'select time control for lichess db', type=str,nargs='+', default = ['blitz','rapid'])
parser.add_argument('--min-ply',dest='MINPLY', help= 'dont show alternatives for the first plies', type=int, default = -1)

parser.add_argument('-m','--choose_most_played',dest='MYMOVE',default = 'best', help= 'criterion for choosing our move most_played,terminate, or best', type=str)

def main(): 
    args = parser.parse_args()
    masterarg= SimpleNamespace(DATABASE=0)
    game = util.loadpgn(args.PGNFILE) 
    game.proba = 1
    fens = {} # visited

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

        fen = gn.board().fen()
        try:
            moves, movesum, opening = (mydb if myturn(gn) else db).ask(fen)
        except:
            db.end()
            mydb.end()
            assert False, 'sending requests too fast probably'


        fens[fen]=1
        
        #print()
        #print(gn.ply())
        print(gn.board().unicode())
        print ("proba:",gn.__dict__.get("proba","no proba"))
        if gn.ply() < args.MINPLY:
            if myturn(gn):
                for child in gn.variations:
                    child.proba = gn.proba
            else:
                for move in moves:
                    mov = gn.board().push_san(move['san'])
                    if gn.has_variation(mov):
                        gn.variation(mov).proba =  (bunseki.util.sumdi(move) / movesum) * gn.proba

        elif myturn(gn):
            if not gn.variations:
                best_san = util.find_best(moves, gn.ply())

                if args.MYMOVE=='most_frequent':
                    mov = gn.board().push_san(moves[0]['san'])
                    child = gn.add_variation(mov)
                    if best_san != moves[0]['san']:
                        child.comment = f"better: {best_san}"


                elif args.MYMOVE=='best':
                    mov = gn.board().push_san(best_san)
                    child = gn.add_variation(mov)
                    if best_san != moves[0]['san']:
                        child.comment = f"most frequent: {moves[0]['san']}"


                elif args.MYMOVE == 'terminate':
                    if best_san == moves[0]['san']:
                        mov = gn.board().push_san(best_san)
                        child = gn.add_variation(mov)
                    else:
                        gn.comment = f"terminated:{gn.proba*100:.1f}"

                else:
                    assert False

            for child in gn.variations:
                child.proba = gn.proba
        else:
            for move in moves: 
                p= (bunseki.util.sumdi(move) / movesum) * gn.proba
                mov = gn.board().push_san(move['san']) 
                print( '\t',move['san'],int(p*100))
                if p > (args.UTILITYCUT/100):
                    if not  gn.has_variation(mov):
                        gn.add_variation(mov)
                        print("  addvariation", move['san'])
                if gn.has_variation(mov):
                    gn.variation(mov).proba = p


        return gn.variations

    nodelist =  [game]

    while nodelist: 
        node = nodelist.pop()
        if node.board().fen() in fens:
            continue
        else:
            nodelist+=visit(node)


    db.end()
    mydb.end()
    print(game)


if __name__ == '__main__':
    main()
