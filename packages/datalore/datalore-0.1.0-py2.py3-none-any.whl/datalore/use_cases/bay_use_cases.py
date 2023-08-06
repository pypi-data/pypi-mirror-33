from datalore.shared import use_case as uc
from datalore.shared import response_object as res


class BayListUseCase(uc.UseCase):

    def __init__(self, repo):
        self.repo = repo

    def process_request(self, request_object):
        domain_bay = self.repo.list(filters=request_object.filters)
        return res.ResponseSuccess(domain_bay)
