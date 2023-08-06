import pprint


class Sample:

    def __init__(self,meta=None):
        self.metadata = {
            'owner': None,
            'identifier': None,
            'batch_nr': None,
            'name': None,
            'history': [],
            'description': None,
            'extra': None
        }
        if meta is not None:
            self._add_meta_info(meta)

    def set_name(self,name):
        self.metadata['name'] = name

    def set_owner(self,owner):
        self.metadata['owner'] = owner

    def set_identifier(self,identifier):
        self.metadata['identifier'] = identifier

    def set_batch_nr(self,batch_nr):
        self.metadata['batch_nr'] = batch_nr

    def set_description(self,description):
        self.metadata['description'] = description

    def set_extra(self,extra):
        self.metadata['extra'] = extra

    def set_fabrication_date(self,date):
        self.metadata['history'].append(
            {
                'description': 'fabrication',
                'date': date
            }
        )

    def get_name(self):
        return self.metadata['name']

    def get_owner(self):
        return self.metadata['owner']

    def get_identifier(self):
        return self.metadata['identifier']

    def get_batch_nr(self):
        return self.metadata['batch_nr']

    def get_description(self):
        return self.metadata['description']

    def get_extra(self):
        return self.metadata['extra']

    def get_fabrication_date(self):
        for event in self.metadata['history']:
            if 'description' in event and event['description'] is 'fabrication':
                return event['date']
        return None

    def get_history(self):
        return self.metadata['history']

    def add_event_to_history(self,event):
        self.metadata['history'].append(event)

    def print_metadata(self):
        print('\n')
        pprint.pprint(self.metadata)
        print('\n')

    def print_history(self):
        history = self.get_history()
        sorted_history = self._sort_history_on_date(history)
        print('-' * 60)
        for index, event in enumerate(history):
            print('\n' + str(index) + '.')
            for key in event:
                print(key + ': ' + str(event[key]) + '\n')
        print('-'*60)

    def get_metadata(self):
        return self.metadata

    def is_valid_sample(self):
        return False

    def _add_meta_info(self,meta):
        for key in meta:
            if key in self.metadata:
                self.metadata[key] = meta[key]

    @staticmethod
    def _sort_history_on_date(history):
        sort_on = "date"
        sorted_history = sorted(history, key=lambda k: k[sort_on])
        return sorted_history





