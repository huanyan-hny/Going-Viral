from django.conf.urls import include, url
import views

urlpatterns = [
    # Data import
    url(r'^add_airline$', views.add_airline),
    url(r'^add_airport$', views.add_airport),
    url(r'^add_country$', views.add_country),
    url(r'^add_location_to_country$', views.add_location_to_country),
    url(r'^update_airport_location', views.update_airport_location),

    # Data export
    url(r'^export_countries', views.export_all_countries),
    url(r'^export_airlines', views.export_all_airlines),
    url(r'^save_airlines', views.save_airlines),
    url(r'^save_all_airlines', views.save_all_airlines),
    url(r'^export_stats', views.export_stats),

    # Background management
    url(r'^start_listener', views.start_kafka_consumer),

    # Connect with front
    url(r'^init_map', views.init_country),
    url(r'^submit_plague$', views.submit_job),
    url(r'^init_airports', views.init_airports),
    url(r'get_airlines', views.get_airlines),
    url(r'^get_status', views.retrieve_status),

    # Get status and stats
    url(r'^current_status', views.dummy_current_status),
    url(r'^current_stats', views.dummy_current_stats),

    # Background stat
    url(r'^airport_stats', views.calculate_airport_airline_count),
    url(r'^airport_importance', views.calculate_airport_importance),
    url(r'^airline_importance', views.calculate_airline_importance),

    url(r'^export_kiev', views.export_kiev),
    url(r'^update_kiev', views.update_kiev),

    # Test
    url(r'^get_session', views.get_session),
    url(r'^dummy', views.fuck_you),

    # Work
    url(r'^atlas', views.atlas),
]
