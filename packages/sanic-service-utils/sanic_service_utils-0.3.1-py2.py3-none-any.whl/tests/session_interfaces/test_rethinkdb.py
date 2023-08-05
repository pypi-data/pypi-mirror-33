from unittest.mock import patch
import uuid
import time

from asynctest.mock import CoroutineMock, Mock

from sanic.response import text
import pytest
import ujson

from sanic_service_utils.session_interfaces.rethinkdb import RethinkDBSessionInterface, RethinkDBSession

SID = '5235262626'
COOKIE_NAME = 'cookie'
COOKIES = {COOKIE_NAME: SID}


@pytest.fixture
def mock_dict():
    class MockDict(dict):
        pass

    return MockDict


def mock_coroutine(return_value=None):
    async def mock_coro(*args, **kwargs):
        return return_value

    return Mock(return_value=return_value)


@pytest.mark.asyncio
async def test_redis_should_create_new_sid_if_no_cookie(mocker, mock_dict):
    request = mock_dict()
    request.cookies = {}

    mocker.spy(uuid, 'uuid4')
    session_interface = RethinkDBSessionInterface()
    await session_interface.open(request)

    assert uuid.uuid4.call_count == 1, 'should create a new SID with uuid'
    assert request['session'] == {}, 'should return an empty dict as session'


@pytest.mark.asyncio
async def test_should_return_data_from_redis(mocker, mock_dict):
    request = mock_dict()

    request.cookies = COOKIES

    mocker.spy(uuid, 'uuid4')
    data = {'foo': 'bar'}
    async_get_patch = mocker.patch(
        'sanic_service_utils.session_interfaces.rethinkdb.RethinkDBSession.async_get',
        return_value=RethinkDBSession(session_data=data),
        new_callable=CoroutineMock
    )

    session_interface = RethinkDBSessionInterface(cookie_name=COOKIE_NAME)
    session = await session_interface.open(request)

    assert uuid.uuid4.call_count == 0, 'should not create a new SID'
    assert async_get_patch.call_count == 1, 'should call on redis once'
    assert async_get_patch.call_args_list[0][0][0] == SID, 'should call only SID'
    assert session.get('foo') == 'bar', 'session data is pulled from redis'


@pytest.mark.asyncio
async def test_should_attach_session_to_request(mocker, mock_dict):
    request = mock_dict()
    request.cookies = COOKIES

    mocker.patch(
        'sanic_service_utils.session_interfaces.rethinkdb.RethinkDBSession.async_get',
        return_value=RethinkDBSession(session_data={}),
        new_callable=CoroutineMock
    )

    session_interface = RethinkDBSessionInterface(cookie_name=COOKIE_NAME)
    session = await session_interface.open(request)

    assert session == request['session']


@pytest.mark.asyncio
async def test_should_delete_session_from_redis(mocker, mock_dict):
    request = mock_dict()
    response = mock_dict()
    request.cookies = COOKIES
    response.cookies = {}

    get_mock = mocker.patch(
        'sanic_service_utils.session_interfaces.rethinkdb.RethinkDBSession.async_get',
        return_value=RethinkDBSession(session_data={}),
        new_callable=CoroutineMock
    )

    delete_mock = mocker.patch(
        'sanic_service_utils.session_interfaces.rethinkdb.RethinkDBSession.async_delete',
        return_value=None,
        new_callable=CoroutineMock
    )

    session_interface = RethinkDBSessionInterface(cookie_name=COOKIE_NAME)

    await session_interface.open(request)
    await session_interface.save(request, response)

    assert delete_mock.call_count == 1
    assert get_mock.call_args_list[0][0][0] == SID
    assert response.cookies == {}, 'should not change response cookies'


@pytest.mark.asyncio
async def test_should_expire_redis_cookies_if_modified(mocker, mock_dict):
    request = mock_dict()
    response = text('foo')
    request.cookies = COOKIES

    mocker.patch(
        'sanic_service_utils.session_interfaces.rethinkdb.RethinkDBSession.async_get',
        return_value=RethinkDBSession(session_data={}),
        new_callable=CoroutineMock
    )

    mocker.patch(
        'sanic_service_utils.session_interfaces.rethinkdb.RethinkDBSession.async_delete',
        return_value=None,
        new_callable=CoroutineMock
    )

    session_interface = RethinkDBSessionInterface(cookie_name=COOKIE_NAME)

    await session_interface.open(request)

    request['session'].clear()
    await session_interface.save(request, response)
    assert response.cookies[COOKIE_NAME]['max-age'] == 0
    assert response.cookies[COOKIE_NAME]['expires'] == 0


