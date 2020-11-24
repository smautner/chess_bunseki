

# what is this

You have a chess repertoire pgn file and want to know where it could be improved.
This scripts checks your oponents responses against the most played moves
on the lichess database.


# usage
```
pip install bunseki


# whites perspective, missing moves musst have been played at least 500 times
# utility is the probability of seeing the top opponent move
# we sort by that, cutoff is defined by -q
bunseki -w 1  -i lichessstudy_white.pgn -m 500 -q .5

# to check against lichess user database instead of the masters, e.g.:
-d 1  -s 1600 1800 -t blitz rapid
```

# example

```
possition frequency:35.68 utility:6.15 <- possition proability and utility of learning a new move
♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖            <- colors conveniently inverted for terminal usage
♙ ♙ ♙ ♙   ♙ ♙ ♙

        ♙
        ♟
          ♞
♟ ♟ ♟ ♟   ♟ ♟ ♟
♜ ♞ ♝ ♛ ♚ ♝   ♜
        Nc6     6235325(66)     OK [50, 4, 44]
        d6      1619060(17)     !! [52, 4, 42] <- this move is missing in the db
        Nf6     869610(9)       OK [49, 4, 45]

1. e4 e5 2. Nf3 *
rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2
https://lichess.org/analysis/rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R_b_KQkq_-_1_2
```



# strange stuff

* i would have liked to use UCI notation to communicate between python-chess and lichess
but they use different notation for castles.

* python-chess requires python >= 3.7
