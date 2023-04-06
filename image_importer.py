import glob
import sqlite3
images = glob.glob('images/*.jpg')

connection = sqlite3.Connection("images.db")
images_inserted = 0

for image in images:
    filename = image.split("/")[1]
    name = (" ".join(filename.split('-')[0:-1]))

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM images WHERE path = ?", (image,))
    output = cursor.fetchall()

    if len(output) == 0:
        #no file found
        print("inserting new file")
        cursor.execute("INSERT INTO images (name, path) VALUES (?,?)", (name, image))
        connection.commit()
        images_inserted += 1
connection.close()
print("{0} images inserted".format(images_inserted))
        