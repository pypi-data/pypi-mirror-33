# simplegitweb
----------------------

A Python git web server that base on dulwich lib.

## install
    python setup.py install
    or pip install simplegitweb
    then find and run bash script "simplegitweb/systemd/install_service.sh" install systemd service

## use
gitwebserver.py
```python
from simplegitweb import gitwebserver as gitweb
if __name__ == '__main__':
    gitweb.main()
```
simplegitweb.conf
```bash
[DEFAULT]
scanpath = /opt/simplegitweb/
listen_address = 127.0.0.5
port = 3000
```
    python gitwebserver.py --config simplegitweb.conf
Use browser to browse this [default address](http://127.0.0.5:3000) you can add your project.

## caddy proxy example
```bash
https://example.com {
    proxy / http://127.0.0.5:3000
    basicauth / 'your name' 'password'
    tls example@example.com
}
```
