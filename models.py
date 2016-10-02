import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, select, desc
from formencode import Schema, validators


Base = declarative_base()


artwork_tag_association_table = Table("association", Base.metadata,
                                      Column("artwork_id", Integer, ForeignKey("artwork.id")),
                                      Column("tag_id", Integer, ForeignKey("tag.id"))
                                      )



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
    

class People(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key = True)
    name = Column(String(255))
    address = Column(String(255))
    main_phone = Column(String(32))
    alt_phone = Column(String(32))
    cell_phone = Column(String(32))
    notes = Column(String(255))
    

class Location(Base):
    __tablename__ = 'location'
    id = Column(Integer, primary_key = True)
    name = Column(String(255))
    address = Column(String(255))
    contact_person = Column(Integer, ForeignKey('people.id'))
    notes = Column(String(255)) 
                      
class Purchase(Base):
    __tablename__= "purchase"
    id = Column(Integer, primary_key = True)
    buyer_id = Column(Integer, ForeignKey('people.id'), primary_key = True)
    artwork_id = Column(Integer, ForeignKey('artwork.id'), primary_key = True)
    purchase_price = Column(Integer)
    purchase_date = Column(String(32))
    notes = Column(String(255))
    


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
    


# sqlalchemy boilerplate
engine = create_engine("sqlite:///artdb.sqlite")
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)


#helper functions
def format_date(date):
    MONTH_NAME = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
    return MONTH_NAME[date.month-1]+" "+str(date.day)+" "+str(date.year)



def date_string(date):
    return 

# validators


class ArtworkSchema(Schema):
    
    title = validators.String(if_missing = None)
    date_created = validators.String(if_missing = None)
    list_price = validators.Int(if_missing = None)
    dimensions = validators.String(if_missing = None)
    notes = validators.String(if_missing = None)



# API to the database



def create_artwork():
    pass


def update_artwork(ident, **kwargs):
    ident = int(ident)
    s = session()
    artwork = s.query(Artwork).filter(Artwork.id == ident).one()

    values = ArtworkSchema(allow_extra_fields = True).to_python(kwargs)
    print values
    artwork.title = kwargs["title"]   
    #artwork.list_price = int(kwargs["list_price"])
    #artwork.medium = kwargs["medium"]
    s.commit()
    
    

def delete_artwork(ident):
    pass


def get_artwork(ident):
    try:
        ident = int(ident)
        s = session()
        artwork = s.query(Artwork).filter(Artwork.id == ident).one()
        result = {}
        result["id"] = artwork.id
        result["title"] = artwork.title
        result["date_created"] = str(artwork.date_created)
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




    

    
def test():    
    print "committing..."
    painting = Artwork(title="Blue boy", description="A classic")
    s = session()
    s.add(painting)
    s.commit()

    print "committed"

    rows = s.query(Artwork).all()
    print len(rows)
    


if __name__ == "__main__":
    print str(list_artworks())
    

