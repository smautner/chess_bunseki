import chess.pgn
from types import SimpleNamespace
import bunseki.util as util
import bunseki.asklichess as ali
from collections import defaultdict 
import argparse



parser = argparse.ArgumentParser() 
parser.add_argument('-w','--white',dest='COLOR', help= 'is the repertoire for white', type=int, choices=[0,1], required=True)
parser.add_argument('-i','--pgnfile',dest='PGNFILE', help= 'path to pgn file to parse', type=str, required=True)
parser.add_argument('-u','--utilitycut',dest='UTILITYCUT', help= 'cutoff based on utility..i.e. probability that the top move is on board', type=float, default = 2)
parser.add_argument('-c','--mydb',dest='SHAREDB', help= 'database for my moves is masterdb, regardless of enemy', type=int, default = 1)
parser.add_argument('-d','--database',dest='DATABASE', help= '0 = master database 1 = lichess', type=int, default = 0)
parser.add_argument('-s','--lichess_strength',dest='STRENGTH', help= 'select playing strength for lichess db', type=int,nargs='+', default = [1600,1800])
parser.add_argument('-t','--lichess_format',dest='TIMECTL', help= 'select time control for lichess db', type=str,nargs='+', default = ['blitz','rapid'])


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
        print(gn.board().unicode())

        if myturn(gn):
            if not gn.variations: 
                mov = gn.board().push_san(moves[0]['san']) 
                gn.add_variation(mov)
            for child in gn.variations:
                child.proba = gn.proba
        else:
            for move in moves: 
                p= (ali.sumdi(move)/movesum)*gn.proba 
                mov = gn.board().push_san(move['san']) 
                if p > (args.UTILITYCUT/100):
                    if not  gn.has_variation(mov):
                        gn.add_variation(mov)
                        print("  addvariation", move['san'])
                if gn.has_variation(mov):
                    gn.variation(mov).proba = p
        return gn.variations

    nodelist =  [game]
    while nodelist: 
        node =nodelist.pop()
        if node.board().fen() in fens:
            continue
        else:
            nodelist+=visit(node)


    db.end()
    mydb.end()
    print(game)


if __name__ == '__main__':
    main()
