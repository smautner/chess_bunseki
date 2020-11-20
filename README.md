

# what is this

You have a chess repertoire pgn file and want to know where it could be improved.
This scripts checks your oponents responses against the most played moves
on the lichess database.


# usage 
```
pip install bunseki


# whites perspective, ignores moves played < 500x, make sure my repertoire covers 60% of opponents responses
bunseki  -o example2.pgn -w 1 -m 500 -c 60  
```

# example


![''](https://raw.githubusercontent.com/smautner/chess_bunseki/master/output.png)'

* i have only the most played move in my repertoire and that doesnt cover 60% of moves in the database



# strange stuff 

i would have liked to use UCI notation to communicate between python-chess and lichess
but they use different notation for castles.
