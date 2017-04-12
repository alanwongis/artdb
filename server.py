import cherrypy
import json
import os
import shutil


import models
from models import session, Artwork, Person, Location, Consignment, Purchase

from jsonschema import validate
from jsonschema.exceptions import ValidationError


# error message handler
def error_page_default(status, message, trackback, version):
    ret = {
        'status': status,
        'version': version,
        'message': [message],
        'traceback': traceback }
    return json.dumps(ret)


      
class Root(object):
    _cp_config = {'error_page_default': error_page_default }

    @cherrypy.expose             
    def index(self):
        return "Hello World!"
    


class ArtworkIndexAPI(object):
    exposed = True
            
    
    @cherrypy.tools.json_out()
    def GET(self, **kwargs):
        """List all items"""

        filter_values = validate(kwargs, ArtworkIndexAPI.GET_VALIDATION) 
        result = models.list_artworks()
        
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

   

class ArtworkAPI(object):
    exposed = True
    
    
    PUT_VALIDATION = {
        "type" : "object",
        "properties": {
            "title": { "type": "string" },
            "list_price": { "type": "number"},
            "medium": {"type": "string"},
            "location": { "type": "string"},
            "buyer": {  "type": "string"},
            "notes": { "type": "string"}
        }
    }
       
    POST_VALIDATION = {
        "type": "object",
        "properties": {
            "title": { "type": "string"},
            "dimensions": { "type": "string"},
            "date_created": { "type": "date"},
            "medium": { "type": "string"},
            "list_price": {"type": "number"},
            "notes": {"type": "string"}         
         }
    }
    
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    #@cherrpy.tools.authorize_all()
    def GET(self, *vpath):
        """GET /artwork index or individual item """
        if len(vpath)==0: # get index
            result =  models.list_artworks()
        else:
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
        print "before"
        print str(args)
        try:
            s = session()
            validate(args, ArtworkAPI.PUT_VALIDATION)
            artwork = s.query(Artwork).get(int(ident))
            for key, value in args.iteritems():
                setattr(artwork, key, value)
            s.commit()
            result = True
        except ValidationError as e:
            error_msg = str(e)
            result = False
           
          
            
        if result:
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
    cherrypy.quickstart(Root(), '/', root_conf)