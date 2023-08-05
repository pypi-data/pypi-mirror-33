import xml.etree.ElementTree as ET
import os
import copy
import traceback

from fixation import gen

from fixation.models import Message, MsgContent, Component, Field, Enum


def extract_xml(constructor, element):
    r = constructor()
    for tag in element:
        r.parse_value(tag.tag, tag.text)
    for attrib in element.attrib:
        r.attrib[attrib] = element.attrib[attrib]
    return r


def parse_messages(xml):
    tree = ET.parse(xml)
    root = tree.getroot()
    messages = {}
    for element in root:
        m = extract_xml(Message, element)
        messages[m.ComponentID] = m
    return {'entries': messages, 'copyright': root.attrib.get('copyright'), 'version': root.attrib.get('version')}


def parse_msgcontents(xml):
    from collections import defaultdict

    tree = ET.parse(xml)
    root = tree.getroot()

    msgcontent = defaultdict(list)

    for element in root:
        m = extract_xml(MsgContent, element)
        msgcontent[m.ComponentID].append(m)
    return {'entries': msgcontent, 'copyright': root.attrib.get('copyright'), 'version': root.attrib.get('version')}


def parse_fields(xml):
    tree = ET.parse(xml)
    root = tree.getroot()

    fields = {}

    for element in root:
        f = extract_xml(Field, element)
        fields[f.Tag] = f
    return {'entries': fields, 'copyright': root.attrib.get('copyright'), 'version': root.attrib.get('version')}


def parse_components(xml):
    tree = ET.parse(xml)
    root = tree.getroot()

    components = {}

    for element in root:
        c = extract_xml(Component, element)
        components[c.Name] = c
    return {'entries': components, 'copyright': root.attrib.get('copyright'), 'version': root.attrib.get('version')}


def parse_enums(xml):
    from collections import defaultdict

    tree = ET.parse(xml)
    root = tree.getroot()

    enums = defaultdict(list)

    for element in root:
        c = extract_xml(Enum, element)
        enums[c.Tag].append(c)
    return {'entries': enums, 'copyright': root.attrib.get('copyright'), 'version': root.attrib.get('version')}


# noinspection SqlNoDataSourceInspection
class Lookup:
    def _init_db(self):
        import sqlite3

        self._db = sqlite3.connect(":memory:")
        cur = self._db.cursor()
        cur.execute('CREATE TABLE messages (type varchar, name varchar, component_id int)')
        cur.execute('CREATE TABLE msgcontents (component_id int, tag_text varchar)')
        cur.execute('CREATE TABLE fields (tag int, name varchar)')
        cur.execute('CREATE TABLE components (component_id int, name varchar)')
        cur.close()
        self._db.commit()

    def _index(self):
        cur = self._db.cursor()
        # Insert messages
        cur.executemany('INSERT INTO messages values(?, ?, ?)',
                        [(x.MsgType, x.Name, x.ComponentID) for x in self._messages.values()])

        # Insert msgcontents
        import itertools
        cur.executemany('INSERT INTO msgcontents values(?, ?)',
                        [(x.ComponentID, x.TagText) for x in itertools.chain.from_iterable(self._msgcontents.values())])

        # Insert fields
        cur.executemany('INSERT INTO fields values(?, ?)',
                        [(x.Tag, x.Name) for x in self._fields.values()])

        # Insert components
        cur.executemany('INSERT INTO components values(?, ?)',
                        [(x.ComponentID, x.Name) for x in self._components.values()])

        cur.close()
        self._db.commit()

    def __init__(self, messages, msgcontents, fields, components, enums, **kwargs):
        self._messages = messages['entries']
        self._msgcontents = msgcontents['entries']
        self._fields = fields['entries']
        self._components = components['entries']
        self._enums = enums['entries']

        self._init_db()
        self._index()

    def msgcontents(self, id):
        result = sorted(copy.deepcopy(self._msgcontents[id]), key=lambda res: float(res.Position))

        for r in result:
            if not r.TagText.isdigit():
                r.FieldName = r.TagText
                # Is this *really* keyed by name?
                # MsgContent -TagText-> Component -ComponentID-> MsgContent?
                if not self._components[r.TagText].NotReqXML:
                    r.AbbrName = self._components[r.TagText].AbbrName
            else:
                r.FieldName = self._fields[r.TagText].Name
                # This seems backwards
                if not self._fields[r.TagText].NotReqXML:
                    if hasattr(self._fields[r.TagText], 'AbbrName'):
                        r.AbbrName = "@" + self._fields[r.TagText].AbbrName
        return result

    def fields_in(self, tag):
        result = {}

        cur = self._db.cursor()
        res = cur.execute('SELECT f.name, group_concat(c.name) '
                          'FROM fields f '
                           
                          'LEFT JOIN msgcontents mc ON f.tag == mc.tag_text '
                          'LEFT JOIN components c ON mc.component_id == c.component_id '
                           
                          'WHERE f.name = ? '
                           
                          'ORDER BY f.tag', (tag,)).fetchone()
        if res and res[1]:
            result['components'] = sorted(zip(res[1].split(','), res[1].split(',')))

        res = cur.execute('SELECT f.name, group_concat(m.name), group_concat(m.type) '
                          'FROM fields f '
                           
                          'LEFT JOIN msgcontents mc ON f.tag == mc.tag_text '
                          'LEFT JOIN messages m ON mc.component_id == m.component_id '
                           
                          'WHERE f.name = ? '
                           
                          'ORDER BY f.tag', (tag,)).fetchone()
        if res and res[1]:
            result['messages'] = sorted(zip(res[1].split(','), res[2].split(',')), key=lambda x: x[0])

        cur.close()

        return result

    def get_enums(self, tag_id):
        return self._enums.get(tag_id)


