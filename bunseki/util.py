# based on https://github.com/permutationlock/merge-pgn
import chess.pgn
import sys
import chess

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
        g= g.add_variation(chess.Move.from_uci(move))

    exporter = chess.pgn.StringExporter(headers=False, variations=True, comments=True)
    return g.game().accept(exporter)
