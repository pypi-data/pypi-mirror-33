import os
from jinja2 import Environment, FileSystemLoader, PackageLoader, ChoiceLoader, select_autoescape, evalcontextfilter, Markup
from fixation import jinja_filters


class Stylify:
    def __init__(self, conf):
        self.conf = conf

    @evalcontextfilter
    def linkify(self, eval_ctx, obj):
        result = "../{}.html".format(self.conf.get_http_path(obj))
        if eval_ctx.autoescape:
            return Markup(result)
        return result


def get_env(conf=None, jfilter=jinja_filters.Filter()):
    loaders = ChoiceLoader([
        FileSystemLoader(['.', 'templates']),
        PackageLoader('fixation'),
    ])
    env = Environment(
        loader=loaders,
        autoescape=select_autoescape(['html'])
    )

    if conf:
        stylify = Stylify(conf)
        env.filters['linkify'] = stylify.linkify

    env.tests['blacklisted'] = jfilter.is_blacklisted
    env.tests['whitelisted'] = jfilter.is_whitelisted

    env.tests['component'] = jinja_filters.is_component
    env.tests['message'] = jinja_filters.is_message
    env.tests['field'] = jinja_filters.is_field

    return env, jfilter


def fiximate(env, conf, subdir, input, lookup, repo):

    path = conf.get_paths(subdir)
    os.makedirs(path, exist_ok=True)

    if isinstance(input, dict):
        entries = input.values()
    else:
        # probably a list
        entries = input

    write_index(entries, env, lookup, path, repo, subdir)
    write_entries(conf, entries, env, lookup, path, repo, subdir)


def write_index(entries, env, lookup, path, repo, subdir):
    template = env.select_template(['index_{}.html'.format(subdir), 'index.html'])

    template.stream(entries=entries, lookup=lookup, repository=repo) \
        .dump(os.path.join(path, 'index.html'), encoding='utf-8')


def write_entries(conf, entries, env, lookup, path, repo, subdir):
    template = env.select_template([subdir + '.html', 'messages.html'])
    for entry in entries:
        filename = '{}.html'.format(conf.get_filename(entry))

        template.stream(entry=entry, lookup=lookup, repository=repo)\
            .dump(os.path.join(path, filename), encoding='utf-8')


def document(env, input, version, lookup, template_data, repo):

    path = os.path.join('out', version)
    os.makedirs(path, exist_ok=True)

    template = env.get_template('document.html')

    messages = input['messages']['entries']
    components = input['components']['entries']

    template.stream(messages=messages.items(), message_list=messages.values(),
                    components=components.items(), component_list=components.values(),
                    lookup=lookup, repository=repo, **template_data)\
        .dump(os.path.join(path, 'document.html'), encoding='utf-8')
