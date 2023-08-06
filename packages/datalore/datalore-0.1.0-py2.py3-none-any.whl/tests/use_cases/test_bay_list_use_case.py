import pytest
from unittest import mock

from datalore.domain.bay import Bay
from datalore.shared import response_object as res
from datalore.use_cases import request_objects as req
from datalore.use_cases import bay_use_cases as uc


@pytest.fixture
def domain_bays():
    bay_1 = Bay(
        code='f853578c-fc0f-4e65-81b8-566c5dffa35a',
        size=215,
        price=39,
        longitude='-0.09998975',
        latitude='51.75436293',
    )

    bay_2 = Bay(
        code='fe2c3195-aeff-487a-a08f-e0bdc0ec6e9a',
        size=405,
        price=66,
        longitude='0.18228006',
        latitude='51.74640997',
    )

    bay_3 = Bay(
        code='913694c6-435a-4366-ba0d-da5334a611b2',
        size=56,
        price=60,
        longitude='0.27891577',
        latitude='51.45994069',
    )

    bay_4 = Bay(
        code='eed76e77-55c1-41ce-985d-ca49bf6c0585',
        size=93,
        price=48,
        longitude='0.33894476',
        latitude='51.39916678',
    )

    return [bay_1, bay_2, bay_3, bay_4]


def test_bay_list_without_parameters(domain_bays):
    repo = mock.Mock()
    repo.list.return_value = domain_bays

    bay_list_use_case = uc.BayListUseCase(repo)
    request_object = req.BayListRequestObject.from_dict({})

    response_object = bay_list_use_case.execute(request_object)

    assert bool(response_object) is True
    repo.list.assert_called_with(filters=None)

    assert response_object.value == domain_bays


def test_bay_list_with_parameters(domain_bays):
    repo = mock.Mock()
    repo.list.return_value = domain_bays

    bay_list_use_case = uc.BayListUseCase(repo)
    qry_filters = {'a': 5}
    request_object = \
        req.BayListRequestObject.from_dict({'filters': qry_filters})

    response_object = bay_list_use_case.execute(request_object)

    assert bool(response_object) is True
    repo.list.assert_called_with(filters=qry_filters)

    assert response_object.value == domain_bays


def test_bay_list_handles_generic_error():
    repo = mock.Mock()
    repo.list.side_effect = Exception('Just an error message')

    bay_list_use_case = uc.BayListUseCase(repo)
    request_object = req.BayListRequestObject.from_dict({})

    response_object = bay_list_use_case.execute(request_object)

    assert bool(response_object) is False
    assert response_object.value == {
        'type': res.ResponseFailure.SYSTEM_ERROR,
        'message': "Exception: Just an error message"
    }


def test_bay_list_handles_bad_request():
    repo = mock.Mock()

    bay_list_use_case = uc.BayListUseCase(repo)
    request_object = req.BayListRequestObject.from_dict({'filters': 5})

    response_object = bay_list_use_case.execute(request_object)

    assert bool(response_object) is False
    assert response_object.value == {
        'type': res.ResponseFailure.PARAMETERS_ERROR,
        'message': "filters: Is not iterable"
    }
