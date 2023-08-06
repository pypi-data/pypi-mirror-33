from __future__ import print_function

import collections
import importlib
import json
import pkgutil
from functools import wraps

import plotly
import dash_renderer
import six

from django.http import HttpResponse, JsonResponse as BaseJsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .dependencies import Event, Input, Output, State
from .resources import Scripts, Css
from .development.base_component import Component
from . import exceptions
from ._utils import AttributeDict as _AttributeDict


__all__ = (
    'JsonResponse',
    'MetaDashView',
    'Dash',
    'BaseDashView'
)


class JsonResponse(BaseJsonResponse):
    def __init__(self, data, encoder=plotly.utils.PlotlyJSONEncoder, safe=False,
                 json_dumps_params=None, **kwargs):
        super(JsonResponse, self).__init__(data, encoder=encoder, safe=safe,
                                           json_dumps_params=json_dumps_params, **kwargs)


class MetaDashView(type):
    def __new__(cls, name, bases, attrs):
        new_cls = super(MetaDashView, cls).__new__(cls, name, bases, attrs)

        if new_cls.__dict__.get('dash_name', ''):
            new_cls._dashes[new_cls.__dict__['dash_name']] = new_cls   # pylint: disable=protected-access
            dash_prefix = getattr(new_cls, 'dash_prefix', '').strip()
            if dash_prefix:
                # pylint: disable=protected-access
                new_cls._dashes[dash_prefix + new_cls.__dict__['dash_name']] = new_cls

        return new_cls


