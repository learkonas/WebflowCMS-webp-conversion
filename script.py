import requests
import csv
import pandas as pd
import time
import cloudinary
import cloudinary.uploader

## POPULATE THESE SEVEN VARIABLES
Webflow_Bearer_Token = "YOUR_TOKEN_HERE"     # log in to Webflow via the 'Authenticate' button on this page to get your Bearer token: https://docs.developers.webflow.com/reference/authorized_by
Webflow_Collection_Id = "Collection_ID_HERE" # navigate to your collection settings in the Webflow CMS and locate your Collection ID. It should be a 24-character alpha-numeric string. Go here for assistance: https://www.briantsdawson.com/blog/webflow-api-how-to-get-site-collection-and-item-ids-for-zapier-and-parabola-use
Name_Of_Asset_Field = 'NAME_HERE'            # in your CMS Collection, what is the name of the asset field which holds your image. For example, it might be 'Preview Image' or 'Hero Image'. Convert the name to lower case and replace every space with a dash, like 'preview-image' or 'hero-image'
New_Asset_Field = 'NAME_HERE'                # create a new field in your CMS Collection, and again make it lower case and replace spaces with dashes. If you wish, you can overrwite the above field by naming this variable the same as the above, but this is not recommended because it would delete a backup that would be needed in the event something went wrong.
CollectionSize = PUT_A_NUMBER_HERE           # number of items in your collection, round up to the nearest hundred
CloundinaryKey = "API_KEY_HERE"
CloundinarySecret = "API_SECRET_HERE"
    # to find your Cloudinary authentication API access keys, make an account and go to this page: https://console.cloudinary.com/settings/c-d07518079a66f742ecc00f45ba5fe7/api-keys
CloundinaryCloud = "Cloud_Name_HERE"
    # your Cloud Name should be listed under Product Environments here: https://console.cloudinary.com/settings/c-d07518079a66f742ecc00f45ba5fe7/account

postIDs = []
options = { 'headers': {
    'accept': 'application/json',
    'authorization': f"Bearer {Webflow_Bearer_Token}" }}
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {Webflow_Bearer_Token}"
}
cloudinary.config( 
  cloud_name = CloundinaryCloud, 
  api_key = CloundinaryKey, 
  api_secret = CloundinarySecret
)

def fullProcess():                        # this will run all of the code below. You'll need to uncomment the last line in each of the functions (including this one) to proceed to each next step
    print("Beginning the full process.")
    #fetchItems()

def fetchItems():                         # this finds the collection item ID for each item in your collection
    for round in range(0, CollectionSize, 100): #Webflow is rate limited to 100 items per Fetch; this line runs the Fetch request the appropriate amount of times, based on your CollectionSize
        urlPost = f"https://api.webflow.com/v2/collections/{Webflow_Collection_Id}/items?offset={round}"
        response = requests.get(urlPost, **options)     # the response will be a list of Objects, one Object containing the data for each collection item
        json_data = response.json()                 
        for item in json_data['items']:                 
            postIDs.append(item['id'])                  # adds the postID from each Object (corresponding to one collection item) to an array
    with open('postIDs.csv', 'w', newline='') as f:     # creates a new CSV file called postIDs; it will overrwrite any other file with the same name in the same location
        writer = csv.writer(f)                          
        writer.writerow(['postIDs'])                    # the first cell will be called 'postIDs'
        for id in postIDs:                              # the list of postIDs will be added in the column beneath it
            writer.writerow([id])
    #fetchImageAssetURLS()                              # remove the # comment if you want the code to automatically run the next step

def fetchImageAssetURLS():                    # this finds the URL of the specified image asset (from line 11) in each collection item
    df = pd.read_csv('postIDs.csv')                     # this will load the postIDs.csv you generated in the above function
    for index, row in df.iterrows():                    # we will run through every row (except the top index row), ie through every collection item
        failed = False                                                                              # fresh start, this search hasn't failed (yet)
        post_id = row['postIDs']                                                                    # finds the correct postID
        url = f"https://api.webflow.com/v2/collections/{Webflow_Collection_Id}/items/{post_id}"     # adds that postID to the API request
        while True:                                                                                 # runs until the break command on line 67 is hit
            response = requests.get(url, **options)                                                 # makes the Fetch request to Fetch data on the Collection item with that specific post ID
            json_data = response.json()
            if json_data.get('fieldData', {}).get(Name_Of_Asset_Field):                             # checks to see if we successfully found the specified Asset
                df.at[index, 'ImageAsset'] = json_data['fieldData'][Name_Of_Asset_Field]['url']     # adds the Webflow URL of that image asset to a list
                if failed == True:                                                                  # if the search had previously failed...
                    print(f"Succeed for post_id {post_id}.")                                            # ...then print a line to say that the search on this specific collection item has now succeeded
                    failed = False                                                                      # and set failed to False
                break                                         # exit the while loop if ImageAsset URL is found
            else:
                failed = True                                                               # if we don't find the Image Asset, then try again
                print (response.text)                                                       # prints the response to help diagnose the problem
                print(f"Rate limit: {response.headers['X-Ratelimit-Remaining']}")           # a potential problem is you hit the rate limit
                waitTime = 5                                                                # this code instigates a pause of 5 seconds (waitTime = 5) and will retry.
                for i in range(waitTime, 0, -1):
                    print(f"Failed for post_id {post_id}, retrying in {i} seconds...")
                    time.sleep(1)                                                           # if you have done something wrong with the code, then this delay-and-retry tactic will not work. You will have to Cmd/Ctrl + C to kill the script running and diagnose the error.
    df.to_csv('postIDs.csv', index=False)                                                   # once you have gone through every Collection item, overrwrite the postIDs.csv with a new doc containing the original postIDs, but also the Image Asset URLs
    #webpFiltering()                                                # remove the # comment if you want the code to automatically run the next step

