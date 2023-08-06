from faker import Faker
fake = Faker('en_GB')


def example():
    return {
        'addressLines': '%s, %s' % (fake.street_address(), fake.city()),
        'postcode': fake.postcode(),
        'country': 'UK'
    }
