
##############
# mostly contains utils concerning the pychess module
##################

# based on https://github.com/permutationlock/merge-pgn
import chess.pgn
import sys
import chess
import os 
import pickle

from bunseki.tree import sumdi
def merge(games):
    master_node = chess.pgn.Game()

    mlist = []
    for game in games:
        mlist.extend(game.variations)

    variations = [(master_node, mlist)]
    done = False

    while not done:
        newvars = []
        done = True
        for vnode, nodes in variations:
            newmoves = {}
            for node in nodes:
                if node.move is None:
                    continue
                elif node.move not in list(newmoves):
                    nvnode = vnode.add_variation(node.move)
                    if len(node.variations) > 0:
                        done = False
                    newvars.append((nvnode, node.variations))
                    newmoves[node.move] = len(newvars) - 1
                else:
                    nvnode, nlist = newvars[newmoves[node.move]]
                    if len(node.variations) > 0:
                        done = False
                    nlist.extend(node.variations)
                    newvars[newmoves[node.move]] = (nvnode, nlist)
        variations = newvars

    return master_node

def loadpgn(filename, maxread=999):
    assert maxread == 999, 'not implemented'
    repo = open(filename)
    games = []
    while True:
        stuff = chess.pgn.read_game(repo)
        if not stuff:
            break
        games.append(stuff)
    game = merge(games)
    return game


def history(node):
    r=[]
    while node.parent:
        r.append(str(node.move))
        node = node.parent
    r.reverse()
    return r

def pgn(node):
    g = chess.pgn.Game()
    for move in history(node):
        g = g.add_variation(chess.Move.from_uci(move))
    exporter = chess.pgn.StringExporter(headers=False, variations=True, comments=True)
    return g.game().accept(exporter)



def find_best(moves, ply):
    # returns the best move, most played or ''
    us = 'black'
    them = 'white'
    if (ply + 1) % 2:
        us, them = them, us
    min_played = max(sumdi(moves[0])*.15, 100)
    score_mv = lambda m: (m[us] - m[them]) / sumdi(m) if sumdi(m) > min_played else -99999
    best = max(moves, key=score_mv)
    return best['san']


def illegal(san,board):
    try:
        board.push_san(san)
    except:
        return True
    return False

    
def split_ply(game,ply): 
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

def mkgame(game,r):
    history = util.history(r)
    game = chess.pgn.Game()
    node = game
    print(history[:-1])
    for move in history[:-1]: 
        node = node.add_variation(chess.Move.from_uci(move))
    node.variations = [r]
        
    return game

#####################
# this is just the cacher, if i  get more generic utils there will be a new file
#####################
class cacher():

    def __init__(self,cachename): 
        self.cachename = f".{cachename}"
        if os.path.exists(self.cachename): 
            self.cache = pickle.load( open( self.cachename, "rb" ) )
        else:
            self.cache={}

    def write(self):
        pickle.dump( self.cache, open( self.cachename, "wb" ) )

    def call(self,f, key): 
        if key in self.cache:
            return self.cache[key]
        else:
            r = f()
            self.cache[key] = r 
        return r



