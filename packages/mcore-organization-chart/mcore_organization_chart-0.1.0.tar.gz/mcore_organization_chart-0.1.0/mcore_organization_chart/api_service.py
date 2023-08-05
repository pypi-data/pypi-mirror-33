import requests


class MigacoreApiService:
    BASE_URL = 'http://migacore-coding-orgchart.herokuapp.com'

    @staticmethod
    def reports_to(subordinate: str, supervisor: str) -> bool:
        endpoint = '/reports_to'
        params = {
            'subordinate': subordinate,
            'supervisor': supervisor
        }

        response = requests.get(url='{}{}'.format(MigacoreApiService.BASE_URL, endpoint), params=params)
        assert response.status_code == 200
        return response.json()
