import addict
import json
import requests


class Query(object):
    """
    Construct a GraphQL query
    """
    def __init__(self, name='query', client=None, parent=None):
        self._name = name
        self._nodes = []
        self._call_args = None
        self._values_to_show = []
        self._client = client
        self._parent = parent

    def __getattr__(self, key):
        q = Query(name=key, parent=self)
        self._nodes.append(q)
        return q

    def __call__(self, *args, **kwargs):
        self._call_args = kwargs
        return self

    def values(self, *args):
        self._values_to_show.extend(args)
        return self

    def get_graphql(self, tab=2, indentation=2):
        def serialize_arg(arg):
            if isinstance(arg, int):
                return str(arg)
            else:
                return '"{0}"'.format(arg)

        if self._call_args:
            args = ', '.join([
                '{0}: {1}'.format(k, serialize_arg(v))
                for k, v in self._call_args.items()
            ])
            name = '{0}({1})'.format(self._name, args)
        else:
            name = self._name

        nodes = [v for v in self._values_to_show]
        nodes.extend([
            node.get_graphql(tab=tab + indentation, indentation=indentation)
            for node in self._nodes
        ])

        nodes_str = ('\n' + ' '*tab).join([v for v in nodes])

        return '{name} {{\n{opening_tab}{nodes}\n{closing_tab}}}'.format(
            name=name,
            opening_tab=' '*tab,
            closing_tab=' '*(tab - indentation),
            nodes=nodes_str,
        )

    def _get_root(self):
        if self._parent:
            return self._parent._get_root()
        else:
            return self

    def fetch(self):
        root = self._get_root()
        client = root._client
        graphql = root.get_graphql()
        body = {
            'query': graphql
        }
        r = requests.post(client.url, json.dumps(body), headers=client.headers)
        if r.status_code != 200:
            raise Exception(r.content)
        return addict.Dict(json.loads(r.content)['data'])


class Client(object):
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def query(self):
        return Query(client=self)
