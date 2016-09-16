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

    
    print "initializing artwork database..."
    
    Artwork.__table__.drop(engine) # delete old values
    Artwork.__table__.create(engine)
    ArtImage.__table__.drop(engine)
    ArtImage.__table__.create(engine)

    with open("artwork.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            title = row["InvTitle"].strip()
            
            date_created = row["InvCreationDate"]
            year, month, day = ( int(elem) for elem in date_created.split("-") )
            old_id = row["InvRefID"]
            status = row["ArtworkStatus::Status"]
            
            try:
                price = int(row["InvPrice"])
            except:
                price = 0
                
            gallery = row["GalleryLocationfor Inventory::GalName"]
            height = row["InvHeight"]
            width = row["InvWidth"]
            depth = row["InvDepth"]
            medium = row["Medium::MedMedium"]
            image_filename = row["InvImages"].split("\n")[1][28:]
            print title, "[", image_filename, "]"

            hash_name = process_image(path_to_images+image_filename)
            img = ArtImage(filename=image_filename, hash_name=hash_name)
            s.add(img)
        
            artwork = Artwork(title=title,
                              list_price= price,
                              date_created = datetime.date(year, month, day),
                              status = status,
                              medium = medium)
            artwork.image = img
            s.add(artwork)
            s.commit()
            
            
    print "processing all the images..."
    rows = s.query(Artwork).all()
    print len(rows)



if __name__ == "__main__":
    init_db()
    
    
