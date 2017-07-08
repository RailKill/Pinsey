import ast
import csv
import dateutil
import glob
import os
import shutil
from datetime import datetime
from munch import munchify
from pinsey.thread.DownloadPhotosThread import DownloadPhotosThread


class LikesHandler:
    """
        Handles likes/dislikes and writes the history to a .csv file.
    """
    def __init__(self):
        self.likes_filepath = 'likes.csv'
        self.dislikes_filepath = 'dislikes.csv'
        self.photo_storage_path = '../images/'
        self.fieldnames = ['id', 'name', 'gender', 'age', 'birth_date', 'bio', 'jobs', 'schools', 'distance_km',
                           'common_connections', 'common_likes', 'date_added', 'added_by']

        # Every time the CSV files are read, the Munchy user object is stored in this history dictionary.
        self.history = {self.likes_filepath: [], self.dislikes_filepath: []}

    def like_user(self, user, owner='User'):
        # user.like()
        self._write(self.likes_filepath, user, owner)

    def dislike_user(self, user, owner='User'):
        # user.dislike()
        self._write(self.dislikes_filepath, user, owner)

    def superlike_user(self, user, owner='User'):
        # user.superlike()
        self._write(self.likes_filepath, user, owner)

    def get_likes(self):
        return self._read(self.likes_filepath)

    def get_dislikes(self):
        return self._read(self.dislikes_filepath)

    def delete_history(self, user):
        found = None
        filepath = self.likes_filepath

        for record in self.history[self.likes_filepath]:
            if record['id'] == user.id:
                found = record
                break

        if not found:
            filepath = self.dislikes_filepath
            for record in self.history[self.dislikes_filepath]:
                if record['id'] == user.id:
                    found = record
                    break

        if found:
            self.history[filepath].remove(found)
            shutil.rmtree(self.photo_storage_path + user.id, ignore_errors=True)  # Remove images for this user.
            self._rewrite(filepath)

    def _rewrite(self, filepath):
        """
            Rewrite the whole CSV file from the likes/dislikes history dictionary.

            :param filepath: Location of the CSV that stores the likes or dislikes data.
            :return: None
        """
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames, extrasaction='ignore')
            writer.writeheader()
            for user in self.history[filepath]:
                writer.writerow(user)

    def _read(self, filepath):
        """
            Reads the entire like/dislike CSV history file and returns a list of user objects.

            :param filepath: Location of the CSV file storing the like/dislike history data.
            :return: List of Munch objects (from dict) containing user data.
        """
        user_list = []
        self.history[filepath] = []

        if os.path.exists(filepath):
            with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.history[filepath].append(row)
                    user = munchify(row)
                    user.age = int(user.age)
                    user.birth_date = dateutil.parser.parse(user.birth_date)
                    user.date_added = dateutil.parser.parse(user.date_added)
                    user.distance_km = float(user.distance_km)
                    user.jobs = ast.literal_eval(user.jobs)
                    user.photos = glob.glob(self.photo_storage_path + user.id + '/*.jpg')
                    user.schools = ast.literal_eval(user.schools)
                    user.common_connections = ast.literal_eval(user.common_connections)
                    user.common_likes = ast.literal_eval(user.common_likes)

                    try:
                        user.thumb_data = open(user.photos[0], 'rb').read()
                    except IndexError:
                        # Happens if there are no images stored.
                        user.thumb_data = None

                    for i in range(len(user.photos)):
                        user.photos[i] = 'file:' + user.photos[i]
                    user_list.append(user)

        return user_list

    def _write(self, filepath, user, owner):
        """
            Appends a new user into the like/dislike CSV history data and saves their photos locally.

            :param filepath: Location of the like/dislike CSV history file.
            :param user: User to be stored.
            :return: None
        """
        def save_photos(data):
            for index, photo in enumerate(data):
                photo_path = self.photo_storage_path + user.id + '/' + str(index) + '.jpg'
                dirname = os.path.dirname(photo_path)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

                with open(photo_path, 'wb') as jpgfile:
                    jpgfile.write(photo.data)
                user.photos[index] = photo_path

            file_exists = os.path.exists(filepath)
            with open(filepath, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames, extrasaction='ignore')
                if not file_exists:
                    writer.writeheader()

                user_dict = user.__dict__
                user_dict['age'] = user.age
                user_dict['distance_km'] = user.distance_km
                user_dict['gender'] = user.gender
                user_dict['common_connections'] = user.common_connections
                user_dict['common_likes'] = user.common_likes
                user_dict['date_added'] = datetime.now()
                user_dict['added_by'] = owner
                writer.writerow(user_dict)

        # Not starting a concurrent thread, instead just using the thread's function to download photos will do.
        download_photos = DownloadPhotosThread(user.photos).download()
        save_photos(download_photos)