class Dash(object):  # pylint: disable=too-many-instance-attributes
    template = '''<!DOCTYPE html>
    <html>
        <head>
            <meta charset="UTF-8">
            <title>{}</title>
            {}
        </head>
        <body>
            <div id="react-entry-point">
                <div class="_dash-loading">
                    Loading...
                </div>
            </div>
            <footer>
                {}
                {}
            </footer>
        </body>
    </html>'''

    def __init__(self, url_base_pathname='/', **kwargs):
        super(Dash, self).__init__(**kwargs)

        self.url_base_pathname = url_base_pathname
        self.config = _AttributeDict({
            'suppress_callback_exceptions': False,
            'routes_pathname_prefix': url_base_pathname,
            'requests_pathname_prefix': url_base_pathname
        })

        # list of dependencies
        self.callback_map = {}

        # static files from the packages
        self.css = Css()
        self.scripts = Scripts()
        self.registered_paths = {}

        self._layout = None
        self._cached_layout = None
        self.routes = []

    @property
    def layout(self):
        return self._layout

    def _layout_value(self):
        if isinstance(self._layout, collections.Callable):
            self._cached_layout = self._layout()
        else:
            self._cached_layout = self._layout
        return self._cached_layout

    @layout.setter
    def layout(self, value):
        if (not isinstance(value, Component) and
                not isinstance(value, collections.Callable)):
            raise Exception(
                ''
                'Layout must be a dash component '
                'or a function that returns '
                'a dash component.')

        self._layout = value

        layout_value = self._layout_value()
        # pylint: disable=protected-access
        self.css._update_layout(layout_value)
        self.scripts._update_layout(layout_value)
        self._collect_and_register_resources(
            self.scripts.get_all_scripts()
        )
        self._collect_and_register_resources(
            self.css.get_all_css()
        )

    def _config(self):
        return {
            'url_base_pathname': self.url_base_pathname,
            'requests_pathname_prefix': self.config.requests_pathname_prefix
        }

    def _collect_and_register_resources(self, resources):
        # template in the necessary component suite JS bundles
        # add the version number of the package as a query parameter
        # for cache busting
        def _relative_url_path(relative_package_path='', namespace=''):

            # track the registered packages
            if namespace in self.registered_paths:
                self.registered_paths[namespace].append(relative_package_path)
            else:
                self.registered_paths[namespace] = [relative_package_path]

            return '{}_dash-component-suites/{}/{}?v={}'.format(
                self.config['routes_pathname_prefix'],
                namespace,
                relative_package_path,
                importlib.import_module(namespace).__version__
            )

        srcs = []
        for resource in resources:
            if 'relative_package_path' in resource:
                if isinstance(resource['relative_package_path'], str):
                    srcs.append(_relative_url_path(**resource))
                else:
                    for rel_path in resource['relative_package_path']:
                        srcs.append(_relative_url_path(
                            relative_package_path=rel_path,
                            namespace=resource['namespace']
                        ))
            elif 'external_url' in resource:
                if isinstance(resource['external_url'], str):
                    srcs.append(resource['external_url'])
                else:
                    for url in resource['external_url']:
                        srcs.append(url)
            elif 'absolute_path' in resource:
                raise Exception(
                    'Serving files form absolute_path isn\'t supported yet'
                )
        return srcs

    def _generate_css_dist_html(self):
        links = self._collect_and_register_resources(
            self.css.get_all_css()
        )
        return '\n'.join([
            '<link rel="stylesheet" href="{}">'.format(link)
            for link in links
        ])

    def _generate_scripts_html(self):
        # Dash renderer has dependencies like React which need to be rendered
        # before every other script. However, the dash renderer bundle
        # itself needs to be rendered after all of the component's
        # scripts have rendered.
        # The rest of the scripts can just be loaded after React but before
        # dash renderer.
        # pylint: disable=protected-access
        srcs = self._collect_and_register_resources(
            self.scripts._resources._filter_resources(
                dash_renderer._js_dist_dependencies
            ) +
            self.scripts.get_all_scripts() +
            self.scripts._resources._filter_resources(
                dash_renderer._js_dist
            )
        )

        return '\n'.join([
            '<script src="{}"></script>'.format(src)
            for src in srcs
        ])

    def _generate_config_html(self, **kwargs):
        config = self._config()
        config.update(kwargs)
        return (
            '<script id="_dash-config" type="application/json">'
            '{}'
            '</script>'
        ).format(json.dumps(config, cls=plotly.utils.PlotlyJSONEncoder))

    def index(self, *args, **kwargs):  # pylint: disable=unused-argument
        scripts = self._generate_scripts_html()
        css = self._generate_css_dist_html()
        config = self._generate_config_html()
        title = getattr(self, 'title', 'Dash')

        return self.template.format(title, css, config, scripts)

    def dependencies(self, *args, **kwargs):  # pylint: disable=unused-argument
        return [
            {
                'output': {
                    'id': k.split('.')[0],
                    'property': k.split('.')[1]
                },
                'inputs': v['inputs'],
                'state': v['state'],
                'events': v['events']
            } for k, v in list(self.callback_map.items())
        ]

    # pylint: disable=unused-argument, no-self-use
    def react(self, *args, **kwargs):
        raise exceptions.DashException(
            'Yo! `react` is no longer used. \n'
            'Use `callback` instead. `callback` has a new syntax too, '
            'so make sure to call `help(app.callback)` to learn more.')

    # pylint: disable=unused-argument
    def serve_component_suites(self, package_name, path_in_package_dist, *args, **kwargs):
        """ Serve the JS bundles for each package
        """
        if package_name not in self.registered_paths:
            raise Exception(
                'Error loading dependency.\n'
                '"{}" is not a registered library.\n'
                'Registered libraries are: {}'
                .format(package_name, list(self.registered_paths.keys())))

        elif path_in_package_dist not in self.registered_paths[package_name]:
            print(self.registered_paths[package_name])
            raise Exception(
                '"{}" is registered but the path requested is not valid.\n'
                'The path requested: "{}"\n'
                'List of registered paths: {}'
                .format(
                    package_name,
                    path_in_package_dist,
                    self.registered_paths
                )
            )

        return pkgutil.get_data(package_name, path_in_package_dist)

    def serve_routes(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.routes

    def _validate_callback(self, output, inputs, state, events):
        # pylint: disable=too-many-branches
        layout = self._cached_layout or self._layout_value()

        if (layout is None and
                not self.config.first('suppress_callback_exceptions',
                                      'supress_callback_exceptions')):
            # Without a layout, we can't do validation on the IDs and
            # properties of the elements in the callback.
            raise exceptions.LayoutIsNotDefined('''
                Attempting to assign a callback to the application but
                the `layout` property has not been assigned.
                Assign the `layout` property before assigning callbacks.
                Alternatively, suppress this warning by setting
                `app.config['suppress_callback_exceptions']=True`
            '''.replace('    ', ''))

        for args, obj, name in [([output], Output, 'Output'),
                                (inputs, Input, 'Input'),
                                (state, State, 'State'),
                                (events, Event, 'Event')]:

            if not isinstance(args, list):
                raise exceptions.IncorrectTypeException(
                    'The {} argument `{}` is '
                    'not a list of `dash.dependencies.{}`s.'.format(
                        name.lower(), str(args), name
                    ))

            for arg in args:
                if not isinstance(arg, obj):
                    raise exceptions.IncorrectTypeException(
                        'The {} argument `{}` is '
                        'not of type `dash.{}`.'.format(
                            name.lower(), str(arg), name
                        ))

                if (not self.config.first('suppress_callback_exceptions',
                                          'supress_callback_exceptions') and
                        arg.component_id not in layout and
                        arg.component_id != getattr(layout, 'id', None)):
                    raise exceptions.NonExistantIdException('''
                        Attempting to assign a callback to the
                        component with the id "{}" but no
                        components with id "{}" exist in the
                        app\'s layout.\n\n
                        Here is a list of IDs in layout:\n{}\n\n
                        If you are assigning callbacks to components
                        that are generated by other callbacks
                        (and therefore not in the initial layout), then
                        you can suppress this exception by setting
                        `app.config['suppress_callback_exceptions']=True`.
                    '''.format(
                        arg.component_id,
                        arg.component_id,
                        list(layout.keys()) + (
                            [] if not hasattr(layout, 'id') else
                            [layout.id]
                        )
                    ).replace('    ', ''))

                if not self.config.first('suppress_callback_exceptions',
                                         'supress_callback_exceptions'):

                    if getattr(layout, 'id', None) == arg.component_id:
                        component = layout
                    else:
                        component = layout[arg.component_id]

                    if (hasattr(arg, 'component_property') and
                            arg.component_property not in
                            component.available_properties and not
                            any(arg.component_property.startswith(w) for w in
                                component.available_wildcard_properties)):
                        raise exceptions.NonExistantPropException('''
                            Attempting to assign a callback with
                            the property "{}" but the component
                            "{}" doesn't have "{}" as a property.\n
                            Here is a list of the available properties in "{}":
                            {}
                        '''.format(
                            arg.component_property,
                            arg.component_id,
                            arg.component_property,
                            arg.component_id,
                            component.available_properties).replace(
                                '    ', ''))

                    if (hasattr(arg, 'component_event') and
                            arg.component_event not in
                            component.available_events):
                        raise exceptions.NonExistantEventException('''
                            Attempting to assign a callback with
                            the event "{}" but the component
                            "{}" doesn't have "{}" as an event.\n
                            Here is a list of the available events in "{}":
                            {}
                        '''.format(
                            arg.component_event,
                            arg.component_id,
                            arg.component_event,
                            arg.component_id,
                            component.available_events).replace('    ', ''))

        if state and not events and not inputs:
            raise exceptions.MissingEventsException('''
                This callback has {} `State` {}
                but no `Input` elements or `Event` elements.\n
                Without `Input` or `Event` elements, this callback
                will never get called.\n
                (Subscribing to input components will cause the
                callback to be called whenver their values
                change and subscribing to an event will cause the
                callback to be called whenever the event is fired.)
            '''.format(
                len(state),
                'elements' if len(state) > 1 else 'element'
            ).replace('    ', ''))

        if '.' in output.component_id:
            raise exceptions.IDsCantContainPeriods('''The Output element
            `{}` contains a period in its ID.
            Periods are not allowed in IDs right now.'''.format(
                output.component_id
            ))

        callback_id = '{}.{}'.format(
            output.component_id, output.component_property)
        if callback_id in self.callback_map:
            raise exceptions.CantHaveMultipleOutputs('''
                You have already assigned a callback to the output
                with ID "{}" and property "{}". An output can only have
                a single callback function. Try combining your inputs and
                callback functions together into one function.
            '''.format(
                output.component_id,
                output.component_property).replace('    ', ''))

    # TODO - Update nomenclature.
    # "Parents" and "Children" should refer to the DOM tree
    # and not the dependency tree.
    # The dependency tree should use the nomenclature
    # "observer" and "controller".
    # "observers" listen for changes from their "controllers". For example,
    # if a graph depends on a dropdown, the graph is the "observer" and the
    # dropdown is a "controller". In this case the graph's "dependency" is
    # the dropdown.
    # TODO - Check this map for recursive or other ill-defined non-tree
    # relationships
    # pylint: disable=dangerous-default-value
    def callback(self, output, inputs=[], state=[], events=[]):
        self._validate_callback(output, inputs, state, events)

        callback_id = '{}.{}'.format(
            output.component_id, output.component_property
        )
        self.callback_map[callback_id] = {
            'inputs': [
                {'id': c.component_id, 'property': c.component_property}
                for c in inputs
            ],
            'state': [
                {'id': c.component_id, 'property': c.component_property}
                for c in state
            ],
            'events': [
                {'id': c.component_id, 'event': c.component_event}
                for c in events
            ]
        }

        def wrap_func(func):
            @wraps(func)
            def add_context(*args, **kwargs):
                output_value = func(*args, **kwargs)
                response = {
                    'response': {
                        'props': {
                            output.component_property: output_value
                        }
                    }
                }

                return JsonResponse(response)

            self.callback_map[callback_id]['callback'] = add_context

            return add_context

        return wrap_func

    def update_component(self, output, inputs, state, **kwargs):
        target_id = '{}.{}'.format(output['id'], output['property'])
        args = []
        for component_registration in self.callback_map[target_id]['inputs']:
            args.append([
                c.get('value', None) for c in inputs if
                c['property'] == component_registration['property'] and
                c['id'] == component_registration['id']
            ][0])

        for component_registration in self.callback_map[target_id]['state']:
            args.append([
                c.get('value', None) for c in state if
                c['property'] == component_registration['property'] and
                c['id'] == component_registration['id']
            ][0])

        return self.callback_map[target_id]['callback'](*args, **kwargs)


class BaseDashView(six.with_metaclass(MetaDashView, View)):
    dash_template = Dash.template
    dash_base_url = '/'
    dash_name = None
    dash_prefix = ''  # For additional special urls
    _dashes = {}

    def __init__(self, **kwargs):
        dash_base_url = kwargs.pop('dash_base_url', self.dash_base_url)

        super(BaseDashView, self).__init__(**kwargs)

        dash = getattr(self, 'dash', None)
        if isinstance(dash, Dash):
            self.dash.url_base_pathname = dash_base_url  # pylint: disable=access-member-before-definition
            self.dash.config.requests_pathname_prefix = dash_base_url  # pylint: disable=access-member-before-definition
        else:
            self.dash = Dash(url_base_pathname=dash_base_url)
            self.dash.template = self.dash_template

    @staticmethod
    def _dash_base_url(path, part):
        return path[:path.find(part) + 1]

    def _dash_index(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        return HttpResponse(self.dash.index())

    def _dash_dependencies(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        return JsonResponse(self.dash.dependencies())

    def _dash_layout(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        # TODO - Set browser cache limit - pass hash into frontend
        return JsonResponse(self.dash._layout_value())  # pylint: disable=protected-access

    def _dash_upd_component(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        body = json.loads(request.body)

        output = body['output']
        inputs = body.get('inputs', [])
        state = body.get('state', [])

        return self.dash.update_component(output, inputs, state)

    def _dash_component_suites(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        ext = kwargs.get('path_in_package_dist', '').split('.')[-1]
        mimetype = {
            'js': 'application/JavaScript',
            'css': 'text/css'
        }[ext]

        return HttpResponse(self.dash.serve_component_suites(*args, **kwargs), content_type=mimetype)

    def _dash_routes(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        return JsonResponse(self.dash.serve_routes(*args, **kwargs))

    @classmethod
    def serve_dash_index(cls, request, dash_name, *args, **kwargs):
        view = cls._dashes[dash_name](dash_base_url=request.path)
        return view._dash_index(request, *args, **kwargs)   # pylint: disable=protected-access

    @classmethod
    def serve_dash_dependencies(cls, request, dash_name, *args, **kwargs):
        view = cls._dashes[dash_name](dash_base_url=cls._dash_base_url(request.path, '/_dash-dependencies'))
        return view._dash_dependencies(request, *args, **kwargs)   # pylint: disable=protected-access

    @classmethod
    def serve_dash_layout(cls, request, dash_name, *args, **kwargs):
        view = cls._dashes[dash_name](dash_base_url=cls._dash_base_url(request.path, '/_dash-layout'))
        return view._dash_layout(request, *args, **kwargs)   # pylint: disable=protected-access

    @classmethod
    @csrf_exempt
    def serve_dash_upd_component(cls, request, dash_name, *args, **kwargs):
        view = cls._dashes[dash_name](dash_base_url=cls._dash_base_url(request.path, '/_dash-update-component'))
        return view._dash_upd_component(request, *args, **kwargs)   # pylint: disable=protected-access

    @classmethod
    def serve_dash_component_suites(cls, request, dash_name, *args, **kwargs):
        view = cls._dashes[dash_name](dash_base_url=cls._dash_base_url(request.path, '/_dash-component-suites'))
        return view._dash_component_suites(request, *args, **kwargs)   # pylint: disable=protected-access

    @classmethod
    def serve_dash_routes(cls, request, dash_name, *args, **kwargs):
        view = cls._dashes[dash_name](dash_base_url=cls._dash_base_url(request.path, '/_dash-routes'))
        return view._dash_component_suites(request, *args, **kwargs)   # pylint: disable=protected-access
