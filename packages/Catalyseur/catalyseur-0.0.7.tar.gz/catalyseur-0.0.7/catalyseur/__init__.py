from multiprocessing import Pool
import time
import os  
import requests
import json
import urllib.request


try:
    os.stat(".daemon") 
    os.chdir("..")
except:
    print("0")


DR = os.getcwd()


try:
    os.mkdir("Catalyseur") 
    os.mkdir("Catalyseur/.daemon")
except:
    print("0")


file = open("Catalyseur/.daemon/last_action","w")
file.write("0")
file.close()
file = open("Catalyseur/.daemon/last_save","w")
file.write("0")
file.close()
file = open("Catalyseur/.daemon/code","w")
file.write("0")
file.close()
    
    
    
def f(x):
    
    os.chdir(DR)
    
    time.sleep(20)
    while(True):
        time.sleep(10)
        
        # Replace the last action
        ts = time.time()
        file = open("Catalyseur/.daemon/last_action","w")
        file.write(str(ts))
        file.close()
    
        # Get the last save time 
        file = open("Catalyseur/.daemon/last_save", "r") 
        tsr = float(file.read())
        
        # Get the last file modif
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat("Catalyseur/Code.py")
        
        if( abs(mtime-tsr)>5 ):
            save(mtime)
            
    return 0


def save(mtime):
    
    os.chdir(DR)
    
    # Save the new modification time
    file = open("Catalyseur/.daemon/last_save","w")
    file.write(str(mtime))
    file.close()

    # Get the current code
    file = open("Catalyseur/.daemon/code","r") 
    code = file.read()
            
    alldata = {'data':code}
    allfiles = dict({})
    allfiles["1"] = open("Catalyseur/Code.py")
    requests.post("http://gcb202.espaceweb.usherbrooke.ca/cloud_server_save.php",data=alldata,files=allfiles)
        

def main(code):
    
    os.chdir(DR)
    
    # If already in use... send the current version
    file = open("Catalyseur/.daemon/code","r") 
    code_old = (file.read())
    if(code_old != "0"):
        save(0)
    
    
    # Check if the daemon is in use
    ts = time.time()
    file = open("Catalyseur/.daemon/last_action", "r") 
    tsr = float(file.read())
    if( (ts-tsr)>45 ):  # If not in use, start it
        pool = Pool(processes=1)
        pool.apply_async(f, [20])
    
        
    # Download the requested file
    alldata = {'data':code}
    r = requests.post("http://gcb202.espaceweb.usherbrooke.ca/cloud_server_open.php",data=alldata)
    code_contents = r.content.decode('utf-8')
    file = open("Catalyseur/Code.py","w")
    file.write(code_contents)
    file.close()
    
    # Replace the last save
    file = open("Catalyseur/.daemon/last_save","w")
    file.write(str(ts))
    file.close()
    
    # Replace the last action
    file = open("Catalyseur/.daemon/last_action","w")
    file.write(str(ts))
    file.close()
    
    # Save the code
    file = open("Catalyseur/.daemon/code","w")
    file.write(code)
    file.close()
    
    curdir =  os.getcwd()
    curdir = curdir.replace("\\", "/")
    
    print(" ")
    print(" ")
    print("Travaillez sur votre code en ouvrant "+curdir+"/Catalyseur/Code.py")
    print("==================================")
    print("Ce script se téléversera directement sur Catalyseur.ca dès qu'une modification est enregistrée sur votre ordinateur.")
    print("Ce téléversement automatique est valide pour les 2 prochaines heures, tant que la console actuelle n'est pas fermée et qu'une connexion Internet est établie sur votre ordinateur.")
    print("En utilisant le module Catalyseur pour Python3, vous acceptez que le contenu de 'Code.py' soit téléversé sur les serveurs de l'Université de Sherbrooke. Si vous refusez, veuillez fermer la console actuelle et ne pas réutiliser ce module.")
    print("==================================")
        
        # Download the joined file
    if (code != "0"):
        count = 0
        alldata = {'data':code}
        r = requests.post("http://gcb202.espaceweb.usherbrooke.ca/cloud_server_get_joined_files.php",data=alldata)
        s = r.content.decode('utf-8')
        jdata = json.loads(s)
        for jf in jdata:
            filename = "Catalyseur/" + jf[0]
            urllib.request.urlretrieve(jf[1],filename)
            count = count + 1
        if(count==1):
            print("1 fichier supplémentaire a été téléchargé pour cet exercice.")
            print("Il se trouve dans le même répertoire que votre code de travail.")
        elif(count>1):
            print("%.0f fichiers supplémentaires ont été téléchargé pour cet exercice." % count)
            print("Ils se trouvent dans le même répertoire que votre code de travail.")
        



if __name__ == '__main__':
    main("0")
    
