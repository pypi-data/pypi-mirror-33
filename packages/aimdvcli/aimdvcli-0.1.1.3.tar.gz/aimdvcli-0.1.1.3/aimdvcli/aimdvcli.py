import sys
import os

from .audio import convert
 
def help ():
    print ("usage: aimdvcli <command> [<options>]")
    print ("command:")
    print ("  convert: convert to standard wave audio")        
    sys.exit ()
     
def main ():    
    try: 
        cmd = sys.argv [1]
    except IndexError:
        help ()        
    sys.argv.pop (1)    
    if cmd == "audio":
        cmd = "convert"
        sys.argv.pop (1)
        
    if cmd in ("convert"):
        convert.main ()    
    else:
        print ("unknown conmand")


if __name__ == "__main__":
    main ()
