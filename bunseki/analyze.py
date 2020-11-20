import chess.pgn
import bunseki.util as util
import bunseki.asklichess as ali

import argparse

parser = argparse.ArgumentParser() 
parser.add_argument('-w','--white',dest='COLOR', help= 'is the repertoire for white', type=int,choices=[0,1], required=True)
parser.add_argument('-o','--pgnfile',dest='PGNFILE', help= 'path to pgn file to parse', type=str, required=True)
parser.add_argument('-m','--minmoves',dest='MINMOV', help= 'suggestions musst have been played this many times', type=int, default = 300)
parser.add_argument('-c','--coverage',dest='MINPERC', help= 'replies musst cover this percentage of moves', type=int, default = 60)

parser.add_argument('-d','--database',dest='DATABASE', help= '0 = master database 1 = lichess', type=int, default = 0)
parser.add_argument('-s','--lichess_strength',dest='STRENGTH', help= 'select playing strength for lichess db', type=int,nargs='+', default = [1600,1800])
parser.add_argument('-f','--lichess_format',dest='TIMECTL', help= 'select time control for lichess db', type=float,nargs='+', default = ['blitz','rapid'])


def main(): 
    args = parser.parse_args()
    repo = open(args.PGNFILE)
    games = []
    while True:
        stuff = chess.pgn.read_game(repo)
        if not stuff:
            break
        games.append(stuff)

    game = util.merge(games)



    def visit(gn):
        if gn.ply() % 2  == args.COLOR:  # do we need to analyze this?
            enemy_moves = [str(v.san()) for v in  gn.variations]
            #enemy_moves = [str(v.move) for v in  gn.variations]
            if  enemy_moves:
                # lets do a lookup 
                fen = gn.board().fen()
                res, movesum = ali.ask(fen,enemy_moves, minmov= args.MINMOV, minperc=args.MINPERC, args=args)
                # outout
                if res: 
                    #
                    if args.COLOR ==1:
                        print(gn.board().unicode(empty_square=' ',invert_color=True))
                    else:
                        print(gn.board().transform(chess.flip_vertical).transform(chess.flip_horizontal).unicode(empty_square=' ',invert_color=True))
                    print(res)
                    print()
                    print(util.pgn(gn))
                    print(gn.board().fen())
                    print(f"https://lichess.org/analysis/{fen.replace(' ','_')}")
                    print("\n\n\n")
                if movesum < args.MINMOV*2:
                    return

        for child in gn.variations:
            visit(child)


    for g in game.variations:
        visit(g)



