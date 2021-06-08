import chess.pgn
from copy import deepcopy
from types import SimpleNamespace
import chess
import bunseki.util
import bunseki.util as util
import bunseki.tree as tree
from collections import defaultdict 
import dirtyopts

docs = '''
--color str white assert white black
--pgn str 
--cut int 1000
--minply int 0

--dbus str+ 2200 2500 blitz rapid classical
--dbthem str+ 2200 2500 blitz rapid classical
'''




lalala = 65

def main(): 
    args = dirtyopts.parse(docs)
    game = util.loadpgn(args.pgn) #if args.pgn else chess.pgn.Game() 
    fens = {} # known gamenodes

    def getjmp():
        global lalala
        r = f"#{chr(lalala)}#"
        lalala +=1
        return r
    
    mydb = tree.lichess(args.dbus)
    if args.dbus == args.dbthem:
        db = mydb
    else:
        db = tree.lichess2(args.dbthem)
        

    def myturn(gn):
        return gn.ply()% 2 != (args.color == 'white')  

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


        skip =  gn.ply() < args.minply

        if myturn(gn) and not skip:
                
            best_san = util.find_best(moves, gn.ply())
            best_san_valid = bunseki.util.sumdi(moves[0]) >= 50 # best move has been played at least 50x
            mov = gn.board().push_san(best_san)


            if gn.variations:
                if not gn.has_variation(mov) and best_san_valid:
                    gn.variations[0].comment+=f" better:{best_san}"

            elif best_san_valid:
                gn.add_variation(mov)


        elif not skip:
            second_border = tree.sumdi(moves[0])*.2
            for move in moves: 
                freq = tree.sumdi(move)
                if freq > args.cut and freq > second_border: 
                    mov = gn.board().push_san(move['san']) 
                    if not gn.has_variation(mov):
                        # move is not yet in the list and noteworthy
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
    
    




if __name__ == '__main__':
    main()