@pytest.mark.asyncio
async def test_should_save_in_redis_for_time_specified(mocker, mock_dict):
    request = mock_dict()
    request.cookies = COOKIES
    response = text('foo')

    mocker.patch(
        'sanic_service_utils.session_interfaces.rethinkdb.RethinkDBSession.async_get',
        return_value=RethinkDBSession(session_data={'foo': 'bar'}),
        new_callable=CoroutineMock
    )

    send_mock = mocker.patch(
        'sanic_service_utils.session_interfaces.rethinkdb.RethinkDBSession.async_send',
        return_value=None,
        new_callable=CoroutineMock
    )

    session_interface = RethinkDBSessionInterface(cookie_name=COOKIE_NAME)

    await session_interface.open(request)

    request['session']['foo'] = 'baz'
    await session_interface.save(request, response)

    assert send_mock.call_count == 1


@pytest.mark.asyncio
async def test_should_reset_cookie_expiry(mocker, mock_dict):
    request = mock_dict()
    request.cookies = COOKIES
    response = text('foo')
    mocker.patch("time.time")
    time.time.return_value = 1488576462.138493

    mocker.patch(
        'sanic_service_utils.session_interfaces.rethinkdb.RethinkDBSession.async_get',
        return_value=RethinkDBSession(session_data={'foo': 'bar'}),
        new_callable=CoroutineMock
    )

    mocker.patch(
        'sanic_service_utils.session_interfaces.rethinkdb.RethinkDBSession.async_send',
        return_value=None,
        new_callable=CoroutineMock
    )

    session_interface = RethinkDBSessionInterface(cookie_name=COOKIE_NAME)

    await session_interface.open(request)
    request['session']['foo'] = 'baz'
    await session_interface.save(request, response)

    assert response.cookies[COOKIE_NAME].value == SID
    assert response.cookies[COOKIE_NAME]['max-age'] == 2592000
    assert response.cookies[COOKIE_NAME]['expires'] == "Sun, 02-Apr-2017 21:27:42 GMT"


@pytest.mark.asyncio
@pytest.mark.skip  # Require sanic-session new release
async def test_sessioncookie_should_omit_request_headers(mocker, mock_dict):
    request = mock_dict()
    request.cookies = COOKIES
    response = text('foo')

    mocker.patch(
        'sanic_service_utils.session_interfaces.rethinkdb.RethinkDBSession.async_get',
        return_value=RethinkDBSession(session_data={'foo': 'bar'}),
        new_callable=CoroutineMock
    )

    mocker.patch(
        'sanic_service_utils.session_interfaces.rethinkdb.RethinkDBSession.async_send',
        return_value=None,
        new_callable=CoroutineMock
    )

    session_interface = RethinkDBSessionInterface(cookie_name=COOKIE_NAME, sessioncookie=True)

    await session_interface.open(request)
    await session_interface.save(request, response)

    assert response.cookies[COOKIE_NAME].value == SID
    assert 'max-age' not in response.cookies[COOKIE_NAME]
    assert 'expires' not in response.cookies[COOKIE_NAME]


@pytest.mark.asyncio
async def test_sessioncookie_delete_has_expiration_headers(mocker, mock_dict):
    request = mock_dict()
    request.cookies = COOKIES
    response = text('foo')

    mocker.patch(
        'sanic_service_utils.session_interfaces.rethinkdb.RethinkDBSession.async_get',
        return_value=RethinkDBSession(session_data={'foo': 'bar'}),
        new_callable=CoroutineMock
    )

    mocker.patch(
        'sanic_service_utils.session_interfaces.rethinkdb.RethinkDBSession.async_send',
        return_value=None,
        new_callable=CoroutineMock
    )

    mocker.patch(
        'sanic_service_utils.session_interfaces.rethinkdb.RethinkDBSession.async_delete',
        return_value=None,
        new_callable=CoroutineMock
    )

    session_interface = RethinkDBSessionInterface(
        cookie_name=COOKIE_NAME,
        sessioncookie=True
    )

    await session_interface.open(request)
    await session_interface.save(request, response)
    request['session'].clear()
    await session_interface.save(request, response)

    assert response.cookies[COOKIE_NAME]['max-age'] == 0
    assert response.cookies[COOKIE_NAME]['expires'] == 0
