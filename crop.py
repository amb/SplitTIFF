import argparse
import numpy as np

from osgeo import gdal
from PIL import Image

# python .\crop.py -i LOLA_DEM.tiff -o hi-res -p

rescale = 4
resolution = 1024

gdal.UseExceptions()

parser = argparse.ArgumentParser()

parser.add_argument("-i", type=str)
parser.add_argument("-o", type=str)
parser.add_argument("-p", "--preview", action="store_true")

args = parser.parse_args()

if args.i is not None and args.o is not None:
    print("Input:", args.i, " Output:", args.o)
    Image.MAX_IMAGE_PIXELS = 250000000

    # Load dataset with GDAL
    dataset =  gdal.Open(args.i, gdal.GA_ReadOnly)
    data = dataset.ReadAsArray()

    print(data.shape, data.dtype)
    print(np.max(data), np.min(data))

    data -= np.min(data)
    data = np.float64(data)
    data /= np.max(data)
    data = np.int16(32768 * data)

    print(np.max(data), np.min(data))

    # Convert to PIL Image
    #img = Image.open(args.i)
    img = Image.fromarray(data)
    
    width, height = img.size
    #print("Image size:", width, height)

    fres = resolution * rescale

    con_table = [j/256 for j in range(65536)]

    if width > fres and height > fres:
        for x in range(0, 10):
            for y in range(0, 10):
                left = x*fres
                top = y*fres
                right = left+(fres-1)
                bottom = top+(fres-1)

                if right >= width or bottom >= height:
                    continue

                print("")
                print("Tile:", x, y)

                print("Cropping...")
                piece = img.crop((left, top, right, bottom))

                print("Resizing...")
                piece = piece.resize((resolution, resolution), Image.ANTIALIAS)

                fname = args.o+"_"+repr(x)+"_"+repr(y)

                if not args.preview:
                    otext = piece.tobytes('raw')

                    print("Preparing...")
                    ntext = bytes([val for pair in zip(otext[0::4], otext[1::4]) for val in pair])

                    print("Saving...")
                    with open(fname+".raw", "wb") as out_file:
                        out_file.write(ntext)
                else:
                    #tarr = np.asarray(piece)
                    #print(np.max(tarr), np.min(tarr))
                    #piece = piece.convert('RGB')
                    piece = piece.point(con_table, 'L')
                    piece.save(fname+".png")
    else:
        print("Image too small to be cropped from with size ", resolution)

