

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
```

# example


![''](https://raw.githubusercontent.com/smautner/chess_bunseki/master/output.png)'

* we see move frequency, included moves are marked with 'OK' and win distribution in [white draw black]. 
* the example repertoire has only the main moves, which cover less than 60% of moves



# strange stuff 

* i would have liked to use UCI notation to communicate between python-chess and lichess
but they use different notation for castles.

* python-chess requires python > 3.7
