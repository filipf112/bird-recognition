#!/usr/bin/env/python

# A script to download bird sound files from the www.xeno-canto.org archives with metadata


import urllib.request, json
import sys
import os
import ssl

# returns the Xeno Canto catalogue numbers for the given list of search terms.

# http://www.xeno-canto.org/explore?query=common+snipe
ssl._create_default_https_context = ssl._create_unverified_context

# Creates the subdirectory data/xeno-canto-dataset if necessary
# Downloads and saves json files for number of pages in a query
# and directory path to saved json's
def save_json(searchTerms):
    numPages=1
    page=1;
    #create a path to save json files and recordings
    path = "data/xeno-canto-dataset/" + ''.join(searchTerms)
    if not os.path.exists(path):
        print("Creating subdirectory " + path + " for downloaded files...")
        os.makedirs(path)
    #download a json file for every page found in a query
    while page < numPages+1:
        print("Loading page "+str(page)+"...")
        url ='https://www.xeno-canto.org/api/2/recordings?query={0}&page={1}'.format('%20'.join(searchTerms),page)
        print(url)
        jsonPage = urllib.request.urlopen(url)
        jsondata = json.loads(jsonPage.read().decode('utf-8'))
        filename= path+"/jsondata_p"+str(page)+".json"
        with open(filename, 'w') as outfile:
            json.dump(jsondata, outfile)
        #check number of pages
        numPages=jsondata['numPages']
        page=page+1
    print("Found ", numPages, " pages in total.")
    # return number of files in json
    # each page contains 500 results, the last page can have less than 500 records
    print("Saved json for ", (numPages - 1) * 500 + len(jsondata['recordings']), " files")
    return path

# reads the json and return the list of values for selected json part
# i.e. "id" - ID number, "type": type of the bird sound such as call or song
# for all Xeno Canto files found with the given search terms.
def read_data(searchTerm, path):
    data = []
    numPages=1
    page=1
    #read all pages and save results in a list
    while page < numPages+1:
        # read file
        with open(path+"/jsondata_p"+str(page)+".json", 'r') as jsonfile:
            jsondata = jsonfile.read()
        jsondata=json.loads(jsondata)
        # check number of pages
        numPages = jsondata['numPages']
        # find "recordings" in a json and save a list with a search term
        for k in range(len(jsondata['recordings'])):
            data.append(jsondata["recordings"][k][searchTerm])
        page=page+1
    return data


# downloads all sound files found with the search terms into xeno-canto directory
# into catalogue named after the search term (i.e. Apus apus)
# filename have two parts: the name of the bird in latin and ID number
def download(searchTerms):
    # create data/xeno-canto-dataset directory
    path = save_json(searchTerms)
    # get filenames: recording ID and bird name in latin from json
    filenamesID = read_data('id', path)
    filenamesGen = read_data('gen', path)
    # get website recording http download address from json
    fileaddress = read_data('file', path)
    numfiles = len(filenamesID)
    print("A total of ", numfiles, " files will be downloaded")
    for i in range(0, numfiles):
        print("Saving file ", i, "/", numfiles, ": " + filenamesGen[i] + filenamesID[i] + ".mp3")
        # Correcting the URL scheme
        urllib.request.urlretrieve(fileaddress[i], path + "/" + filenamesGen[i].replace(':', '') + filenamesID[i] + ".mp3")




def main(argv):
    if (len(sys.argv) < 2):
        print("Usage: python xcdl.py searchTerm1 searchTerm2 ... searchTermN")
        print("Example: python xcdl.py apus apus")
        return
    else:
        download(argv[1:len(argv)])


if __name__ == "__main__":
    main(sys.argv)