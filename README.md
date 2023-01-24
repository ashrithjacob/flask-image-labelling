# flask-image-labelling

Creating a simple UI to label images

# TODO:

1. feature to drag and drop images ("/" )
2. feature to add labels and save ("/labels")
3. feature to toggle between images, assigning label to each image ("/
   toggle")
4. export csv:

- Create labels folder in "static/"
- Create labels.yaml file inside with index to label mapping like below:
  classes:
  0: label_1
  1: label_2
  2: label_3
- create .txt files of same name as files in "uploads/"
- fill each .txt file with a binary array: 0; 1; 1
  TODO:
  - how to remove labels
  - make labelling more user firendly by displaying all icons (highlight buttons)
  - beautify html and clean up labelling
  - use request.url
