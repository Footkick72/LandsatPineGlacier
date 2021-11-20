# =============================================================================
#  Modified by Daniel Long from:
#  USGS/EROS Inventory Service Example
#  Description: Download Landsat Collection 2 files
#  Usage: python download_sample.py -u username -p password -f filetype
#         optional argument f refers to filetype including 'bundle' or 'band'
# =============================================================================

import json
import requests
import sys
import time
import argparse
import re
import threading
import datetime

path = "dataPineGlacier/" # Fill a valid download path
maxthreads = 5 # Threads count for downloads
sema = threading.Semaphore(value=maxthreads)
label = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") # Customized label using date time
threads = []
# The entityIds/displayIds need to save to a text file such as scenes.txt.
# The header of text file should follow the format: datasetName|displayId or datasetName|entityId. 
# sample file - scenes.txt
# landsat_ot_c2_l2|displayId
# LC08_L2SP_012025_20201215_20201219_02_T1
# LC08_L2SP_012027_20201215_20201219_02_T1
scenesFile = 'landsat_ot_c2_l2_pine_glacier.txt'
sceneFormat = "Landsat Product Identifier L2|Landsat Product Identifier L1|Landsat Scene Identifier|Date Acquired|Collection Category|Collection Number|WRS Path|WRS Row|Target WRS Path|Target WRS Row|Nadir/Off Nadir|Roll Angle|Date Product Generated L2|Date Product Generated L1|Start Time|Stop Time|Station Identifier|Day/Night Indicator|Land Cloud Cover|Scene Cloud Cover L1|Ground Control Points Model|Ground Control Points Version|Geometric RMSE Model|Geometric RMSE Model X|Geometric RMSE Model Y|Processing Software Version|Sun Elevation L0RA|Sun Azimuth L0RA|TIRS SSM Model|Data Type L2|Sensor Identifier|Satellite|Product Map Projection L1|UTM Zone|Datum|Ellipsoid|Scene Center Lat DMS|Scene Center Long DMS|Corner Upper Left Lat DMS|Corner Upper Left Long DMS|Corner Upper Right Lat DMS|Corner Upper Right Long DMS|Corner Lower Left Lat DMS|Corner Lower Left Long DMS|Corner Lower Right Lat DMS|Corner Lower Right Long DMS|Scene Center Latitude|Scene Center Longitude|Corner Upper Left Latitude|Corner Upper Left Longitude|Corner Upper Right Latitude|Corner Upper Right Longitude|Corner Lower Left Latitude|Corner Lower Left Longitude|Corner Lower Right Latitude|Corner Lower Right Longitude|Display ID|Entity ID"
wantedSceneData = ["ANG", "MTL.txt", "SR_B1", "SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7"]

# Send http request
def sendRequest(url, data, apiKey = None, exitIfNoResponse = True):  
    json_data = json.dumps(data)
    
    if apiKey == None:
        response = requests.post(url, json_data)
    else:
        headers = {'X-Auth-Token': apiKey}              
        response = requests.post(url, json_data, headers = headers)  
    
    try:
      httpStatusCode = response.status_code 
      if response == None:
          print("No output from service")
          if exitIfNoResponse: sys.exit()
          else: return False
      output = json.loads(response.text)
      if output['errorCode'] != None:
          print(output['errorCode'], "- ", output['errorMessage'])
          if exitIfNoResponse: sys.exit()
          else: return False
      if  httpStatusCode == 404:
          print("404 Not Found")
          if exitIfNoResponse: sys.exit()
          else: return False
      elif httpStatusCode == 401: 
          print("401 Unauthorized")
          if exitIfNoResponse: sys.exit()
          else: return False
      elif httpStatusCode == 400:
          print("Error Code", httpStatusCode)
          if exitIfNoResponse: sys.exit()
          else: return False
    except Exception as e: 
          response.close()
          print(e)
          if exitIfNoResponse: sys.exit()
          else: return False
    response.close()
    
    return output['data']

