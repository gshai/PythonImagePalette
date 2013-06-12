"""Request Handler for /main endpoint."""

__author__ = 'shai.gilad@gmail.com'


import io
import jinja2
import logging
import os
from urlparse import urlparse
import webapp2

from google.appengine.api import urlfetch
from google.appengine.ext import deferred
from google.appengine.api import users
from google.appengine.api.app_identity import get_application_id


from imageProcessing import color_palette as cp


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
    
class IndexHandler(webapp2.RequestHandler):
  """Request Handler for the / endpoint."""
  logging.info("index // ")

  def _render_template(self, message=None):      
    """Render the main page template."""
    logging.info("get templates/index.html")
    pr = urlparse(self.request.url)
        
    image_url = ["http://www.elle.com/cm/elle/images/Xs/elle-01-cruise-2013-dior-xln-lg.jpg",
                                       "http://www.elle.com/cm/elle/images/ut/elle-02-cruise-2013-dior-xln-lg.jpg",
                                       "http://www.elle.com/cm/elle/images/R8/elle-05-cruise-2013-dior-xln-lg.jpg"]
    imageRender = cp.histogram_for_url_and_rect(image_url[0] )
#     data_uri = imageRender.read().encode('base64').replace('\n', '')
    
    print "imageRender: ", imageRender
    template_values = {'appBaseUrl' : pr.netloc}
    template_values['imageUrls'] = image_url
    template_values['imageRendered'] = imageRender
    template = jinja_environment.get_template('/content/index.html')  
    #logging.info(template_values)  
    self.response.out.write(template.render(template_values))

  def _get_full_url(self, path):
    """Return the full url from the provided path."""
    pr = urlparse(self.request.url)
    return '%s://%s%s' % (pr.scheme, pr.netloc, path)

  def get(self):
    """Render the main page."""
    logging.info("IndexHandler get")
    self._render_template()

  def post(self):
    """Execute the request and render the template."""
    message = "I don't know how to "
    self.response.out.write(message)



MAIN_ROUTES = [
    ('/', IndexHandler)
]
