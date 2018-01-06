# BTC Address Monitor

This is a simple proof of concept BTC address monitoring application. It should be provided with a watchlist of 
addresses. The application will then monitor transactions on the blockchain and watch for deposits into the addresses
that are contained in the watch list.

### Watchlist format example

```json
{"addresses": ["n2unYMeXXpadkocVka1rPzGLpJ6PwLBgRy", "2N8jrpNnTzrYJMU4cLfmQudbRemyLyQKWnC"]}
```

### Application usage

#### Start bitcoind

The application requires a connection to `bitcoind`. An example of starting bitcoind is as follows: 
`bitcoind -testnet -datadir=testnet -server -rpcuser=marcus -rpcpassword=test -txindex=1`. This
will run bitcoind on 127.0.0.1 and port 18332.

#### Running the application

