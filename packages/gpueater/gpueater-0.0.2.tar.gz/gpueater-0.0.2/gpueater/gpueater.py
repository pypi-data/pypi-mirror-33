import tempfile
import os
import requests
import json

G_GPUEATER_URL = "https://www.gpueater.com"

if 'GPUEATER_URL' in os.environ:
    G_GPUEATER_URL = os.environ['GPUEATER_URL']
    

G_HOMEDIR   = os.path.expanduser("~")
G_TMPDIR    = tempfile.gettempdir()
G_COOKIE    = os.path.join(G_TMPDIR,"gpueater_cookie.txt")
G_CONFIG    = None

try:
    G_CONFIG = json.loads(open(".eater").read())
except:
    try:
        G_CONFIG = json.loads(open(os.path.join(G_HOMEDIR,".eater")).read())
    except:
        print("You must define config to "+os.path.join(G_HOMEDIR,".eater")+" json file.")
        fp = open(os.path.join(G_HOMEDIR,".eater"),"w")
        fp.write('{"gpueater":{"email":"[Your email address]","password":"[Your password]"}}')
        fp.close
        exit(9)

if G_CONFIG['gpueater']['email'] == "[Your email address]":
    print("Invalid email")
    print("You must define config to "+os.path.join(G_HOMEDIR,".eater")+" json file.")
    exit(9)
    
if G_CONFIG['gpueater']['password'] == "[Your password]":
    print("Invalid password")
    print("You must define config to "+os.path.join(G_HOMEDIR,".eater")+" json file.")
    exit(9)
    

G_HEADERS = {'User-Agent': 'PythonAPI'}

try:
    G_HEADERS['cookie'] = open(G_COOKIE).read()
except:
    pass

def relogin():
    res = requests.post(G_GPUEATER_URL+"/api_login",headers=G_HEADERS,data={'email':G_CONFIG['gpueater']['email'],'password':G_CONFIG['gpueater']['password']})
    j = json.loads(res.text)
    G_HEADERS['cookie'] = res.headers['set-cookie']
    with open(G_COOKIE,"w") as f:
        f.write(G_HEADERS['cookie'])
    return j

def instance_list():
    res = requests.get(G_GPUEATER_URL+"/console/servers/instance_list",headers=G_HEADERS)
    j = None
    try:
        j = json.loads(res.text)
    except:
        relogin()
        j = instance_list()
    return j

def ssh_keys():
    res = requests.get(G_GPUEATER_URL+"/console/servers/ssh_keys",headers=G_HEADERS)
    j = None
    try:
        j = json.loads(res.text)
    except:
        relogin()
        j = instance_list()
    return j
    
def image_list():
    res = requests.get(G_GPUEATER_URL+"/console/servers/images",headers=G_HEADERS)
    j = None
    try:
        j = json.loads(res.text)
    except:
        relogin()
        j = image_list()
    return j

class ProductsResnpose:
    def __init__(self,res):
        self.images = res['data']['images']
        self.ssh_keys = res['data']['ssh_keys']
        self.products = res['data']['products']
        
    def find_image(self,name):
        data = self.images
        for k in data:
            if data[k]['name'] == name:
                return data[k]
        return None
        
    def find_product(self,name):
        data = self.products
        for d in data:
            if d['name'] == name:
                return d
        return None
    
    def find_ssh_key(self,name):
        data = self.ssh_keys
        for d in data:
            if d['name'] == name:
                return d
        return None
        
def ondemand_list():
    res = requests.get(G_GPUEATER_URL+"/console/servers/ondemand_launch_list",headers=G_HEADERS)
    j = None
    try:
        j = json.loads(res.text)
    except:
        relogin()
        j = ondemand_list()
    
    return ProductsResnpose(j)
    
def launch_ondemand_instance(form):
    if 'product_id' not in form:
        raise "product_id is required"
    if 'image' not in form:
        raise "image is required"
    if 'ssh_key_id' not in form:
        raise "ssh_key_id is required"
    if 'tag' not in form:
        form['tag'] = ""
    res = requests.post(G_GPUEATER_URL+"/console/servers/launch_ondemand_instance", headers=G_HEADERS, data=form)
    j = None
    try:
        j = json.loads(res.text)
    except:
        relogin()
        j = launch_ondemand_instance(form)
    return j
    
def terminate(form):
    if 'instance_id' not in form:
        raise "instance_id is required"
    if 'machine_resource_id' not in form:
        raise "image is machine_resource_id"
    if 'tag' not in form:
        form['tag'] = ""
    arr = [{'instance_id':form['instance_id'],'machine_resource_id':form['machine_resource_id']}]
    res = requests.post(G_GPUEATER_URL+"/console/servers/force_terminate", headers=G_HEADERS, data=json.dumps(arr))
    j = None
    try:
        j = json.loads(res.text)
    except:
        relogin()
        j = terminate(form)
    return j
