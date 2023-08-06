from faker import Faker
fake = Faker('en_GB')


def example(survey_ids, country=None, surveyType=None):
    return {
        'name': fake.sentence(nb_words=3, variable_nb_words=True)[:-1],
        'year': fake.year(),
        'country': fake.country() if country is None else country,
        'surveyType': surveyType if surveyType is not None else fake.words(nb=1, ext_word_list=["domestic", "non-domestic", "transient"])[0],
        'surveys': survey_ids,
    }
