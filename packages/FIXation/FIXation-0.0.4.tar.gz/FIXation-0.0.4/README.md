Generate nice looking documents from your FIX repository.

### Command-line interface

`fix-parse [--base fixation/fix_repository_2010_edition_20140507] [--document] [--fiximate]`

`--base` points to where you're storing your fix repository.

`--document` generates a single-page document.html suitable for turning into a pdf.

`--fiximate` generates fiximate-styled pages, suitable for online-publishing.

### Using your own templates

The core of fixation is centered around Jinja2 templates, before you begin you should bookmark [http://jinja.pocoo.org/docs/2.10/templates/] contains well-written and easy to follow documentation on how to write templates.

Now the easiest way to get started is to copy the templates/ folder into your current working directory, there are a few base templates which contain the generic structure and then more specific templates which extends the bases.

### Writing templates

In the case of `--fiximate` you'll have a `repository` which will tell you what `type` you're handling, the `copyright` and `version`

You also have access to the Jinja2 filter `linkify` (which gives you a relative link to the item) and the tests `messages`, `field`, `component`, and `blacklist`/`whitelist` (with or without context).

The following is how messages.html uses linkify to generate links.

```jinja2
<a href="{{ msgcontent | linkify }}">
```

The following is from how messages.html check if something is a field or component.

```jinja2
{% if msgcontent is component %}
```

The following example is from document.html and handles blacklisting/whitelisting with and without context.
```jinja2
{% if msgcontent is not blacklisted(message) %}
{% if message is not blacklisted %}

```

### document-settings.json

If you want to blacklist or whitelist things there are two ways to do it, in the following example the StandardTrailer will be considered blacklisted in the context of message ResendRequest (2)

Anything put in extra_data will be inserted into the document so the following example would let you use `{{ key }}` to access the list.

```json
{
"blacklist": ["0", "StandardHeader"],
"ctx_blacklist": { "2": ["StandardTrailer"] },
"extra_data": { "key": ["value1", "value2"] }
}
```  