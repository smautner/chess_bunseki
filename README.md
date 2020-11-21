

# what is this

You have a chess repertoire pgn file and want to know where it could be improved.
This scripts checks your oponents responses against the most played moves
on the lichess database.


# usage 
```
pip install bunseki


# whites perspective, missing moves musst have been played at least 500 times 
# make sure my repertoire covers 60% of opponents responses
bunseki  -o lichessstudy_white.pgn -w 1 -m 500 -c 60 

# to check against lichess user database instead of the masters, e.g.:
-d 1  -s 1600 1800 -t blitz rapid 
```

# example

```
possition reached: 60.53     <- accoding to choosen database and repertoire file                                                                                
♜ ♞ ♝ ♚ ♛ ♝ ♞ ♜        
♟ ♟ ♟   ♟ ♟ ♟ ♟                  
                             
      ♟                                  
          ♙                                               
                                                                                                          
♙ ♙ ♙ ♙ ♙   ♙ ♙                      
♖ ♘ ♗ ♔ ♕ ♗ ♘ ♖       
        Nf3     5890406(58)     OK [47, 4, 47]     
        Bc4     879736(8)       !! [43, 4, 52]   <- this move is not in the repertoire, but it seems to score well for black 
        Nc3     792600(7)       OK [49, 4, 45]                                                            
                                                                                                          
1. e4 c5 *                                    
rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2                           
https://lichess.org/analysis/rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR_w_KQkq_-_0_2   <- analysis link
```



# strange stuff 

* i would have liked to use UCI notation to communicate between python-chess and lichess
but they use different notation for castles.

* python-chess requires python > 3.7
