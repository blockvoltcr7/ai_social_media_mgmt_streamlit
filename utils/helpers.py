import csv
import os

def save_data(image, description, caption, hashtags):
    filename = "data/content.csv"
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Image', 'Description', 'Caption', 'Hashtags'])
        writer.writerow([image.name, description, caption, hashtags])
