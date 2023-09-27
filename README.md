# Webflow webp converter
This script will convert images in a specific asset field on your Webflow CMS to the efficient .webp format.
### Webflow
You will need some familiarity with the Webflow CMS to added the relevant Webflow variables for your collection and the asset field you want to update.
### Cloundinary
The script uses Cloundinary to convert images to Webp. You will need to create a free account and get API credentials, but the script explains how to do this and it is not difficult.
### Steps
- Step 1: find all collecton item IDs within a collection (fetchItems())
- Step 2: for each collection item, fetch the image asset URL that you would like to convert (fetchImageAssetURLS())
- Step 3: remove collection items for which the image asset is already in the webp format (webpFiltering())
- Step 4: convert the non-webp images to webp using Cloudinary (convertToWebp())
- Step 5: populate the specified asset field with the Cloudinary webp URLs

