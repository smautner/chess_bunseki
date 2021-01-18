# based on https://github.com/permutationlock/merge-pgn
import chess.pgn
import sys
import chess
import os 
import pickle
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


def getimportance(node):
    res = 1
    while node.parent:
        res*= node.proba
        node = node.parent
    return res


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


'''
def find_lemons(moves, ply):
    # checks if the most popular move is not the best in win percentage
    # (compared to a move at least 20% played)

    us = 'black'
    them = 'white'

    if (ply+1) % 2:
        us, them = them,us
    score_mv = lambda m: (m[us]-m[them]) / sumdi(m)
    score = score_mv(moves[0])
    sum = max(sumdi(moves[0]), 100)
    if Z:=[ e for e in moves[1:] if sumdi(e) > sum*.2  and score_mv(e) > score  ]:
        return "there might be a better move"+str([ z['san'] for z in Z])
    return ''


def find_best(moves, ply):
    # returns the best move, most played or ''

    us = 'black'
    them = 'white'
    if (ply + 1) % 2:
        us, them = them, us
    sum = max(sumdi(moves[0]), 100)
    score_mv = lambda m: (m[us] - m[them]) / sumdi(m) if sumdi(m) > .2*sum else -99999
    best = max(moves, key=score_mv)
    return best['san'], '' if best['san'] == moves[0]['san'] else f"most played is {moves[0]['san']}"
'''

def find_best(moves, ply):
    # returns the best move, most played or ''

    us = 'black'
    them = 'white'
    if (ply + 1) % 2:
        us, them = them, us
    sum = max(sumdi(moves[0]), 100)
    score_mv = lambda m: (m[us] - m[them]) / sumdi(m) if sumdi(m) > .2*sum else -99999
    best = max(moves, key=score_mv)
    return best['san']


def sumdi(di):
    return di['black']+di['white']+di['draws']