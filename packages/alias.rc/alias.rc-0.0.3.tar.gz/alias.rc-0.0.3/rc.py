import click

import urllib2
import base64
import json
import os.path
import getpass
from usersettings import Settings
from pprint import pprint
from simplecrypt import encrypt, decrypt
from binascii import hexlify, unhexlify


class Config(object):

    def __init__(self):
        self.verbose = False
        self.token = ''
        self.gist_id = ''

        s = Settings("li.env.rc")
        s.add_setting("gist_id", str)
        s.add_setting("token", str)
        s.load_settings() # loads anything that might be saved
        self.settings = s


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option('--verbose', default=False, help='Verbose mode', type=bool)
@pass_config
def cli(config, verbose):
    changed = False
    if config.settings.token == "" or config.settings.token == None or config.settings.token == "None":
        token = click.prompt('GitHub token', type=str)
        if gistTest(token) == False:
            click.echo("\nIt appears that the token is invalid.")
            exit()
        config.settings.token = token
        changed = True

    # if config.settings.gist_id == "" or config.settings.gist_id == None or config.settings.gist_id == "None":
    #     config.settings.gist_id = findGist()
    #     changed = True

    if changed == True:
        config.settings.save_settings()

    # gistTest(config.settings.token)
    # pprint(config.settings.gist_id)
    # exit()
    config.token = config.settings.token
    config.gist_id = config.settings.gist_id
    config.verbose = verbose
    # click.echo("Using GitHub token (%s) and gist id (%s)" % (config.token, config.gist_id))

@cli.command(help="Create alias.rc file")
@pass_config
def setup(config):
    install()

@cli.command(help="Reset your GitHub credentials")
@pass_config
def reset(config):
    answer = click.confirm("Are you sure you want to reset your GitHub token?")
    if answer == False:
        return

    config.gist_id = None
    config.token = None
    config.settings.token = None
    config.settings.gist_id = None
    config.settings.save_settings()
    click.secho("\nCleared token.", fg="green")


# @cli.command(help='Coming soon (maybe)')
# @click.option('--string', default='World', help='A little help note')
# @click.argument('key', type=str)
# @pass_config
def digitalocean(config, key):
    click.echo('Enabling firewall %s' % key)
    # click.echo(key)

@cli.command(help='Upload configuration')
@pass_config
def up(config):
    upload()



@cli.command(help='Download configuration')
@pass_config
def down(config):
    if config.gist_id == "None" or config.gist_id == None or config.gist_id == "":
        config.settings.gist_id = findGist()
        config.gist_id = config.settings.gist_id
        config.settings.save_settings()
        
    url = "https://api.github.com/gists"
    url += '/' + config.gist_id

    req = urllib2.Request(url)
    req.add_header("Authorization", "token {}".format(config.token))
    req.add_header("Content-Type", "application/json")

    try:
       result = urllib2.urlopen(req)
       # print result.read()
    except urllib2.URLError, e:
       print e

    response = result.read()

    # print response
    data = json.loads(response)
    content = data["files"][".alias.rc"]["content"]
    # print content
    if content.find("!encrypted!") != -1:
        password = click.prompt('The file is encrypted. Password is required', type=str)
        content = content.replace('!encrypted!', '', 1)
        # print content
        content = decrypt(password, unhexlify(content))
        # print content

    path = os.path.expanduser("~") + '/.alias.rc'
    open(path, 'w').write(content)
    click.echo('Done')
    # filename = '.alias.rc'


def install(soft = False):
    path = os.path.expanduser("~") + '/.alias.rc'
    if os.path.isfile(path) == True:
        click.secho("%s file already exists." % path, fg="red")
        exit()

    if soft == True:
        create = click.confirm("\nWould you like to create the alias.rc file (%s)" % path)

        if create == False:
            exit()

    click.echo("Creating a boilerplate alias.rc file in ")
    open(path, 'w').write("# alias.rc configurations")

    return True

def gistTest(token):
    url = "https://api.github.com/gists"

    req = urllib2.Request(url)
    req.add_header("Authorization", "token {}".format(token))
    req.add_header("Content-Type", "application/json")

    try:
       result = urllib2.urlopen(req)
       # pprint(result.read())
       return True
    except urllib2.URLError, e:
       print e

    return False


