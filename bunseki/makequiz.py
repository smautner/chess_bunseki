
import pprint  as p 
from bunseki import util
import basics as ba

def decorate_unicode(board): 
    print(b)
    print()
    for e in b.split('\n'):
        print(list(e))

def add_to_data(gn, color): 
    # is it our turn? 
    # if so data[fen] = {q:q, a:a}
    if gn.ply() % 2 == (color=='black'): 
        if gn.variations:
            mv = gn.variations[0].move.uci()
            return gn, mv
    return False,False


def makequiz(color,inpgn, outdeck):
    game = util.loadpgn(inpgn)
    nodes = [game]
    data = {} # fen:{q:board, a:variation}
    sort = 0 
    while nodes: 
        n = nodes.pop()
        gn,mv = add_to_data(n, color)
        if gn:
            b = gn.board().unicode(invert_color=True)
            data[hash(gn.board().fen())] = {'q':b, 'a':mv, 'sort':sort}
            sort+=1

        nodes+=n.variations

    p.pprint(data)
    ba.jdumpfile(data,outdeck)

