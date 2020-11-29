import chess.pgn
import bunseki.util as util
import bunseki.asklichess as ali
from collections import defaultdict 
import argparse

parser = argparse.ArgumentParser() 
parser.add_argument('-w','--white',dest='COLOR', help= 'is the repertoire for white', type=int, choices=[0,1], required=True)
parser.add_argument('-i','--pgnfile',dest='PGNFILE', help= 'path to pgn file to parse', type=str, required=True)
parser.add_argument('-m','--minmoves',dest='MINMOV', help= 'suggestions musst have been played this many times', type=int, default = 500)
parser.add_argument('-u','--utilitycuy',dest='UTILITYCUT', help= 'cutoff based on utility..i.e. probability that the top move is on board', type=float, default = 0)

parser.add_argument('-d','--database',dest='DATABASE', help= '0 = master database 1 = lichess', type=int, default = 0)
parser.add_argument('-s','--lichess_strength',dest='STRENGTH', help= 'select playing strength for lichess db', type=int,nargs='+', default = [1600,1800])
parser.add_argument('-t','--lichess_format',dest='TIMECTL', help= 'select time control for lichess db', type=str,nargs='+', default = ['blitz','rapid'])


parser.add_argument('-a','--showallnodes',dest='PRINTALL', help= 'print all to nodes even if they pass the filter',action = "store_true")
parser.add_argument('-p','--minpercentage',dest='MINPERC', help= 'suggestions musst have been played this many times', type=int, default = 3)
parser.add_argument('-c','--coverage',dest='MINCOV', help= 'replies musst cover this percentage of moves', type=int, default = 100)
parser.add_argument('--maxparse',dest='MAXPARSE', help= 'my studies have a few outdated chapters that i put at the end', type=int, default = 100)


def proba_calculation(gn, moves, movesum):

    movcntdi = { m['san']:ali.sumdi(m)  for m in moves}
    for child in gn.variations: #  i could calculate the percentage of games that end up here...
        if movesum == 0: 
            child.proba = 0
        else:
            child.proba = movcntdi.get(child.san(),0)/ movesum


def main(): 
    args = parser.parse_args()
    db = ali.lichess(args)

    ####
    # collect the game in a huge tree
    # we could also just make a list of fens, but the tree makes it easy 
    # to cut a whole branch when there are too few games
    ####
    repo = open(args.PGNFILE)
    games = []
    while True:
        stuff = chess.pgn.read_game(repo)
        if not stuff or len(games)==args.MAXPARSE:
            break
        games.append(stuff)
    game = util.merge(games)

    fen = game.board().fen()
    moves, total_games, openingname = db.ask(fen)
    game.proba = 1
    game.openingname = openingname
    if args.COLOR ==0:
        proba_calculation(game, moves, total_games)

    ###############
    # for fens get the game-node and lichess-db answer
    ##############
    fens = defaultdict(list)
    def visit(gn):
        if gn.ply() % 2  == args.COLOR:  # do we need to analyze this?
            gn.proba = 1 
            enemy_moves = [str(v.san()) for v in  gn.variations] # UCI has redundant codes :(
            if  enemy_moves:
                # lets do a lookup 
                fen = gn.board().fen()
                if fen in fens:
                    moves,movesum = fens[fen][0][:2]

                moves, movesum, opening= db.ask(fen)

                # this blocck is for proba calculation
                proba_calculation(gn,moves,movesum) 
                gn.opening = opening

                fens[fen].append([moves,movesum,gn]) 
                if movesum < args.MINMOV*2:
                    return

        for child in gn.variations:
            visit(child)
    for g in game.variations:
        visit(g)

    db.end()

    #########################
    # so, now we can evaluate what we have... 
    ##########################

    # sort by node weight
    #keys = list(fens.keys())
    #keys.sort(key = lambda x: fens[x][0][1], reverse = True)



    bunsekitachi = []

    for k in fens.keys(): 
        mo_s_gn_li  = fens[k]
        # all the moves from all game nodes that share the fen
        enemy_moves = [str(v.san()) for mosgn in mo_s_gn_li  for v in  mosgn[2].variations]
        res,perc_miss = ali.analyse2(mo_s_gn_li[0][0],enemy_moves, 
                              minmov=args.MINMOV, 
                              target_share  = args.MINCOV/100,
                              minperc= args.MINPERC/100)
        bunsekitachi.append(bunseki( [e[2] for e in mo_s_gn_li ]  ,args.COLOR, res, perc_miss   ))

    bunsekitachi.sort(key = lambda x: x.frequency*x.perc_miss)

    for e in bunsekitachi: 
        if (e.perc_miss > 0 and e.utility > args.UTILITYCUT)  or args.PRINTALL:
            e.print()
        




class bunseki():
    def __init__(self,gn,color,res_str,perc_miss):
        self.gn = gn
        self.color= color
        self.moves=res_str
        self.perc_miss = perc_miss
        self.board = gn[0].board()
        self.frequency = sum(map( util.getimportance, self.gn))*100
        self.utility = self.frequency * self.perc_miss

    def print(self):
        print(f"possition frequency:{ self.frequency:.2f} utility:{self.utility:.2f}")
        op = self.gn[0].opening
        if op:
            print (f"{op['eco']} {op['name']} ")
        print ()


        if self.color ==1:
            print(self.board.unicode(empty_square=' ',invert_color=True))
        else:
            print(self.board.transform(chess.flip_vertical).transform(chess.flip_horizontal).unicode(empty_square=' ',invert_color=True))

        print (self.moves)
        print ()
            
        for node in self.gn:
            print(util.pgn(node))
        print(self.board.fen())
        print(f"https://lichess.org/analysis/{self.board.fen().replace(' ','_')}")
        #print( self.gn.get('opening',''))
        print("\n\n\n")

if __name__ == '__main__':
    main()
