from directory_client_core.base import BaseAPIClient


class PIRAPIClient(BaseAPIClient):

    def get_options(self):
        """
        Field options. Useful when building a form.

        Gives a list of options, display and and value
        for building out the market or countries list.

        Also called when validating create report
        """
        return self.request(
            url='/api/pir/',
            method="OPTIONS",
        ).json()['actions']['POST']

    def get_reports(self):
        """
        List of reports
        """
        return self.get('/api/pir/').json()

    def create_report(self, data):
        """
        Main API:

        Client accepts following parameters. Error will be raised
        if sent market and country.

        >>> client = PIRAPIClient()
        >>> client.create_report({
             'name': 'test',
             'sector': 'tech',
             'company': 'Rollo',
             'email': 'rollokb@gmail.com',
             'market': 'europe',
             # OR an iso code
             'country': 'SE',
             })

        Returns:

            {
                'id': 22,
                'country': None,
                'market': 'usa',
                'sector': 'tech',
                'name': 'test',
                'company': 'Rollo',
                'email': 'rollokb@gmail.com',
                'pdf': 'https://pir-invest.s3.amazonaws.com/media/
                usatechRollo2018-05-25.pdf',
                'date_created': '2018-05-25T11:23:45.406400Z'
            }

        """
        options = self.get_options()

        if 'market' in options:
            market_choices = [
                o['value'] for o in options['market']['choices']
            ]
        else:
            market_choices = []

        if 'country' in options:
            country_choices = [
                o['value'] for o in options['country']['choices']
            ]
        else:
            country_choices = []

        if 'sector' in options:
            sector_choices = [
                o['value'] for o in options['sector']['choices']
            ]
        else:
            sector_choices = []

        if 'market' in data and 'country' in data:
            raise ValueError('Cannot provide country and market')

        if 'country' in data and data['country'] not in country_choices:
            raise ValueError(
                'Country option must be in {}'.format(country_choices))

        if 'market' in data and data['market'] not in market_choices:
            raise ValueError(
                'Market option must be in {}'.format(market_choices))

        if 'sector' in data and data['sector'] not in sector_choices:
            raise ValueError(
                'Sector option must be in {}'.format(sector_choices))

        res = self.post('/api/pir/', data=data)
        res.raise_for_status()
        return res.json()
