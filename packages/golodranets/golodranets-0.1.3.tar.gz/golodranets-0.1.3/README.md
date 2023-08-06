# Official Python GOLOS Library

`golodranets` is the GOLOS library for Python which was forked from official STEEM library for Python. It comes with a BIP38 encrypted wallet.

The main differences from the `steem-python`:
* directed to work with GOLOS blockchain
* websocket support
* convert Cyrillic to Latin for tags and categories
* Golos assets - `STEEM` -> `GOLOS`, `SBD` -> `GBG`, `VESTS` -> `GESTS`
* renamed modules - `steem` -> `golos`, `steemdata` -> `golosdata`
* for `Post` instance added two fields - `score_trending` and `score_hot`. This fields may be helpful if you want to sort your saved posts like `get_discussions_by_trending` and `get_discussions_by_trending` methods do. `reblogged_by` field is also filled now
* for `Account` instance methods `get_followers` and `get_following` were improved - now it takes `limit` and `offset` parameters

GOLOS HF 17 is supported.

This library currently works on Python 3.5 and 3.6.

# Installation

With pip:

```
pip3 install golodranets
```

From Source:

```
git clone https://github.com/steepshot/golodranets.git
cd golodranets
python3 setup.py install
```

## Homebrew Build Prereqs

If you're on a mac, you may need to do the following first:

```
brew install openssl
export CFLAGS="-I$(brew --prefix openssl)/include $CFLAGS"
export LDFLAGS="-L$(brew --prefix openssl)/lib $LDFLAGS"
```

# Documentation

Unfortunately we do not have documentation for Golodranets yet, but documentation from steem-python may help you -  **http://steem.readthedocs.io**

# Usage examples

#### Get trending posts

``` python
from golos import Steem

steem = Steem(['wss://ws.golos.io'])
posts = steem.get_posts(limit=20, sort='trending')
for post in posts:
    print(post.identifier)
```

#### Get followers for user
``` python
from golos import Steem
from golos.account import Account
from golos.instance import set_shared_steemd_instance

steem = Steem(['wss://ws.golos.io'])
set_shared_steemd_instance(steem)
account = Account('golos')
followers = account.get_followers(limit=10)
for follower in followers:
    print(follower)
```

#### Create post
``` python
from golos import Steem

steem = Steem(['wss://ws.golos.io'])
username = 'your account username here'
posting_key = 'your private posting key here'
steem.commit.wallet.setKeys(posting_key)

# this method returns the transaction broadcasted to blockchain, you can jst omit it if not needed
steem.commit.post(
        title='Test post from Golodranets',
        body='This post created in Golodranets library!',
        author=username,
        tags=['test', 'spam'],
        beneficiaries=[
            {'account': 'golos', 'weight': 1000},  # beneficiaries support!
        ],
        self_vote=True
    )
```

# Tests

Some tests are included.  They can be run via:

* `python setup.py test`

# Notice

This library is *under development*.  Beware.
