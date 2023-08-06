from xmltodict import parse


class Parsers:
    def groups(self, data):
        group_dict = {}
        for i in parse(data)['Packet']['DatabaseManager']['ControlGroup']['MnetList']['MnetRecord']:
            group_dict[i['@Group']] = {
                'number': i['@Group'],
                'name_web': i['@GroupNameWeb'],
                'name_lcd': i['@GroupNameLcd']
            }
        return group_dict

    def bulk_from_single(self, data):
        return parse(data)['Packet']['DatabaseManager']['Mnet']['@Bulk']

    def all_basic_info(self, data, domain):
        new_data = parse(data)['Packet']['DatabaseManager'][domain]
        return_data = {}
        for i in new_data.keys():
            return_data[i[1:]] = new_data[i]
        return return_data

    def current_drive(self, data):
        return parse(data)['Packet']['DatabaseManager']['Mnet']['@Drive']
