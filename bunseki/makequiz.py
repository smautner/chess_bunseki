
import pprint  as p 
from bunseki import util
import basics as ba


#########
#    replaces all sqares that are empty with an square in foreground
##########
def decorate_unicode(b,color): 

    boardlines = [] 
    for i,line  in enumerate(b.split('\n')):
        newline = [ putthis(i,e,symbol)  for e, symbol in enumerate(line)  ]
        boardlines.append(''.join(newline))

    if color == 'black':
        boardlines.reverse()
        boardlines = [ s[::-1] for s in boardlines]
    board = "\n".join(boardlines)
    print(board)
    return board

def putthis(bline,sq,symbol):
    sq_b ="▢"
    sq_b= '□'
    sq_w ='■'

    #sq_b=' '

    if symbol != 'x':
        return symbol
    else:
        ret =  sq_b
        if ((bline%2) + (sq%4 == 0))%2:
            ret = sq_w 
    return ret

################
# REALCOLORIZE 
############### 

def decorate_unicode_2(b,color): 
    
    board = b.split('\n')
    if color == 'black':
        board.reverse()
        board = [ s[::-1] for s in board]

    board = [transformline(i+(color=='black'),e) for i,e in enumerate(board)]

    board = "\n".join(board)
    print(board)
    print()
    return board

def transformline(i,bline):

    cend =  '\x1b[0m'
    rline = ''
    for idd,sym in enumerate(bline.split()):
        if sym == 'x': 
            sym = ' '

        if (idd+i) % 2:
            item = '\x1b[1;30;47m'+sym+" "+cend
        else:
            item = '\x1b[1;30;43m'+sym+' '+cend

        rline += item

    rline += cend
    return rline

###############
# QUIZ MAKER
####################
        

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
            b = gn.board().unicode(invert_color=True, empty_square='x')
            b = decorate_unicode_2(b,color= color)
            data[hash(gn.board().fen())] = {'q':b, 'a':mv, 'sort':sort}
            sort+=1

        nodes+=n.variations

    #p.pprint(data)
    ba.jdumpfile(data,outdeck)

