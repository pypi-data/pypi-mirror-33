from pymongo import MongoClient
import gridfs
import ntpath
from bson.objectid import ObjectId
from ttlab.sample import Sample


class DBConnection:

    def __init__(self, URI, database_name, collection):
        self.mongo_client = MongoClient(URI)
        self.db = self.mongo_client[database_name][collection]
        self.fs = gridfs.GridFS(self.mongo_client[database_name])

    def upload_sample(self, sample):
        if not isinstance(sample, Sample):
            raise ValueError('Not a valid sample. Must be an instance of ttlab Sample class.')
        sample.set_identifier(self._create_unique_identifier())
        self.db.insert_one(sample.get_metadata())
        print(sample.get_identifier())
        return sample.get_identifier()

    def get_sample(self, identifier):
        if self._sample_identifier_exists(identifier):
            return Sample(self.db.find_one({'identifier': identifier}))

    def add_event_to_sample_history(self, identifier, event):
        sample = self.get_sample(identifier)
        sample.add_event_to_history(event)
        self.update_sample(identifier, sample)

    def update_sample(self, identifier, sample):
        self.db.update({'identifier': identifier}, sample.get_metadata())

    def upload_measurement(self, filepath, sample_identifier, date, description, encoding='UTF-8'):
        if not self._sample_identifier_exists(sample_identifier):
            raise ValueError('Sample identifier: ' + str(sample_identifier) + ' do not exist')
        file = open(filepath, 'rb')
        file_meta = {
            'encoding': encoding,
            'description': description,
            'date': date,
            'sample_identifier': sample_identifier,
            'name': self._extract_filename_from_path(filepath)
        }
        uploaded_file_id = self.fs.put(data=file.read(), **file_meta)
        history_event = {
            'description': description,
            'date': date,
            'file_id': uploaded_file_id,
            'name': file_meta['name']
        }
        self.add_event_to_sample_history(sample_identifier, history_event)

    def _sample_identifier_exists(self, sample_identifier):
        if self.db.find_one({'identifier': sample_identifier}) is None:
            return False
        return True

    def download_measurement_to_path(self, id, path):
        meta_info = self.fs._GridFS__files.find_one({'_id': ObjectId(id)})
        grid_file = self.fs.find_one({'_id': ObjectId(id)})
        local_file = open(path + meta_info['name'], 'wb')
        local_file.write(grid_file.read())
        local_file.close()

    def _extract_filename_from_path(self, path):
        return ntpath.basename(path)

    def get_gridfs_file(self, id):
        return self.fs.find_one({'_id': ObjectId(id)})

    def _create_unique_identifier(self):
        docs = self.db.find().sort([('identifier', -1)])
        if docs.count() == 0:
            return 1
        if 'identifier' not in docs[0]:
            return 1
        return docs[0]['identifier'] + 1