def downloadFile(url):
    sema.acquire()
    try:        
        response = requests.get(url, stream=True)
        disposition = response.headers['content-disposition']
        filename = re.findall("filename=(.+)", disposition)[0].strip("\"")
        wanted = False
        for name in wantedSceneData:
            if name in filename:
                wanted = True
                break
        if not wanted:
            print(f"Ignoring {filename}\n")
            sema.release()
            return
        print(f"Downloading {filename} ...\n")
        if path != "" and path[-1] != "/":
            filename = "/" + filename
        open(path+filename, 'wb').write(response.content)
        print(f"Downloaded {filename}\n")
        sema.release()
    except Exception as e:
        print(f"Failed to download from {url}. Will try to re-download.")
        sema.release()
        runDownload(threads, url)
    
def runDownload(threads, url):
    thread = threading.Thread(target=downloadFile, args=(url,))
    threads.append(thread)
    thread.start()

class Scene:
    properties = {}
    
    def __init__(self, data):
        fields = sceneFormat.split("|")
        datums = data.split("|")[1:]
        for i in range(len(fields)):
            self.properties[fields[i]] = datums[i].strip()

    def get(self, key):
        return self.properties[key]
        

if __name__ == '__main__':     
    username = "***"
    password = "***"

    print("\nRunning Scripts...\n")
    startTime = time.time()
    
    serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/stable/"
    
    # Login
    payload = {'username' : username, 'password' : password}    
    apiKey = sendRequest(serviceUrl + "login", payload)    
    print("API Key: " + apiKey + "\n")

    datasetName = "landsat_ot_c2_l2"

    #show dataset filter options
    #print(json.dumps(sendRequest(serviceUrl + "dataset-filters", {"datasetName": datasetName}, apiKey),indent=0))
    
    # Read scenes from file
    #f = open(scenesFile, "r", errors = "ignore")
    #f.readline()
    #lines = f.readlines()
    #f.close()
    #scenes = []
    #entityIds = []
    #for line in lines:
    #    s = Scene(line)
    #    scenes.append(s)
    #    entityIds.append(s.get("Entity ID"))
    

    #Get temporal filter and coordinates of wanted tiles (in this case only path 2 row 113 tile)
    #payload = {
    #            "gridType": "WRS2",
    #            "responseShape": "polygon",
    #            "path": "2",
    #            "row": "113"
    #            }
    #coordinates = sendRequest(serviceUrl + "grid2ll", payload, apiKey)['coordinates']
    #lowerLeft = coordinates[2]
    #upperRight = coordinates[1]
    #print(f"Filtering Scenes from {lowerLeft} to {upperRight}\n")
    # Search scenes 
    # If you don't have a scenes text file that you can use scene-search to identify scenes you're interested in
    # https://m2m.cr.usgs.gov/api/docs/reference/#scene-search
    # payload = { 
    #             'datasetName' : '', # dataset alias
    #             'maxResults' : 10, # max results to return
    #             'startingNumber' : 1, 
    #             'sceneFilter' : {} # scene filter
    #           }

    pathFilterID = "5e83d14fb9436d88"
    rowFilterID = "5e83d14ff1eda1b8"
    payload = {
                "maxResults": 100,
                "datasetName": datasetName,
                "sceneFilter": {
                    "spatialFilter": None,
                    "metadataFilter": {
                                        "filterType": "and",
                                        "childFilters": [
                                            {
                                                "filterId": pathFilterID,
                                                "filterType": "value",
                                                "value": "002",
                                                "operand": "="
                                            },
                                            {
                                                "filterId": rowFilterID,
                                                "filterType": "value",
                                                "value": "113",
                                                "operand": "="
                                            }
                                        ]
                                    },
                    "cloudCoverFilter": None,
                    "ingestFilter": None
                },
                "metadataType": "summary",
                "sortDirection": "ASC",
                "startingNumber": 1
            }
    
    entityIds = []
    print("Searching Scenes...\n")
    scenes = sendRequest(serviceUrl + "scene-search", payload, apiKey)
    for result in scenes["results"]:
        entityIds.append(result["entityId"])
        
    print("Found %d Scenes matching filters\n"%len(entityIds))
    
    # Add scenes to a list
    #listId = f"temp_{datasetName}_list" # customized list id
    listId = "pine_list"
    payload = {
        "listId": listId,
        "entityIds": entityIds,
        "datasetName": datasetName
    }
    
    print("Adding scenes to list...\n")
    count = sendRequest(serviceUrl + "scene-list-add", payload, apiKey)    
    print("Added", count, "scenes\n")
    
    # Get download options
    payload = {
        "listId": listId,
        "datasetName": datasetName
    }
    
    print("Getting product download options...\n")
    products = sendRequest(serviceUrl + "download-options", payload, apiKey)
    print("Got product download options\n")
    
    # Select products
    downloads = []
    filetype = "band"
    if filetype == 'bundle':
        # select bundle files
        for product in products:        
            if product["bulkAvailable"]:               
                downloads.append({"entityId":product["entityId"], "productId":product["id"]})
    elif filetype == 'band':
        # select band files
        for product in products:  
            if product["secondaryDownloads"] is not None and len(product["secondaryDownloads"]) > 0:
                for secondaryDownload in product["secondaryDownloads"]:
                    if secondaryDownload["bulkAvailable"]:
                        downloads.append({"entityId":secondaryDownload["entityId"], "productId":secondaryDownload["id"]})
    else:
        # select all available files
        for product in products:        
            if product["bulkAvailable"]:
                downloads.append({"entityId":product["entityId"], "productId":product["id"]})
                if product["secondaryDownloads"] is not None and len(product["secondaryDownloads"]) > 0:
                    for secondaryDownload in product["secondaryDownloads"]:
                        if secondaryDownload["bulkAvailable"]:
                            downloads.append({"entityId":secondaryDownload["entityId"], "productId":secondaryDownload["id"]})
    
    # Remove the list
    #payload = {
    #    "listId": listId
    #}
    #sendRequest(serviceUrl + "scene-list-remove", payload, apiKey)                
    
    # Send download-request
    payLoad = {
        "downloads": downloads,
        "label": label,
        'returnAvailable': True
    }
    
    print(f"Sending download request ...\n")
    results = sendRequest(serviceUrl + "download-request", payLoad, apiKey)
    print(f"Done sending download request\n") 
    
    
    for result in results['availableDownloads']:       
        print(f"Get download url: {result['url']}\n" )
        runDownload(threads, result['url'])
    
    preparingDownloadCount = len(results['preparingDownloads'])
    preparingDownloadIds = []
    if preparingDownloadCount > 0:
        for result in results['preparingDownloads']:  
            preparingDownloadIds.append(result['downloadId'])
  
        payload = {"label" : label}                
        # Retrieve download urls
        print("Retrieving download urls...\n")
        results = sendRequest(serviceUrl + "download-retrieve", payload, apiKey, False)
        if results != False:
            for result in results['available']:
                if result['downloadId'] in preparingDownloadIds:
                    preparingDownloadIds.remove(result['downloadId'])
                    print(f"Get download url: {result['url']}\n" )
                    runDownload(threads, result['url'])
                
            for result in results['requested']:   
                if result['downloadId'] in preparingDownloadIds:
                    preparingDownloadIds.remove(result['downloadId'])
                    print(f"Get download url: {result['url']}\n" )
                    runDownload(threads, result['url'])
        
        # Don't get all download urls, retrieve again after 30 seconds
        while len(preparingDownloadIds) > 0: 
            print(f"{len(preparingDownloadIds)} downloads are not available yet. Waiting for 30s to retrieve again\n")
            time.sleep(30)
            results = sendRequest(serviceUrl + "download-retrieve", payload, apiKey, False)
            if results != False:
                for result in results['available']:                            
                    if result['downloadId'] in preparingDownloadIds:
                        preparingDownloadIds.remove(result['downloadId'])
                        print(f"Get download url: {result['url']}\n")
                        runDownload(threads, result['url'])
    
    print("\nGot download urls for all downloads\n")                
    # Logout
    endpoint = "logout"  
    if sendRequest(serviceUrl + endpoint, None, apiKey) == None:        
        print("Logged Out\n")
    else:
        print("Logout Failed\n")  
     
    print("Downloading files... Please do not close the program\n")
    for thread in threads:
        thread.join()
            
    print("Complete Downloading")
    
    executionTime = round((time.time() - startTime), 2)
    print(f'Total time: {executionTime} seconds')