def webpFiltering():                    # this creates a new file focused on the collection items where the image asset is not a webp image (these are the only ones that matter)                                                
    df = pd.read_csv('postIDs.csv')                                 # downloads the postIDs.csv (and converts to a dataframe)
    df = df.dropna(subset=['ImageAsset'])                           # filters out lines (Collection items) where no ImageAsset URLs were found
    df = df[~df['ImageAsset'].str.endswith('.webp')]                # filters out lines (Collection items) where the ImageAsset is already a webp file (no need to convert these!)
    df.to_csv('noWEBP.csv', index=False)                            # creates a new csv called noWEBP.csv
    #convertToWebp()                                    # remove the # comment if you want the code to automatically run the next step

def convertToWebp():                    # this converts all images to webp
    df = pd.read_csv('noWEBP.csv')                      # downloads the noWEBP.csv (and converts to a dataframe)
    for index, row in df.iterrows():                    # we will run through every row (except the top index row), ie through every collection item
        imageURL = row['ImageAsset']                    # finds the correct image asset URL
        try:
            result = cloudinary.uploader.upload(imageURL, format='webp')    # uses the Cloundinary API to convert images to webp
            if 'secure_url' in result:                                      # Cloundinary should return a result called 'secure-url'
                webpURL = result['secure_url']                                  # this URL is our webpURL for the image asset!
                df.at[index, 'webpURL'] = webpURL                           # let's add that to a column next to the orignal Image Asset
            else:
                print("secure-url not found in result.")                    # if there is no secure-url but we do get a result back from Cloudinary
                print(result)                                               # print the result so we can have a look at it
        except Exception as e:                                              # if there are any problems with the code in the 'try' section...
            print(f"An error occurred: {e}")                                    # then print the error message too
    df.to_csv('noWEBP.csv', index=False)                                # after we have run through every row (line 86), overrwite the noWEBP.csv with the original data, plus a webp URL for each image asset
    #upgradeToWebp()                                    # remove the # comment if you want the code to automatically run the next step

def upgradeToWebp():                    # this updates the image asset in each collection item with the new webp URL
    df = pd.read_csv('noWEBP.csv')                                                  # downloads the noWEBP.csv (and converts to a dataframe)
    print("Successfully loaded the webp URLs. Commencing updates to Webflow.") 
    for index, row in df.iterrows():                                                # we will run through every row (except the top index row), ie through every collection item
        post_id = row['postIDs']                                                    # pick up the relevant collection item ID
        webpURL = row['webpURL']                                                    # pick up the relevant webp image asset URL
        url = f"https://api.webflow.com/v2/collections/{Webflow_Collection_Id}/items/{post_id}"     
        payload = {
            "isArchived": False,
            "isDraft": False,
            "fieldData": { New_Asset_Field: webpURL }               # this is what adds the webp URL of the image to the New_Asset_Field you created
        }
        failed = False                                              # fresh start, we haven't failed on this one yet
        while True:                                                 # runs until hitting the break on line 133
            response = requests.patch(url, json=payload, headers=headers)
            if int(response.headers['X-Ratelimit-Remaining']) < 20:             # if the rate limit gets too low, then we wait 5 seconds
                waitTime = 5
                failed = True
                for i in range(waitTime, 0, -1):
                    print(f"Approached rate limit at post_id {post_id}, waiting for {i} seconds...")
                    time.sleep(1)
            json_data = response.json()
            if json_data.get('fieldData', {}).get(New_Asset_Field, {}).get('url'):                                  # if we successfully added the webp URL to the New_Asset_Field, then this part runs
                df.at[index, 'newWebpURL'] = json_data.get('fieldData', {}).get(New_Asset_Field, {}).get('url')         # add the new webp URL (it will have 'webflow' in it) to a new column called newWebpURL
                if (index + 1) % 10 == 0:                                                                           # progress update on every 10 items updated
                    print(f"{index+1} banner images have been updated so far, with {df.shape[0]-index} remaining.") 
                    print(f"Rate limit stands at: {response.headers['X-Ratelimit-Remaining']}")
                if failed == True:                                                                                  # if we previously failed on an item, then print a success message for when we succeed
                    print(f"Succeed for post_id {post_id}.")
                    failed = False
                break                                                                                               
            else:
                failed = True                                                                   # if we fail, then...
                waitTime = 5                                                                    
                print(response.text)                                                                # ...print the response
                for i in range(waitTime, 0, -1):                                                    # wait 5 seconds
                    print(f"Failed for post_id {post_id}, retrying in {i} second(s)...")        # if the problem is not a rate limiting problem, you will need to kill the script run and diagnose the issue
                    time.sleep(1)
    df.to_csv('upgradeToWEBP.csv', index=False) # create a new CSV with: the ID of every collection item you changed, the image asset URL you are replacing, the webp URL from Cloundinary, and the new webflow URL (newWebpURL)


#fetchItems()
#fetchImageAssetURLS()
#webpFiltering()
#convertToWebp()
#upgradeToWebp()

#fullProcess()


