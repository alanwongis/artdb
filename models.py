import os
import sys
import StringIO
import hashlib
import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, Date, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, select, desc

from PIL import Image, ImageOps


Base = declarative_base()

artwork_tag_association_table = Table("artwork_tag_association", Base.metadata,
                                      Column("artwork_id", Integer, ForeignKey("artwork.id")),
                                      Column("tag_id", Integer, ForeignKey("tag.id"))
                                      )

invoice_purchase_association_table = Table("invoice_purchase_association", Base.metadata,
                                           Column("invoice_id", Integer, ForeignKey("invoice.id")),
                                           Column("purchase_id", Integer, ForeignKey("purchase.id"))
                                           )

#
#helper functions
#

def format_date(date):
    MONTH_NAME = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
    return MONTH_NAME[date.month-1]+" "+str(date.day)+" "+str(date.year)


def deserialize_date(st):
    return datetime.strptime(st, '%Y-%m-%dT%H:%M:%S.%fZ')


def process_image(filename, img_data):
    # read the image file
    # get the md5 hash(use as a filename)
    # resize the image to 800x600
    # save to images folder
    # create a 80x80 thumbnail
    # save to the thumbs folder
    # return the hash
    im = Image.open(StringIO.StringIO(img_data))
    new_filename = str(hashlib.md5(img_data).hexdigest())
    new_image = im.copy()
    new_image.thumbnail((800,600), Image.ANTIALIAS)
    new_image.save("./static/images/"+new_filename+".jpg")
    thumb_image = ImageOps.fit(im, (80,80), Image.ANTIALIAS)
    thumb_image.save("./static/thumbs/"+new_filename+"_tb.jpg")
    return new_filename


#    
# define the databases
#

class Artwork(Base):
    __tablename__ = 'artwork'
    id = Column(Integer, primary_key = True)
    title = Column(String(255))
    dimensions= Column(String(32))
    date_created = Column(Date)
    medium = Column(String(32))
    location_id = Column(Integer, ForeignKey('location.id'))
    list_price = Column(Integer)
    purchase_id = Column(Integer, ForeignKey('purchase.id'))
    consignment_id = Column(Integer, ForeignKey('consignment.id'))
    image = relationship("ArtImage", uselist = False, back_populates='artwork')
    status = Column(String(32))
    notes = Column(String(1024))
    tags = relationship("Tag", uselist = True,
                        secondary = artwork_tag_association_table,
                        back_populates="artworks")

    
class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key = True)
    title = Column(String(16))
    first_name = Column(String(64))
    last_name = Column(String(64))
    address = Column(String(128))
    city = Column(String(64))
    state_prov = Column(String(64))
    country = Column(String(64))
    postal = Column(String(32))
    main_phone = Column(String(32))
    alt_phone = Column(String(32))
    cell_phone = Column(String(32))
    company = Column(String(64))
    email = Column(String(64))
    notes = Column(String(255))

    
class Location(Base):
    __tablename__ = 'location'
    id = Column(Integer, primary_key = True)
    name = Column(String(255))
    address = Column(String(255))
    city = Column(String(255))
    state_prov = Column(String(255))
    country = Column(String(255))
    postal = Column(String(255))
    phone = Column(String(32))
    fax = Column(String(32))
    website = Column(String(64))
    email = Column(String(64))
    contact_person = Column(Integer, ForeignKey('person.id'))
    notes = Column(String(255)) 

                     
class Purchase(Base):
    __tablename__= "purchase"
    id = Column(Integer, primary_key = True)
    buyer_id = Column(Integer, ForeignKey('person.id'), primary_key = True)
    artwork_id = Column(Integer, ForeignKey('artwork.id'), primary_key = True)
    purchase_price = Column(Integer)
    purchase_date = Column(String(32))
    notes = Column(String(255))
    invoice_id = Column(Integer, ForeignKey('invoice.id'))
    invoice = relationship("Invoice", back_populates="purchases")

   
class Invoice(Base):
    __tablename__ = "invoice"
    id = Column(Integer, primary_key = True)
    date = Column(Date)
    notes = Column(String(255))
    purchases = relationship("Purchase", back_populates = "invoice")
    total = Column(Integer)   


class Consignment(Base):
    __tablename__ = 'consignment'
    id = Column(Integer, primary_key = True)
    location_id = Column(Integer, ForeignKey('location.id'), primary_key = True)
    artwork_id = Column(Integer, ForeignKey('artwork.id'), primary_key = True)
    consignment_date = Column(String(32))
    notes = Column(String(255))


class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key = True)
    name = Column(String(32))
    artworks = relationship("Artwork",
                            secondary = artwork_tag_association_table,
                            back_populates = "tags")
    

# there is a one to one relation between Artworks and ArtImages
class ArtImage(Base):
    __tablename__ = "artimage"
    id = Column(Integer, primary_key = True)
    filename = Column(String(255))
    hash_name = Column(String(32))
    priority = Column(Integer)
    artwork_id = Column(Integer, ForeignKey("artwork.id"))
    artwork = relationship("Artwork", back_populates = "image") # populates Artwork.images
    

#
# sqlalchemy boilerplate
#

engine = create_engine("sqlite:///artdb.sqlite")
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)



#
# API to the database
#


def get_artwork(ident):
    try:
        ident = int(ident)
        s = session()
        artwork = s.query(Artwork).filter(Artwork.id == ident).one()
        result = {}
        # serialize the results
        result["id"] = artwork.id
        result["title"] = artwork.title
        result["date_created"] = artwork.date_created.ctime()
        result["status"] = artwork.status
        result["list_price"] = artwork.list_price
        result["dimensions"] = artwork.dimensions
        result["medium"] = artwork.medium
        result["image_hash"] = artwork.image.hash_name
        result["location_id"] = artwork.location_id
        result["purchase_id"] = artwork.purchase_id
        result["consignment_id"] = artwork.consignment_id
        result["notes"] = artwork.notes
        # TODO: tags etc...
    except:
        result = None
    return result


def list_artworks(name_filter="", start_date=None,
                 end_date=None, gallery="", buyer = ""):
    results = []
    s = session()
    query = s.query(Artwork, ArtImage)
    query = query.filter(Artwork.id == ArtImage.artwork_id)
    query = query.order_by(desc(Artwork.date_created))
    rows = query.all()
    for artwork, image in rows:
        results.append( [artwork.id, artwork.title,
                         format_date(artwork.date_created),
                         image.hash_name, artwork.status] )
    return results


def update_artwork_image(artwork_id=None, original_filename="", image_data=None):
    pass


def delete_artwork_image(artwork_id=None):
    pass



def create_person():
    pass

def delete_person(ident):
    pass

def update_person(ident, **kwargs):
    pass

def get_person(ident):
    pass

def list_persons(name_filter="", address_filter=""):
    pass


def create_location():
    pass

def delete_location(ident):
    pass

def update_location(ident, **kwargs):
    pass

def get_location(ident):
    pass

def list_locations(name_filter=""):
    pass



def create_consignment(artwork_id, location_id):
    pass

def remove_consignment(consign_id):
    pass



def create_purchase(artwork_id, person_id, sale_price):
    pass

def get_purchase(ident):
    pass

def update_purchase(ident, new_price):
    pass

def delete_purchase(ident):
    pass

def list_purchases(person_id=None, start_date=None, end_date=None):
    pass






if __name__ == "__main__":
    print str(list_artworks())
    


