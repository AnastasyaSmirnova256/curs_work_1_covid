from peewee import *
from datetime import date

sqlite_db = SqliteDatabase('db/my_app.db')


class DataDbModel(Model):
    iso_code = TextField()
    continent = TextField()
    location = TextField()
    date = DateField()
    total_cases = FloatField()
    new_cases = FloatField()
    new_cases_smoothed = FloatField()
    total_deaths = FloatField()
    new_deaths = FloatField()
    new_deaths_smoothed = FloatField()
    total_cases_per_million = FloatField()
    new_cases_per_million = FloatField()
    new_cases_smoothed_per_million = FloatField()
    total_deaths_per_million = FloatField()
    new_deaths_per_million = FloatField()
    new_deaths_smoothed_per_million = FloatField()
    reproduction_rate = FloatField()
    icu_patients = FloatField()
    icu_patients_per_million = FloatField()
    hosp_patients = FloatField()
    hosp_patients_per_million = FloatField()
    weekly_icu_admissions = FloatField()
    weekly_icu_admissions_per_million = FloatField()
    weekly_hosp_admissions = FloatField()
    weekly_hosp_admissions_per_million = FloatField()
    new_tests = FloatField()
    total_tests = FloatField()
    total_tests_per_thousand = FloatField()
    new_tests_per_thousand = FloatField()
    new_tests_smoothed = FloatField()
    new_tests_smoothed_per_thousand = FloatField()
    positive_rate = FloatField()
    tests_per_case = FloatField()
    tests_units = str
    total_vaccinations = FloatField()
    people_vaccinated = FloatField()
    people_fully_vaccinated = FloatField()
    total_boosters = FloatField()
    new_vaccinations = FloatField()
    new_vaccinations_smoothed = FloatField()
    total_vaccinations_per_hundred = FloatField()
    people_vaccinated_per_hundred = FloatField()
    people_fully_vaccinated_per_hundred = FloatField()
    total_boosters_per_hundred = FloatField()
    new_vaccinations_smoothed_per_million = FloatField()
    new_people_vaccinated_smoothed = FloatField()
    new_people_vaccinated_smoothed_per_hundred = FloatField()
    stringency_index = FloatField()
    population = FloatField()
    population_density = FloatField()
    median_age = FloatField()
    aged_65_older = FloatField()
    aged_70_older = FloatField()
    gdp_per_capita = FloatField()
    extreme_poverty = FloatField()
    cardiovasc_death_rate = FloatField()
    diabetes_prevalence = FloatField()
    female_smokers = FloatField()
    male_smokers = FloatField()
    handwashing_facilities = FloatField()
    hospital_beds_per_thousand = FloatField()
    life_expectancy = FloatField()
    human_development_index = FloatField()
    excess_mortality_cumulative_absolute = FloatField()
    excess_mortality_cumulative = FloatField()
    excess_mortality = FloatField()
    excess_mortality_cumulative_per_million = FloatField()

    class Meta:
        database = sqlite_db


if __name__ == '__main__':
    sqlite_db.create_tables([DataDbModel])
