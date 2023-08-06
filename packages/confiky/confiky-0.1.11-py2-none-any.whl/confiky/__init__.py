import os
from configparser import ConfigParser, SafeConfigParser
from optparse import OptionParser

class ConfikySection:
    
    def __init__(self, name):
        self.section_name = name

    def __repr__(self):
        return "<ConfikySection %s>" % self.section_name


class Confiky:

    def __init__(self, env_arg=None, cli_arg=None, files=None, required_sections=list()):
        """
        Confiky evalutes settings source with this order:
        1) env_arg: check for environment variable with provided name
        2) cli_arg: pass --cli_arg (cli_arg as you define) to the main script or who start Confiky
        3) files: list or string of file path.
        """
        cfile = []

        if env_arg:
            if not isinstance(env_arg, list):
                env_arg = [env_arg]

            for el in env_arg:
                try:
                    cfile.append(os.environ[el])
                except KeyError:
                    pass

        if cli_arg:
            if not isinstance(cli_arg, list):
                cli_arg = [cli_arg]

            parser = OptionParser()
            for el in cli_arg:
                parser.add_option("--%s" % el)

            (options, args) = parser.parse_args()

            for el in cli_arg:               
                if hasattr(options, el):
                    cfile.append(getattr(options, el))

        if files:
            if not isinstance(files, list):
                if ',' in files:
                    els = list()
                    for f in files.split(','):
                        cfile.append(f)
                
                else:
                    cfile.append(files)
            else:
                cfile += files
            
        if not cfile:
            raise ValueError

        config = SafeConfigParser()
        config.optionxform = str

        self.files = cfile
        self.file_count = len(cfile)
        self.sections = list()

        for f in cfile:
            try:
                config.read(f)
            except Exception as e:
                raise ValueError('Unable to find %s file in the root folder and no custom file path provided.' % f)

            self.config = config

            sections = required_sections or config.sections()
            for section_name in sections:
            
                if hasattr(self, section_name):
                    section = getattr(self, section_name)
                    section.__dict__.update(config.items(section_name, raw=True))
                else:
                    section = ConfikySection(name=section_name)
                    setattr(self, section_name, section)
                    section = getattr(self, section_name)
                    section.__dict__.update(config.items(section_name, raw=True))
            
                self.sections.append(section)
            
            self.sections = list(set(self.sections))

    def __repr__(self):
        if self.file_count == 1:
            return "<Confiky for %s>" % self.files[0]

        return "<Confiky for %s files>" % self.file_count

    def validate(self, sections=list(), fields=list()):
        """ Check if provided sections or fields is present in 
        the configuration object """
        sections_found = 0
        fields_found = 0
        all_found = False
        
        if sections and isinstance(sections, list):
            for s in sections:
                if hasattr(self, s):
                    sections_found += 1

            if sections_found == len(sections):
                section_all = True

        if fields and isinstance(fields, list):
            for f in fields:
                if hasattr(self, f):
                    fields_found += 1

            if fields_found == len(fields):
                fields_all = True

        if section_all and fields_all:
            all_found = True

        return dict(fields_found=fields_found, sections_found=sections_found, all_found=all_found)


    def is_valid(self, sections=list(), fields=list()):
        if self.validate(sections=sections, fields=fields):
            return True
    
        return False

    def explain(self):
        ddict = dict()
        for s in self.sections:
            csection = getattr(self, s.section_name)
            ddict[s] = csection.__dict__

        return ddict


if __name__ == '__main__':
    c = Confiky(env_arg='testme', cli_arg='settings', files='../../openerp.modernapify/settings.ini')
    print(c)
    print(c.files)
    print(c.sections)
    print(c.explain())

