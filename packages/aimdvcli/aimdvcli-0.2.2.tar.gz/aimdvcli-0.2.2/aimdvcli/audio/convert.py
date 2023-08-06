import sys
import librosa
import soundfile
import os
from aquests.lib import pathtool
import tqdm

COUNT = 0
def resampling (audioFilePath, targetDir):
    global COUNT
    
    try:
        y, sr = librosa.load (audioFilePath, sr = 22050, mono = True)
    except:
        print ("- audio read failed: {}".format (audioFilePath))
        return
    
    COUNT += 1
    filename = "{:06d}.{}".format (COUNT, os.path.basename (".".join (audioFilePath.split (".") [:-1])))
    target = os.path.join (targetDir, filename + "" + ".wav")
    with open (target, "wb") as f:
       soundfile.write (f, y, 22050)       

def collect (directory, recusive = False):
    que = []
    for each in os.listdir (directory):
        if each == "AIMDV":
            continue
        path = os.path.join (directory, each)
        if os.path.isdir (path):
            if recusive:
                que.extend (collect (path, True))
            continue
        que.append (path)    
    return que
        
def usage ():
    print ("""usage: 
  aimdvcli audio [options] <source directory> [output directory]
  
options:
  -r:          recursive converting
      --help   display this screen

example:
  aimdvcli convert -r /home/ubuntu/audios ./output
    """)
    sys.exit ()

def die (msg):
    print ("error:", msg)
    sys.exit (1)
    
def parse_argv (): 
    import getopt
    try:
        argopt = getopt.getopt(sys.argv[1:], "s:o:r", ["source-dir=", "output-dir=", "help"])
    except getopt.GetoptError:
        usage ()
            
    config = {}
    for k, v in argopt [0]:
        if k == "--help":
            usage ()
        elif k == "-s" or k == "--source-dir":
            config ["source"] = v
        elif k == "-o" or k == "--output-dir":
            config ["output"] = v
        elif k == "-r":
            config ["recursive"] = True        
    
    if not config.get ("source"):
        try:
            config ["source"] = argopt [1][0]
        except IndexError:    
            usage ()
    
    try:
        config ["output"] = argopt [1][1]
    except IndexError:    
        pass    
            
    if not config.get ("source"):
        die ("required -s or --source-dir=<directory>")
    elif not os.path.isdir (config.get ("source")):
        die ("source directory not found")
    
    if config.get ("output") is None:
        config ["output"]  = os.path.join (config.get ("source"), "AIMDV")
    try:
        pathtool.mkdir (config ["output"])
    except:
        die ("cannot create output directory")    
        
    return config

def main ():
    config = parse_argv ()
    sources = collect (config ["source"], config.get ("recursive"))
    for each in tqdm.tqdm (sources):        
        resampling (each, config ["output"])
    