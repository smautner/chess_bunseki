import chess.pgn
import bunseki.util as util
import bunseki.asklichess as ali
from collections import defaultdict 
import argparse

parser = argparse.ArgumentParser() 
parser.add_argument('-w','--white',dest='COLOR', help= 'is the repertoire for white', type=int,choices=[0,1], required=True)
parser.add_argument('-o','--pgnfile',dest='PGNFILE', help= 'path to pgn file to parse', type=str, required=True)
parser.add_argument('-m','--minmoves',dest='MINMOV', help= 'suggestions musst have been played this many times', type=int, default = 300)
parser.add_argument('-c','--coverage',dest='MINPERC', help= 'replies musst cover this percentage of moves', type=int, default = 60)

parser.add_argument('-d','--database',dest='DATABASE', help= '0 = master database 1 = lichess', type=int, default = 0)
parser.add_argument('-s','--lichess_strength',dest='STRENGTH', help= 'select playing strength for lichess db', type=int,nargs='+', default = [1600,1800])
parser.add_argument('-t','--lichess_format',dest='TIMECTL', help= 'select time control for lichess db', type=str,nargs='+', default = ['blitz','rapid'])


def main(): 
    args = parser.parse_args()
    hashname = hash((args.DATABASE, tuple(args.STRENGTH), tuple( args.TIMECTL)))
        
    h = util.cacher(hashname)

    ####
    # collect the game in a huge tree
    # we could also just make a list of fens, but the tree makes it easy 
    # to cut a whole branch when there are too few games
    ####
    repo = open(args.PGNFILE)
    games = []
    while True:
        stuff = chess.pgn.read_game(repo)
        if not stuff:
            break
        games.append(stuff)
    game = util.merge(games)


    ###############
    # for fens get the game-node and lichess-db answer
    ##############
    fens = defaultdict(list)
    def visit(gn):
        if gn.ply() % 2  == args.COLOR:  # do we need to analyze this?
            enemy_moves = [str(v.san()) for v in  gn.variations] # UCI has redundant codes :(
            if  enemy_moves:
                # lets do a lookup 
                fen = gn.board().fen()
                if fen in fens:
                    moves,movesum = fens[fen][0][:2]

                moves, movesum = h.call( lambda: ali.ask(fen,args),fen)


                fens[fen].append([moves,movesum,gn]) 
                if movesum < args.MINMOV*2:
                    return

        for child in gn.variations:
            visit(child)
    for g in game.variations:
        visit(g)

    h.write()

    #########################
    # so, now we can evaluate what we have... 
    ##########################

    # sort by node weight
    keys = list(fens.keys())
    keys.sort(key = lambda x: fens[x][0][1], reverse = True)
    
    for k in keys: 
        mo_s_gn_li  = fens[k]
        # all the moves from all game nodes that share the fen
        enemy_moves = [str(v.san()) for mosgn in mo_s_gn_li  for v in  mosgn[2].variations]
        
        res = ali.analyse(mo_s_gn_li[0][0],enemy_moves, minmov=args.MINMOV, minperc= args.MINPERC/100)
        gn = mo_s_gn_li[0][2]
        if res: 
            #
            if args.COLOR ==1:
                print(gn.board().unicode(empty_square=' ',invert_color=True))
            else:
                print(gn.board().transform(chess.flip_vertical).transform(chess.flip_horizontal).unicode(empty_square=' ',invert_color=True))
            print(res)
            print()
            for mosgn in mo_s_gn_li:
                print(util.pgn(mosgn[2]))
            print(gn.board().fen())
            print(f"https://lichess.org/analysis/{k.replace(' ','_')}")
            print("\n\n\n")
