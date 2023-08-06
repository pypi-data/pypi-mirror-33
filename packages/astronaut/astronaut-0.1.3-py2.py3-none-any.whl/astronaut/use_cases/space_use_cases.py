from astronaut.shared import use_case as uc
from astronaut.shared import response_object as res


class SpaceListUseCase(uc.UseCase):

    def __init__(self, repo):
        self.repo = repo

    def process_request(self, request_object):
        domain_space = self.repo.list(filters=request_object.filters)
        return res.ResponseSuccess(domain_space)