@pass_config
def upload(config):
    path = os.path.expanduser("~") + '/.alias.rc'
    if os.path.isfile(path) == False:
        click.secho(".alias.rc file does not exist (Path: %s)." % path, fg="red")
        if install(True) == False:
            return
    filename = '.alias.rc'
    data = {}
    data["description"] = "Cli [alias.rc configuration]"
    data["public"] = False
    data["files"] = {filename:{}}

    content = open(path).read()

    password = click.prompt('Would like to encrypt the files? Then enter a password', type=str, default='')
    if password != '':
        content = '!encrypted!' + hexlify(encrypt(password, content.encode('utf8')))

    # print content
    data["files"][filename]["content"] = content

    url = "https://api.github.com/gists"

    if config.gist_id != '' and config.gist_id != None and config.gist_id != "None":
        url += '/' + config.gist_id
    else:
        id = findGist(config, True)
        if id != None and len(id) > 10:
            config.settings.gist_id = id
            config.gist_id = config.settings.gist_id
            config.settings.save_settings()
            url += '/' + config.gist_id

    req = urllib2.Request(url, json.dumps(data))
    req.add_header("Authorization", "token {}".format(config.token))
    req.add_header("Content-Type", "application/json")

    error = False
    try:
       result = urllib2.urlopen(req)
       # print result.read()
    except urllib2.HTTPError as e:
       click.echo(e.read())
       if e.code == 404:
        error = True

    if error == True or config.gist_id == None or config.gist_id == False or config.gist_id == "None":
        config.settings.gist_id = findGist()
        config.gist_id = config.settings.gist_id
        config.settings.save_settings()

        if error == True:
            upload()
            return

    click.secho("Pushed configuration to gist", fg="green")


@pass_config
def findGist(config, silent = False):
    url = "https://api.github.com/gists?limit=1000"

    req = urllib2.Request(url)
    req.add_header("Authorization", "token {}".format(config.token))
    req.add_header("Content-Type", "application/json")

    try:
       result = urllib2.urlopen(req)
       # pprint(result.read())
       # return True
    except urllib2.URLError, e:
       print e
       exit()

    response = result.read()

    # print response
    data = json.loads(response)
    configurations = []
    for gist in data:
        if gist['description'].find("[alias.rc configuration]") != -1:
            configurations.append(gist)

    # print "helii %d %s" % (len(configurations), silent)

    if len(configurations) == 0:
        if silent == True:
            return

        click.echo("You have no configurations stored in your Gist repo.")
        create = click.confirm("\nWould you like to create the alias.rc file in your gist repo")
        if create == True:
            config.gist_id = None
            config.settings.gist_id = None
            config.settings.save_settings()
            upload()
            return
        exit()

    index = 1
    if len(configurations) > 1:
        click.echo("It seems you have multiple configurations. Choose one\n")
        for index, conf in enumerate(configurations):
            click.echo("%d. %s (Created: %s)" % ((index+1), conf["description"], conf["created_at"]))

        click.echo("\n")
        index = click.prompt(click.style('Which configuration would you like to use', fg='green'), type=int, default=1)

        if index < len(configurations) or (index-1) > (len(configurations)):
            click.echo("Invalid input. Try again")
            exit()

    return configurations[index-1]["id"]

@cli.command(help='Enable alias.rc')
def enable():
    if enableInRc('.zshrc') == False and enableInRc('.bashrc') == False:
        echo.secho("No .bashrc/zshrc file found")
        return

@cli.command(help='Disable alias.rc')
def disable():
    if disableInRc('.zshrc') == False and disableInRc('.bashrc') == False:
        click.secho("alias.rc is not enabled.", fg="red")
        return



def enableInRc(file):
    base = os.path.expanduser("~")
    path = base + '/' + file
    if os.path.isfile(path) == False:
        return False

    file = open(path, 'r+a')
    content = file.read()
    alias = "\n[ -f %s/.alias.rc ] && source %s/.alias.rc" % (base, base)
    # print alias
    if content.find(alias) != -1:
        click.secho("alias.rc is already enabled in %s" % path, fg="yellow")
        return True

    # print "\n\n# alias.rc\n%s" % alias
    file.write("\n# alias.rc%s" % alias)
    click.secho("alias.rc is now enabled in %s" % path, fg="green")

    return True



def disableInRc(file):
    base = os.path.expanduser("~")
    path = base + '/' + file
    if os.path.isfile(path) == False:
        return False

    file = open(path, 'r')
    content = file.read()
    alias = "\n[ -f %s/.alias.rc ] && source %s/.alias.rc" % (base, base)
    if content.find(alias) == -1:
        return False

    file = open(path, 'w')
    content = content.replace(alias, '')
    content = content.replace("\n# alias.rc", '')
    file.write(content)
    click.secho("Removed config from %s" % path, fg="green")
    click.echo("Now open a new terminal/tab for the changes to take effect\nor run 'source %s'" % path)

    # print "source %s" % path
    # os.system("source %s" % path)

    return True


# @cli.command()
# @pass_config
# def test(config):
#     s = Settings('li.env.apps.rc')    
#     s.add_setting("counter", int, default=0)
#     s.add_setting("animal", str, default="turtles")
#     s.add_setting("runtimes", list, [])
#     s.load_settings() # loads anything that might be saved

#     s.counter += 1
#     if s.counter > 2:
#         # Tired of turtles?
#         s.animal = "the Rabbit of Caerbannog"
#     s.runtimes.append('time.time()')
#     s.save_settings()

#     print "I've run {0.counter} time(s). I like {0.animal}!".format(s)
#     print "I've been launched at these times: ",
#     print ", ".join([str(x) for x in s.runtimes])
