import pytest
from src.aws.aws_lambda.router import Router


@pytest.fixture
def router():
    # Use the routes.yaml file from the tests/data/aws_lambda/ directory
    return Router(path_to_routes='../../data/aws_lambda/routes.yaml')


test_ids = [
    'authenticate POST: src.routes.authenticate.do_authenticate',
    'authenticate GET: src.routes.authenticate.get_authenticated_status',
    'users/profile GET: src.routes.users.get_profile',
    'users/settings PUT: src.routes.users.update_settings',
    'groups GET: src.routes.groups.get_all_groups',
    'groups POST: src.routes.groups.create_groups',
    'groups/{id=123} GET: src.routes.group.get_group',
    'group/{id=123} GET: src.routes.group.get_group',
    'group/{id=123} PUT: src.routes.groups.update_group',
    'group/{id=123} DELETE: src.routes.groups.delete_group',
    'groups/{id=123}/users GET: src.routes.groups.get_group_users',
    'groups/{id=123}/users POST: src.routes.groups.add_group_user',

]

test_data = [
    ({'path': 'authenticate', 'httpMethod': 'POST'}, 'src.routes.authenticate.do_authenticate', {}),
    ({'path': 'authenticate', 'httpMethod': 'GET'}, 'src.routes.authenticate.get_authenticated_status', {}),
    ({'path': 'users/profile', 'httpMethod': 'GET'}, 'src.routes.users.get_profile', {}),
    ({'path': 'users/settings', 'httpMethod': 'PUT'}, 'src.routes.users.update_settings', {}),
    ({'path': 'groups', 'httpMethod': 'GET'}, 'src.routes.groups.get_all_groups', {}),
    ({'path': 'groups', 'httpMethod': 'POST'}, 'src.routes.groups.create_groups', {}),
    ({'path': 'groups/123', 'httpMethod': 'GET'}, 'src.routes.group.get_group', {'id': '123'}),
    ({'path': 'group/123', 'httpMethod': 'GET'}, 'src.routes.group.get_group', {'id': '123'}),
    ({'path': 'group/123', 'httpMethod': 'PUT'}, 'src.routes.groups.update_group', {'id': '123'}),
    ({'path': 'group/123', 'httpMethod': 'DELETE'}, 'src.routes.groups.delete_group', {'id': '123'}),
    ({'path': 'groups/123/users', 'httpMethod': 'GET'}, 'src.routes.groups.get_group_users', {'id': '123'}),
    ({'path': 'groups/123/users', 'httpMethod': 'POST'}, 'src.routes.groups.add_group_user', {'id': '123'}),
    # Add more test cases as needed
]


def test_build_route_map(router):
    expected_route_map = {
        ('authenticate', 'POST'): {'function': 'src.routes.authenticate.do_authenticate'},
        ('authenticate', 'PUT'): {'function': 'src.routes.authenticate.do_authenticate'},
        ('authenticate', 'GET'): {'function': 'src.routes.authenticate.get_authenticated_status'},
        ('users/profile', 'GET'): {'function': 'src.routes.users.get_profile'},
        ('users/profile', 'PUT'): {'function': 'src.routes.users.update_profile'},
        ('users/settings', 'GET'): {'function': 'src.routes.users.get_settings'},
        ('users/settings', 'PUT'): {'function': 'src.routes.users.update_settings'},
        ('groups', 'GET'): {'function': 'src.routes.groups.get_all_groups'},
        ('groups', 'POST'): {'function': 'src.routes.groups.create_groups'},
        ('groups/{id}', 'GET'): {'function': 'src.routes.group.get_group'},
        ('group/{id}', 'GET'): {'function': 'src.routes.group.get_group'},
        ('group/{id}', 'PUT'): {'function': 'src.routes.groups.update_group'},
        ('group/{id}', 'DELETE'): {'function': 'src.routes.groups.delete_group'},
        ('groups/{id}/users', 'GET'): {'function': 'src.routes.groups.get_group_users'},
        ('groups/{id}/users', 'POST'): {'function': 'src.routes.groups.add_group_user'}
    }
    assert router.route_map == expected_route_map


@pytest.mark.parametrize('event, expected_function_path, expected_args', test_data, ids=test_ids)
def test_route(router, mocker, event, expected_function_path, expected_args):
    # Mock the import_module function
    mock_import_module = mocker.patch('importlib.import_module')

    # Create a mock module and a mock function
    mock_module = mocker.Mock()
    mock_function = mocker.Mock()

    # Set the return value of the mock import_module function
    mock_import_module.return_value = mock_module

    # Set the desired attribute on the mock module
    module_path, function_name = expected_function_path.rsplit('.', 1)
    setattr(mock_module, function_name, mock_function)

    # Call the route method
    timestamp = 'timestamp'
    router.route(event, timestamp)

    # Check if the correct functions were called with the correct arguments
    mock_import_module.assert_called_once_with(module_path)
    mock_function.assert_called_once_with(event, timestamp, **expected_args)
