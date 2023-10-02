# Webflow webp converter
This script will convert images in a specific asset field on your Webflow CMS to the efficient .webp format.
## Installation and Set-up
Run `pip install -r requirements.txt` to install dependencies.<p>
To clone this repository, run `git clone https://github.com/learkonas/WebflowCMS-webp-conversion`
### Webflow
You will need some familiarity with the Webflow CMS to add the relevant Webflow variables for your collection and the asset field you want to update.
### Cloudinary
The script uses Cloundinary to convert images to Webp. You will need to create a free account and get API credentials. Once you have an account, you can get the API credentials [here](https://console.cloudinary.com/settings/c-d07518079a66f742ecc00f45ba5fe7/api-keys) and your Cloudinary Cloud Name [here](https://console.cloudinary.com/settings/c-d07518079a66f742ecc00f45ba5fe7/account).
### Steps
- Step 1: find all collecton item IDs within a collection (`fetchItems()`)
- Step 2: for each collection item, fetch the image asset URL that you would like to convert (`fetchImageAssetURLS()`)
- Step 3: split image assets between those already in the webp format and those needing converting (`webpFiltering()`)
- Step 4: convert the non-webp images to webp using Cloudinary (`convertToWebp()`)
- Step 5: populate the specified asset field with the new Cloudinary webp URLs or the original webp URL (if one existed)

