
## Anonymous exchange
### Description
Category: Miscellaneous  
Difficulty: Medium
```
I've bought some bitcoins with my credit cards, and some of them attracted attention, but I don't know which ones. Could you find out?

Challenge running at anon.ctfcompetition.com:1337
```

### Exploration
```
notcake@notcake:~/googlectf$ nc anon.ctfcompetition.com 1337
Hey. Could you tell me if my cards ccard0x1 through ccard0x40 have attracted the wrong type of attention? Flagged cards are displayed in their dumps, and their encryption is deterministic. I seem to have the wrong encoding on my terminal, so I'll need help there.
I'll patch you into a management interface in a few seconds.


Welcome to our telnet dogecoin exchange !.
We've currently frozen most of the operations pending an investigation into potential credit card fraud with law enforcement.
 - NEWACC to create an account.
 - NEWCARD to create a test credit card.
 - ASSOC <cardx> <accounty> to associate cardx to accounty.
 - BACKUP to generate a anonymized encrypted jsonified maybe-emojified backup.
newacc
OK: Account uaccount0x1 created.
newacc
OK: Account uaccount0x2 created.
newcard
OK: Card ucard0x1 created.
newcard
OK: Card ucard0x2 created.
assoc ccard0x1 uaccount0x1
OK: Card ccard0x1 associated with account uaccount0x1.
backup
[{"cards":[],"account":"062a497ba8d04fbe"},{"cards":[{"card":"f5b81c95a8b2e62d"}],"account":"2a5c89119df2f57b"},{"cards":[],"account":"a381de49526c8f06"},{"account":"893e817bc94682f8","cards":[]},{"cards":[{"flagged":"1","card":"724593c30ca6b45f"}],"account":"5495915d1e167ea6"},{"account":"f6023cb0604c4eb8","cards":[{"card":"af2d6a95ed202e99"}]},{"c...

So, which cards are burnt?
Answer with a string of zeroes and ones, no spaces.
```

- Connecting to `anon.ctfcompetition.com:1337` creates a different instance of the problem each time
- We need to identify which of cards `ccard0x1` to `ccard0x40` are `flagged` in the dump and submit the bitstring it forms
- Card and account names are hashed in the dump
- We can only dump once
- New accounts we create are named `uaccount0x%x`
- New cards we create are named `ucard0x%x`
- We can link accounts we create to the cards of interest, `ccard0x%x`

Card and account associations form a graph.  
Since we don't get the card and account names in the dump, we need some way to identify cards and accounts from the graph structure alone.

### Idea 1
- Create 0x40 accounts, `uaccount0x1` to `uaccount0x40`
- Create 10 cards
- Link each of those accounts to all 10 cards so that we can identify them by their number of cards
- Link account `uaccount0xn` to cards `ccard0x1` to `ccard0xn`

This doesn't work unfortunately:
```
assoc ucard0x1 uaccount0x1
OK: Card ucard0x1 associated with account uaccount0x1.
assoc ucard0x2 uaccount0x1
OK: Card ucard0x2 associated with account uaccount0x1.
assoc ucard0x3 uaccount0x1
OK: Card ucard0x3 associated with account uaccount0x1.
assoc ucard0x4 uaccount0x1
KO: Too many cards used by this account.
```
```
assoc ucard0x1 uaccount0x1
OK: Card ucard0x1 associated with account uaccount0x1.
assoc ucard0x1 uaccount0x2
OK: Card ucard0x1 associated with account uaccount0x2.
assoc ucard0x1 uaccount0x3
OK: Card ucard0x1 associated with account uaccount0x3.
assoc ucard0x1 uaccount0x4
KO: Too many accounts already use this card.
```

It turned out there was a limit of 3 cards per account and 3 accounts per card so another idea was needed.

### Idea 2
Our markers have to have a maximum of 3 edges.

#### Card-1 and account-1 markers
```
A   A    C   C
 \ /      \ /
  C        A
  |        |
  ?        ?
```
This is easily identifiable (2 edges to nodes with 1 edge).

#### Card-2 and account-2 markers
The previous markers aren't unique enough so we nest them further.  
```
C   C C   C    A   A A   A
 \ /   \ /      \ /   \ /
  A     A        C     C
   \   /          \   /
    \ /            \ /
     C              A
     |              |
     ?              ?
```

#### Card sequence
We need to be able to identify `ccard0x1`, so we attach an account-2 marker on it.  
We also need a way to get the next card in the series, so we join all the cards together with an account "backbone" that can be identified using card-2 markers.
```
A   A A   A
 \ /   \ /
  C     C
   \   /
    \ /        C
     A        /
    /        A
ccard0x1    / \
    \      /   C
     A----C
    /      \   C
ccard0x2    \ /
    \        A
     A-- ...  \
    /          C
ccard0x3
    \
    ...
    /
ccard0x3f
    \
     A-- <card-2 marker>
    /
ccard0x40
```

```lua
local head = f.keys(accounts):filter(is_account_sparkler_2)[1]
local card, account = nil, head
local s = ""
for i = 1, 0x40 do
	card, account = next_link(account, card)
	s = s .. (cards[card].flagged and "1" or "0")
end
print(s)
```

### Solution
Using the second idea above worked:
```
So, which cards are burnt?
Answer with a string of zeroes and ones, no spaces.
1001011111110000100000101011011101000100110000010010001100001111
CTF{e0c70d766a99-no-emojis-in-flags-they-said-T_T}
```
