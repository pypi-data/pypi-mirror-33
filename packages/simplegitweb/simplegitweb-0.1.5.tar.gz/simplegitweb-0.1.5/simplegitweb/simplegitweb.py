from pathlib import Path
from configparser import ConfigParser
import copy
import os
import click

from dulwich.repo import Repo
from dulwich.web import *

from jinja2 import Environment, PackageLoader, select_autoescape, Template

try:
    from urlparse import parse_qs
except ImportError:
    from urllib.parse import parse_qs

env = Environment(
    loader=PackageLoader(__name__, 'templates'),
    autoescape=select_autoescape(['html'])
)


def get_root_index(req, backen, mat):
    req.respond(HTTP_OK, 'text/html')
    repos = ";".join([c for c in backen.repos.keys()])

    yield env.get_template("index_base.html").render(repos_list=repos).encode()

def add_new_repository(req, backen, mat):
    req.respond(HTTP_OK, 'text/html')
    repos = ";".join([c for c in backen.repos.keys()])
    repos_make_message = None
    repos_make = False
    params = parse_qs(req.environ['QUERY_STRING'])
    new_repository = params.get('add_new_repository', [None])[0]+".git"

    if new_repository and new_repository not in repos.split(";"):
        repo_dir = os.path.join(InitRepoPath().get_scanpath(), new_repository)
        try:
            Repo.init_bare(repo_dir, mkdir=True)
        except PermissionError:
            repos_make_message = "make repository folder permission error."
        except FileExistsError:
            repos_make_message = "make repository folder file exists error."
        except OSError:
            repos_make_message = "make repository folder os error."
        else:
            try:
                backen.repos[str('/' + new_repository)] = Repo(repo_dir)
            except:
                pass
            finally:
                repos = ";".join([c for c in backen.repos.keys()])
                repos_make = True

    yield env.get_template("add_new_repository.html").render(
                                                            repos_list=repos,
                                                            repos_make_message=repos_make_message,
                                                            repos_make=repos_make).encode()

        
HTTPGitApplication.services[('GET', re.compile('^/$'))] = get_root_index
HTTPGitApplication.services[('GET', re.compile('^/repository'))] = add_new_repository


class InitRepoPath():

    def __init__(self, config_path=None):
        self.config = ConfigParser()
        if (config_path):
            CONFIG_NAME = config_path
        else:
            CONFIG_NAME = 'simplegitweb.conf'
        try:
            self.home_path = os.path.join(str(Path.home()), "."+CONFIG_NAME)
        except AttributeError:
            self.home_path = os.path.join(os.path.expanduser("~"), "."+CONFIG_NAME)
        self.etc_path = os.path.join('/etc', CONFIG_NAME)
        self.config_path = [CONFIG_NAME, self.home_path, self.etc_path]

        for path in self.config_path:
            if Path(path).exists():
                self.config.read(path)
                break
            else:
                self.config["DEFAULT"] = {
                        "scanpath": ".",
                        "listen_address": "127.0.0.5",
                        "port": 3000
                    }
                try:
                    with open(path, 'w') as configfile:
                        self.config.write(configfile)
                except:
                    continue
    
    def get_scanpath(self):
        if self.config["DEFAULT"]['scanpath']:
            scanpath = os.path.abspath(self.config["DEFAULT"]['scanpath'])
            return scanpath
    
    def get_listen_address(self):
        listen_address = self.config["DEFAULT"]["listen_address"]
        port = int(self.config["DEFAULT"]["port"])
        
        if (listen_address and port):
            return listen_address, port
        else:
            return "127.0.0.5", 3000
        
    def get_backends(self):
        path = self.get_scanpath()
        backends = dict()
        
        def create_testRepo():
            try:
                os.makedirs(path)
            except:
                return []
            else:
                testRepo = "testRepo.git"
                repo = Repo.init_bare(os.path.join(path, testRepo), mkdir=True)
                backends[str('/') + testRepo] = repo
            return os.listdir(path)

        try:
            reposdir = os.listdir(path)
        except FileNotFoundError:
            reposdir = create_testRepo()

        for i in reposdir:
            if i == ".git":
                return {}

            repo_path = os.path.join(path, i)
            try:
                repo = Repo(repo_path)
            except:
                continue
            backends[str('/'+i)] = repo
            del repo

        if not backends:
            create_testRepo()
                
        return backends

@click.command()
@click.option('--config', help='set the simplegitweb.conf file path.')
def main(config=None):
    """Entry point for starting an HTTP git server."""
    init = InitRepoPath(config)

    listen_address, port = init.get_listen_address()

    backend = DictBackend(init.get_backends())
        
    app = make_wsgi_chain(backend)
    server = make_server(listen_address, port, app,
                         handler_class=WSGIRequestHandlerLogger,
                         server_class=WSGIServerLogger)
    logger.info('Listening for HTTP connections on %s:%d',
                listen_address, port)
    server.serve_forever()


if __name__ == '__main__':
    main()
    

