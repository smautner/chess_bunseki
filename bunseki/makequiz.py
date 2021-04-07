

import util
import basics as ba
game = util.loadpgn("garbo.pgn")
data = {} # fen:{q:board, a:variation}
color = 'white'
sort = 0 

def decorate_unicode(board): 
    print(b)
    print()
    for e in b.split('\n'):
        print(list(e))

def add_to_data(gn): 
    global sort
    # is it our turn? 
    # if so data[fen] = {q:q, a:a}
    if gn.ply() % 2 == (color=='black'): 
        b = gn.board().unicode(invert_color=True)
        if gn.variations:
            mv = gn.variations[0].move.uci()
            data [hash(gn.board().fen())] = {'q':b, 'a':mv, 'sort':sort}
            sort+=1



nodes = [game]
while nodes: 
    n = nodes.pop()
    add_to_data(n)
    nodes+=n.variations

import pprint  as p 
p.pprint(data)
ba.jdumpfile(data,"/home/ikea/garbo.deck")

