## Secret Notes and Secret Notes 2
This challenge had two flags.

### Description 1
Category: Miscellaneous  
Difficulty: Medium
```
YASCNSS (Yet another secure cloud notes storage solution).

Hint: pyc

Challenge running at https://notes-server-m8tv5txzzohwiznk.web.ctfcompetition.com/

    NotesApp.apk 
```
### Description 2
Category: Miscellaneous  
Difficulty: Medium
```
There is a DIFFerent flag, can you find it?
```

### Exploration
Visiting `https://notes-server-m8tv5txzzohwiznk.web.ctfcompetition.com`, we are greeted with a page asking us to register an account.
```html
<html>
    <head>
        <link rel='stylesheet' href='/static/main.css'>
        <script src='/static/script.js'></script>
    </head>
    <body>
        <div class='title'>Welcome to MemoEyes Backup</div>
        <div class='main'>
            Create a new backup account here
        </div>
        <div class='user-create'>
            <input type='text' id='username' placeholder='Username'></input>
            <button class='submit' id='register'>Register</input>
        </div>
    </body>
</html>
```

Decompiling NotesApp.apk with [https://github.com/skylot/jadx/releases](jadx) reveals that there are two URLs of interest on the server:
- `GET /register`, which sets a cookie and is the registration page
- `GET /private`, which requires a cookie and retrieves a saved SQLite db
- `POST /private`, which requires a cookie and replaces the SQLite db

### index.pyc
We note the hint is `Hint: pyc` - presumably `/register` and/or `/private` is served by a Python script and there is a way to get the .pyc files.
If we look at the HTTP headers for the page we get the name of the .py file:
```
HTTP/1.1 200 OK
X-Served-By: index.py
...
```

Fetching `https://notes-server-m8tv5txzzohwiznk.web.ctfcompetition.com/index.pyc` works! (and fetching `index.py` doesn't).
We can decompile `index.pyc` using `uncompyle6` (`pip install uncompyle`).
`index.py` reveals a username of interest:
```python
...
locked_id = '436f7267316c3076657239393c332121'
...
```
We'd like to get the `/private` db of `436f7267316c3076657239393c332121` / `Corg1l0ver99<3!!`.

### Weak crypto
Trying to register `Corg1l0ver99<3!!` produces the message `Error: User already Exists`.  
Registering with a really long username produces `Error: Limit Username to 32 Characters`.
Registering a username sets an `auth` cookie - `fsgds3` produces the cookie `667367647333-a49c3a8ee8b5b569`.

The first part of the cookie is obviously the username in hex and the second part is presumably a function of the username - having another look at `index.py` confirms this.

Experimenting with long usernames, we see that the hash is really weak for the 17th to 32nd characters of the username:
```
admin                       a 61646d696e202020202020202020202020202020202020202020202061  aa0b53e6ef715af
admin                       b 61646d696e202020202020202020202020202020202020202020202062  aa0b53e6df715af

admin            a            61646d696e202020202020202020202020612020202020202020202020  ae1b53e2ff715af
admin           a             61646d696e202020202020202020202061202020202020202020202020 4ba0b53e2ff715af

bbbbbbbbbbbbbbbbbb 626262626262626262626262626262626262 150d03815e38f9c6
bbbbbbbbbbbbbbbb   62626262626262626262626262626262     776f03815e38f9c6
Corg1l0ver99<3!!bb 436f7267316c3076657239393c3321216262 50857228f277ba31
Corg1l0ver99<3!!   436f7267316c3076657239393c332121     ????????????????
```
Xoring `50857228f277ba31` with `6262000000000000` gives `32e77228f277ba31` - the hash for `Corg1l0ver99<3!!`.

### Flag 1
We can now fetch the `/private` database of `Corg1l0ver99<3!!`.
```
notcake@notcake:~/googlectf$ curl "https://notes-server-m8tv5txzzohwiznk.web.ctfcompetition.com/private" -H "Cookie: auth=436f7267316c3076657239393c332121-32e77228f277ba31"
U1FMaXRlIGZvcm1hdCAzABAAAQEAQCAgAAABewAAAAsAAAAAAAAAAAAAABAAAAAEAAAAAAAAAAkA
AAABAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAF7AC3mAg0PowAHDZgAD6cPHQ94
...
notcake@notcake:~/googlectf$ curl "https://notes-server-m8tv5txzzohwiznk.web.ctfcompetition.com/private" -H "Cookie: auth=436f7267316c3076657239393c332121-32e77228f277ba31" | base64 -d - | strings | grep -i CTF
Qctf{with_crypt0_d0nt_ro11_with_it}
ctf{puZZ1e_C
```
And this gives us the first flag: `ctf{with_crypt0_d0nt_ro11_with_it}`

(The flag was actually stored in the `VALUE` column of a table named `FLAG` in the SQLite database.)

### Flag 2
There are 6 tables in the SQLite database: `Diff`, `DiffSet`, `FLAG`, `NoteSet`, `Notes` and `android_metadata`.  
Under `NoteSet` and `DiffSet` there is a note called `flag.txt` - and the flag we want is probably somewhere in that note's history, represented as diffs.  
`DiffSet` tells us that `DiffSet`s 36 to 74 inclusive correspond to `flag.txt`.  
`Diff` has 5 columns: `(int ID, bool Insertion, int IDX, string Diff, int DiffSet)`.

Luckily `NotesApp.apk` contains code to handle diffs and we can use it to get the flag at the end of DiffSet 66: `ctf{puZZ1e_As_old_as_tIme}`

Alternatively, piecing together `strings` output for the SQLite database works:
```
      f{puZZ1e_As_old_as_TheD
(nds the uZZ1e_As_old_as_The finaleD
    ctf{puZZ1e_C
  thusf{puZZ1e_As_oC
                         tIme}C
```
