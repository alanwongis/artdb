import cherrypy

import json
import os
import shutil
import datetime

import models
from models import session, Artwork, Person, Location, Consignment, Purchase

import formencode
from formencode import validators

#
# helper functions
#

def deserialize_date(st):
    return datetime.strptime(st, '%Y-%m-%dT%H:%M:%S.%fZ')


def deserialize_artwork(args):
    for k in args.keys():
        if k.find("date") >=0:
            args[k] = deserialize_date(args[k])
   

def error_page_default(status, message, trackback, version):
    #error message handler
    ret = {
        'status': status,
        'version': version,
        'message': [message],
        'traceback': traceback }
    return json.dumps(ret)


#
# form validators
#

class ISO8601Date(formencode.FancyValidator):
    def _convert_to_python(self, value, state):
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
   
class ArtworkFormSchema(formencode.Schema):
    title = validators.ByteString(not_empty=True)
    dimensions = validators.ByteString(if_missing=True)
    list_price = validators.Number(if_missing=False)
    notes = validators.ByteString(if_missing=False)
    medium = validators.ByteString(if_missing=False)
    creation_date = ISO8601Date(if_missing=False)
    
artwork_form_validator = ArtworkFormSchema()

class PersonFormSchema(formencode.Schema):
    title = validators.ByteString(if_missing=False)
    first_name = validators.ByteString(not_empty=True)
    last_name = validators.ByteString(if_missing=False)
    address = validators.ByteString(if_missing=False)
    city = validators.ByteString(if_missing=False)
    state_prov = validators.ByteString(if_missing=False)
    country = validators.ByteString(if_missing=False)
    postal = validators.ByteString(if_missing=False)
    main_phone = validators.ByteString(if_missing=False)
    alt_phone = validators.ByteString(if_missing=False)
    cell_phone = validators.ByteString(if_missing=False)
    company = validators.ByteString(if_missing=False)
    email = validators.Email(if_missing=False)
    notes = validators.ByteString(if_missing=False)
    
person_form_validator = PersonFormSchema()



#
# controllers
#

class Root(object):
    _cp_config = {'error_page_default': error_page_default }

    @cherrypy.expose             
    def index(self):
        return "Hello World!"
    

class ArtworkAPI(object):
    exposed = True
    
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    #@cherrpy.tools.authorize_all()
    def GET(self, *vpath):
        """GET /artwork index or individual item """
        if len(vpath)==0: # get listing 
            result =  models.list_artworks()
        else: # get individual ite,
            result = models.get_artwork(vpath[0])
            
        if result:
            cherrypy.response.status = 200
        else:
            cherrypy.response.status = 404
        return result

        
    @cherrypy.tools.json_in()
    #@cherrypy.tools.authorize_all() 
    def POST(self):
        """Create a new item(optionally using input values), returning location"""

        args = cherrypy.request.json
        print str(args)
        #ident = models.create_artwork(args)
        ident = 100
        
        cherrypy.response.headers['Location'] = "/artwork/"+ str(ident)
        cherrypy.response.status = 201 # "created"


    @cherrypy.tools.json_in()
    #@cherrpy.tools.authorize_all()
    def PUT(self, ident):
        """Update item/nnn with new values"""
        
        args = cherrypy.request.json
        # validate and convert args    
        print str(args)
        is_valid = False
        try:
            new_args = artwork_form_validator.to_python(args)
            is_valid = True
        except Exception as e:
            error_msg = str(e)
      
        # save the new values to db
        saved = False
        if is_valid:
            s = session()
            artwork = s.query(Artwork).get(int(ident))
            for key, value in new_args.iteritems():
                if value:
                    setattr(artwork, key, value)
            s.commit()
            saved = True

        if saved:
            cherrypy.response.status = 204 # "success-return no content"
        else:
            cherrypy.response.status = 404
            return error_msg


    @cherrypy.expose
    def DELETE(self, ident):
        """Delete item/nnn"""
        
        #result = models.delete_artwork(ident)
        result = True

        if result == True:
            cherrypy.response.status = 200 
        else:
            cherrypy.response.status = 404



class ArtImageAPI(object):
    exposed = True


    def POST(self, ident="", img_file=""):
        body = cherrypy.request.body
        print ident
        print body.length
##        dest = os.path.join("/Users/alanwong/Desktop/artdbenv/artdb/temp/result.jpg")
##        with open(dest, "wb") as f:
##            shutil.copyfileobj(body, f)
        data = ""
        while True:
            chunk = body.read(8192)
            if not chunk:
                break
            else:
                data = data + chunk
                size = size +len(chunk)
            
        cherrypy.response.status = 201


        
 #   @cherrypy.tools.json_in()
    #@cherrpy.tools.authorize_all()
    def PUT(self, ident="", **kwargs):
        """ expected endpoint is /image/{artwork_id} where the data is a
        FormData header with a field '0' holding the image file data.
        
        On success return the url of the new image"""
        result = False
        # process the image
        if '0' in kwargs:
            fileUpload = kwargs['0']
            print fileUpload.filename
            size = 0
            data = ""
            while True:
                chunk = fileUpload.file.read(8192)
                if not chunk:
                    break
                else:
                    data = data + chunk
                    size = size + len(chunk)              
            print "Image upload "+ str(size)
            img_hash = models.process_image(fileUpload.filename, data)
            result = True

        if result:
            cherrypy.response.headers['Location'] = "/static/images/"+ img_hash
            cherrypy.response.status = 201 # "created"
        else:
            cherrypy.response.status = 404

 

 
if __name__ == "__main__":
    
    root_conf = {
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.abspath('./static')
        }           
    }

    rest_conf = {
        '/' : {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
            #'tools.response.headers.on': True,
            #'tools.response.headers.headers': [('Content-Type', 'text/plain')]
        }
    }


    #cherrypy.tree.mount(ArtworkIndexAPI(), '/api/artworks', rest_conf)
    cherrypy.tree.mount(ArtworkAPI(), '/api/artwork', rest_conf)
    cherrypy.tree.mount(ArtImageAPI(), 'api/image', rest_conf)
    #cherrypy.config.update({"server.socket_port": 8080})
    cherrypy.quickstart(Root(), '/', root_conf)
