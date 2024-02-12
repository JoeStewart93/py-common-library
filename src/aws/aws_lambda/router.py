import importlib
import yaml
from src.core.logging.logger import logr


class Router:
    def __init__(self, path_to_routes):
        self.processed_files = set()
        self.route_map = self._build_route_map(path_to_routes)

    def _get_methods(self, prop) -> list:
        methods = []
        if 'function' in prop:
            methods = prop['method']
            if isinstance(methods, str):
                methods = [methods]

        return methods



    def _process_properties(self, route, path, parent_path='', route_map=None):

        if 'properties' in route:
            for prop in route['properties']:

                methods = self._get_methods(prop)

                for method in methods:
                    route_map[(path, method)] = {'function': prop['function']}

                if 'routes' in prop:
                    for nested_route in prop['routes']:
                        nested_route_map, path = self._process_route(nested_route, path)
                        route_map.update(nested_route_map)
        return route_map, path



    def _process_route(self, route, parent_path=''):
        route_map = {}
        path = parent_path
        if 'path' in route:
            if isinstance(route['path'], dict):
                path += '/' + str(route['path']).replace(": None", "").replace("'", "") if parent_path else str(
                    route['path']).replace(": None", "").replace("'", "")
            else:
                path += '/' + str(route['path']) if parent_path else str(route['path'])

        route_map, path = self._process_properties(route, path, parent_path, route_map)

        # if 'properties' in route:
        #     for prop in route['properties']:
        #         if 'function' in prop:
        #             methods = prop['method']
        #             if isinstance(methods, str):
        #                 methods = [methods]
        #             for method in methods:
        #                 route_map[(path, method)] = {'function': prop['function']}
        #         if 'routes' in prop:
        #             for nested_route in prop['routes']:
        #                 nested_route_map, path = self._process_route(nested_route, path)
        #                 route_map.update(nested_route_map)
        return route_map, path

    def _build_route_map(self, path_to_routes, parent_path=''):
        if path_to_routes in self.processed_files:
            return {}
        self.processed_files.add(path_to_routes)
        route_map = {}
        with open(path_to_routes) as f:
            routes = yaml.load(f, Loader=yaml.FullLoader)['routes']
            for route in routes:
                route_map_update, path = self._process_route(route, parent_path)
                route_map.update(route_map_update)
                if 'ref' in route:
                    route_map.update(self._build_route_map(route['ref'], path))
        return route_map

    def route(self, event, timestamp):
        path = event['path']
        if path.startswith('/'):
            path = path.lstrip('/')
        method = event['httpMethod']
        path_components = path.split('/')
        for route, route_info in self.route_map.items():
            route_path, route_method = route
            if route_method != method:
                continue
            route_components = route_path.split('/')
            if len(path_components) != len(route_components):
                continue
            kwargs = {}
            for path_component, route_component in zip(path_components, route_components):
                if route_component.startswith('{') and route_component.endswith('}'):
                    kwargs[route_component[1:-1]] = path_component
                elif path_component != route_component:
                    break
            else:
                function_path = route_info['function']
                module_path, function_name = function_path.rsplit('.', 1)
                module = importlib.import_module(module_path)
                function = getattr(module, function_name)
                kwargs.update({k: v for k, v in event.items() if k not in ['path', 'httpMethod']})
                logr.info(f'\nRouting {path} to {function_path} with data:{kwargs}')
                function(event, timestamp, **kwargs)
                break
        else:
            logr.info(f"No route found for path {path} with method {method}.")