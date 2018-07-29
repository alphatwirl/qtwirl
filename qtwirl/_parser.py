# Tai Sakuma <tai.sakuma@gmail.com>

##__________________________________________________________________||
def parse_file(file):
    if isinstance(file, str):
        if not file: # empty string, i.e., ''
            return [ ]
        return [file]
    return file

##__________________________________________________________________||
def parse_reader_cfg(reader_cfg):
    return reader_cfg

##__________________________________________________________________||
