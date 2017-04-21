from models import *
from PIL import Image, ImageOps
import hashlib
import datetime

path_to_images = "/Users/alanwong/Desktop/art_images/"

def process_image(filename):
    # read the image file
    # get the md5 hash(use as a filename)
    # resize the image to 800x600
    # save to images folder
    # create a 80x80 thumbnail
    # save to the thumbs folder
    # return the hash
    im = Image.open(filename)
    new_filename = str(hashlib.md5(open(filename).read()).hexdigest())
    new_image = im.copy()
    new_image.thumbnail((800,600), Image.ANTIALIAS)
    new_image.save("./static/images/"+new_filename+".jpg")
    thumb_image = ImageOps.fit(im, (80,80), Image.ANTIALIAS)
    thumb_image.save("./static/thumbs/"+new_filename+"_tb.jpg")
    return new_filename
    
    

def init_db():
    import csv

    s = session()

    Person.__table__.drop(engine)
    Person.__table__.create(engine)
    
    print "initializing person database..."
    with open("clients.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            title = row["ConTitle"].strip()
            first_name = row["ConFirstName"].strip()
            last_name = row["ConLastName"].strip()
            address = row["ConAddrss"].strip()
            city = row["ConCity"].strip()
            state_prov = row["ConState"].strip()
            country = row["ConCountry"].strip()
            postal  = row["ConZip"].strip()
            main_phone = row["ConHmPhone"].strip()
            cell_phone = ""
            alt_phone = ""
            email = row["ConEmail"].strip()
            spouse = row["ConSpouseFirstName"].strip()
            if len(spouse)>=0:
                notes = "Spouse: "+spouse
            else:
                notes = ""
            person = Person(title = title, first_name = first_name,
                            last_name = last_name, address = address,
                            city = city, state_prov = state_prov,
                            country = country, postal = postal,
                            main_phone = main_phone, cell_phone = cell_phone,
                            alt_phone = alt_phone, email = email,
                            notes = notes)
            s.add(person)
            s.commit()
            


    print "initializing locations ...."
    Location.__table__.drop(engine)
    Location.__table__.create(engine)

    with open("galleries.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row["GalName"].strip()
            suite = row["GalSuite"].strip()
            street1 = row["GalStreet"].strip()
            street2 = row["GalStreet2"].strip()
            address = ",".join([" ".join([suite, street1]), street2])
            city = row["GalCity"]
            state_prov = row["GalState"].strip()
            country = ""
            postal = row["GalZip"].strip()
            phone = row["GalPhoneNumber"].strip()
            fax = row["GalFax"].strip()
            website = row["GalWebsite"].strip()
            email = row["GalEmail"].strip()
            location = Location(name = name, address = address,
                                city = city, state_prov = state_prov,
                                country = country, postal = postal,
                                phone = phone, fax = fax,
                                website = website, email = email)
            s.add(location)
            s.commit()
            
            
    
    
    # print "initializing artwork database..."
    
    # Artwork.__table__.drop(engine) # delete old values
    # Artwork.__table__.create(engine)
    # ArtImage.__table__.drop(engine)
    # ArtImage.__table__.create(engine)

    # with open("artwork.csv") as csvfile:
        # reader = csv.DictReader(csvfile)
        # for row in reader:
            # title = row["InvTitle"].strip()
            # date_created = row["InvCreationDate"]
            # year, month, day = ( int(elem) for elem in date_created.split("-") )
            # old_id = row["InvRefID"]
            # status = row["ArtworkStatus::Status"]
            
            # try:
                # price = int(row["InvPrice"])
            # except:
                # price = 0
                
            # gallery = row["GalleryLocationfor Inventory::GalName"]
            # height = row["InvHeight"]
            # width = row["InvWidth"]
            # depth = row["InvDepth"]
            # medium = row["Medium::MedMedium"]
            # image_filename = row["InvImages"].split("\n")[1][28:]
            # print title, "[", image_filename, "]"

            # hash_name = process_image(path_to_images+image_filename)
            # img = ArtImage(filename=image_filename, hash_name=hash_name)
            # s.add(img)
        
            # artwork = Artwork(title=title,
                              # list_price= price,
                              # date_created = datetime.date(year, month, day),
                              # status = status,
                              # medium = medium,
                              # notes = "")
            # artwork.image = img
            # s.add(artwork)
            # s.commit()
            


    print "processing sales..."
    
    Purchase.__table__.drop(engine)
    Purchase.__table__.create(engine)
    with open("sales.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pass


    print "processing consignments..."
    Consignment.__table__.drop(engine)
    Consignment.__table__.create(engine)
    with open("consignments.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pass
        
        
        


if __name__ == "__main__":
    init_db()
    
    
