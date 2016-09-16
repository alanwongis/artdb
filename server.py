import cherrypy
import json
import os
import models
from models import Artwork, People, Location, Consignment, Purchase



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

        filter_values = kwargs # filter by: 'start_date', 'end_date', 'name', 'limit'
        result = models.list_artworks(filter_values)
        
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

    @cherrypy.tools.json_out()
    #@cherrpy.tools.authorize_all()
    def GET(self, *vpath):
        """GET item/nnn"""
        
        result = models.get_artwork(vpath[0])

        if result:
            cherrypy.response.status = 200
        else:
            cherrypy.response.status = 404
        return result
    

    @cherrypy.tools.json_in()
    #@cherrpy.tools.authorize_all()
    def PUT(self, ident):
        """Update item/nnn with new values"""
        
        args = cherrypy.request.json
        print ident, str(args)
        # result = models.update_artwork(ident, args)
        result = True
        
        if result:
            cherrypy.response.status = 204 # "success-return no content"
        else:
            cherrypy.response.status = 404


    @cherrypy.expose
    def DELETE(self, ident):
        """Delete item/nnn"""
        
        #result = models.delete_artwork(ident)
        result = True

        if result == True:
            cherrypy.response.status = 200 
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


    cherrypy.tree.mount(ArtworkIndexAPI(), '/artworks', rest_conf)
    cherrypy.tree.mount(ArtworkAPI(), '/artwork', rest_conf)
    cherrypy.quickstart(Root(), '/', root_conf)