def parse_spec(path):
    messages = parse_messages(os.path.join(path, 'Messages.xml'))
    msgcontents = parse_msgcontents(os.path.join(path, 'MsgContents.xml'))
    fields = parse_fields(os.path.join(path, 'Fields.xml'))
    components = parse_components(os.path.join(path, 'Components.xml'))
    enums = parse_enums(os.path.join(path, 'Enums.xml'))

    return {
        'messages': messages,
        'msgcontents': msgcontents,
        'fields': fields,
        'components': components,
        'enums': enums
    }


def get_path(base, version):
    for path, dirs, files in os.walk(os.path.join(base, version), topdown=True):
        for f in files:
            if f == 'Messages.xml':
                return path


def render_version(base, version, conf):
    try:
        path = get_path(base, version)
        spec = parse_spec(path)
        lookup = Lookup(**spec)
        env = gen.get_env(conf)[0]
        for content in ['messages', 'components', 'fields']:
            repo = copy.deepcopy(spec[content])
            repo['type'] = content
            gen.fiximate(env, conf, content, spec[content].pop('entries'), lookup, repo)
        return "Parsed {}/{}".format(base, version)
    except:
        print("Exception while processing: %s" % version)
        traceback.print_exc()
        raise


def fiximate(base='fix_repository_2010_edition_20140507'):
    import multiprocessing as mp
    from fixation.configuration import Configuration

    try:
        ctx = mp.get_context('fork')
    except ValueError:
        ctx = mp.get_context()

    with ctx.Pool(processes=4) as p:
        for version in next(os.walk(base))[1]:
            if not version.startswith('FIX'):
                continue
            conf = Configuration.fiximate(os.path.join('out', version))

            p.apply_async(render_version, (base, version, conf), callback=print, error_callback=print)

        # We're done, shut down
        p.close()
        p.join()


def document(base):
    import json

    for version in next(os.walk(base))[1]:
        path = get_path(base, version)
        if not path:
            continue

        spec = parse_spec(path)
        lookup = Lookup(**spec)
        env, filter = gen.get_env()
        template_data = {}
        try:
            with open('document-settings.json') as fp:
                data = json.load(fp)
                if not isinstance(data, dict):
                    raise ValueError("Malformed settings, make sure it parses as a dict {}")

                filter.blacklist = data.get('blacklist', [])
                filter.whitelist = data.get('whitelist', [])
                for k, value in data.get('ctx_blacklist', {}).items():
                    filter.ctx_blacklist[k] = value
                for k, value in data.get('ctx_whitelist', {}).items():
                    filter.ctx_whitelist[k] = value
                template_data = data.get('extra_data', {})
        except IOError:
            pass

        gen.document(env, spec, version, lookup, template_data, repo={'copyright': 'me', 'version': version })


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Parse a fix repository and format it')
    parser.add_argument('--base', type=str, default='fix_repository_2010_edition_20140507',
                        help='(default: fix_repository_2010_edition_20140507)')
    parser.add_argument('--fiximate', dest='fiximate', action='store_true',
                        help='generate a fiximate-styled page')
    parser.add_argument('--document', dest='document', action='store_true',
                        help='create a HTML document suitable for becoming a PDF')
    args = parser.parse_args()
    if args.fiximate:
        fiximate(args.base)
    if args.document:
        document(args.base)


if __name__ == '__main__':
    main()
