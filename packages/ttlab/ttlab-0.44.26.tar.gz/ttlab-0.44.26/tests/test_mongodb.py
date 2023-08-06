import sys
import matplotlib.pyplot as plt

# %matplotlib notebook
sys.path.append('..')
#
from ttlab import DBConnection
from ttlab import Templates
from ttlab import XPS
from ttlab import Sample

URI = 'mongodb://johan:j0hant3nghamn@129.16.112.214:27017/samples'
collection = 'sandbox'
database_name = 'samples'
db = DBConnection(URI, database_name, collection)

# print(dir(db.db))
# print(db.db.collection_names())
sample_info = {
    'name': 'test_sample',
    'history': [
        {
            'date': '180624',
            'description': 'production'
        },
        {
            'date': '180625',
            'description': 'annealing'
        }
    ]
}

sample = Sample()
sample.set_name('ttlab test sample')
sample.set_owner('ttlab')
sample.set_fabrication_date('180627')
sample.set_description('ttlab test sample')


sample.print_metadata()
a = db.upload_sample(sample)

uploaded_sample = db.get_sample(a)

uploaded_sample.print_metadata()

event = {
    'description': 'xps',
    'date': '180627'
}
db.add_event_to_sample_history(a, event)

updated_sample = db.get_sample(a)

updated_sample.print_metadata()

#sample_info = Templates.get_alloy_template()

#sample_info['name'] =

#print(db.get_history_for_sample(1))

#print(db.sample_identifier_exists(1067))
#filepath = 'mock_data/downloads/'
#id = '5b30d75d7838c425dab8c249'

#gridfs_file = db.get_gridfs_file(id)
#xps = XPS(gridfs_survey_file=gridfs_file)
#print(dir(xps))
#print(xps.survey_data.energy)

#db.download_measurement_to_path(id,filepath)
#db.upload_measurement(filepath, sample_identifier=1, date='180612', description='xps')
# inserted_document = db.insert_new_sample(sample_info)
# print(inserted_document)
