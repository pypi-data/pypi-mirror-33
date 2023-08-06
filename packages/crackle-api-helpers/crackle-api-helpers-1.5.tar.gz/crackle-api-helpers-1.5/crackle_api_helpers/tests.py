""" Unit tests for crackle_api_helpers """
import unittest
from collections import namedtuple
from crackle_api_helpers.api_wrapper import (AuthHelpers, APIWrapper,
                                             APIWrapperAnimax)


class TestHelpers(unittest.TestCase):
    """ Test all helper methods """

    email_address, password, user_id = '', '', ''

    def setUp(self):
        """ Set up tasks for tests """
        apiconfig = namedtuple('apiconfig', 'host partner_id secret geo_code')
        self.config = apiconfig('http://ios-api-us.crackle.com', '22',
                                'KRYDXUKMPKTONARP', 'US')
        self.config_animax = apiconfig('http://web-api-animax.crackle.com',
                                       '22', 'KRYDXUKMPKTONARP', 'US')
        self.auth_helpers = AuthHelpers(self.config)
        self.api_wrapper = APIWrapper(self.config)
        self.api_wrapper_animax = APIWrapperAnimax(self.config)

    # Auth
    def test_register_config(self):
        """ Test register_config """
        print('testing register_config')
        self.assertIsNotNone(self.auth_helpers.register_config())

    def test_register_quick(self):
        """ Test register_quick """
        print('testing register_quick')
        message_code, self.email_address, self.password, self.user_id = \
            self.auth_helpers.register_quick()
        assert 'OK' in message_code
        assert self.email_address is not ''
        assert self.password is not ''
        assert self.user_id is not ''

    def test_login(self):
        """ Test login """
        print('testing login')
        self.test_register_quick()
        message_code, email_address, password, user_id = \
            self.auth_helpers.login(self.email_address, self.password)
        assert 'OK' in message_code
        assert email_address is not ''
        assert password is not ''
        assert user_id is not ''

    def test_logout(self):
        """ Test logout """
        print('testing logout')
        self.test_login()
        assert self.user_id is not ''
        print(self.auth_helpers.logout(self.user_id))
        self.assertTrue(self.auth_helpers.logout(self.user_id))

    # Video
    def test_find_media(self):
        """ Test find_media and get_media_id_metadata implicitly """
        print('testing find_media')
        self.assertIsNotNone(self.api_wrapper.find_media())

    def test_find_media_without_adverts(self):
        """ Test find_media_without_adverts """
        print('testing find_media_without_adverts')
        self.assertIsNotNone(self.api_wrapper.find_media_without_adverts())

    def test_find_media_with_preroll(self):
        """ Test find_media_with_preroll """
        print('testing find_media_with_preroll')
        self.assertIsNotNone(self.api_wrapper.find_media_with_preroll())

    def test_find_media_without_preroll(self):
        """ Test find_media_without_preroll """
        print('testing find_media_without_preroll')
        self.assertIsNotNone(self.api_wrapper.find_media_without_preroll())

    def test_find_media_with_two_midrolls(self):
        """ Test find_media_with_two_midrolls """
        print('testing find_media_with_two_midrolls')
        self.assertIsNotNone(self.api_wrapper.find_media_with_two_midrolls())

    def test_find_media_with_preroll_midroll(self):
        """ Test find_media_with_preroll_midroll """
        print('testing find_media_with_preroll_midroll')
        self.assertIsNotNone(
            self.api_wrapper.find_media_with_preroll_midroll())

    def test_find_media_with_rating_1(self):
        """ Test find_media_with_rating """
        print('testing find_media_with_rating')
        self.assertIsNotNone(
            self.api_wrapper.find_media_with_rating(rating='Not Rated'))

    def test_find_media_with_rating_2(self):
        """ Test find_media_with_rating """
        print('testing find_media_with_rating')
        self.assertIsNotNone(
            self.api_wrapper.find_media_with_rating(rating='PG'))

    def test_find_media_with_rating_3(self):
        """ Test find_media_with_rating """
        print('testing find_media_with_rating')
        self.assertIsNotNone(
            self.api_wrapper.find_media_with_rating(rating='PG-13'))

    def test_find_media_with_rating_4(self):
        """ Test find_media_with_rating """
        print('testing find_media_with_rating')
        self.assertIsNotNone(
            self.api_wrapper.find_media_with_rating(rating='TV-14'))

    def test_find_media_with_rating_5(self):
        """ Test find_media_with_rating """
        print('testing find_media_with_rating')
        self.assertIsNotNone(
            self.api_wrapper.find_media_with_rating(rating='R'))

    def test_find_media_with_min_duration(self):
        """ Test find_media_with_min_duration """
        print('testing find_media_with_min_duration')
        self.assertIsNotNone(
            self.api_wrapper.find_media_with_min_duration())

    def test_find_media_with_subtitles(self):
        """ Test find_media_with_subtitles """
        print('testing find_media_with_subtitles')
        self.assertIsNotNone(
            self.api_wrapper.find_media_with_subtitles())

    # Other
    def test_get_watchnow_tray_metadata(self):
        """ Test get_watchnow_tray_metadata """
        print('testing get_watchnow_tray_metadata')
        self.assertIsNotNone(
            self.api_wrapper.get_watchnow_tray_metadata(tray_position=0))

    def test_get_genre_carousel_metadata_1(self):
        """ Test get_genre_carousel_metadata TV """
        print('testing get_genre_carousel_metadata TV')
        self.assertIsNotNone(
            self.api_wrapper.get_genre_carousel_metadata(genre='TV'))

    def test_get_genre_carousel_metadata_2(self):
        """ Test get_genre_carousel_metadata MOVIES """
        print('testing get_genre_carousel_metadata Movies')
        self.assertIsNotNone(
            self.api_wrapper.get_genre_carousel_metadata(genre='Movies'))

    def test_get_genre_all_metadata_1(self):
        """ Test get_genre_all_metadata TV """
        print('testing get_genre_all_metadata TV')
        self.assertIsNotNone(
            self.api_wrapper.get_genre_all_metadata(genre='TV'))

    def test_get_genre_all_metadata_2(self):
        """ Test get_genre_all_metadata MOVIES """
        print('testing get_genre_all_metadata MOVIES')
        self.assertIsNotNone(
            self.api_wrapper.get_genre_all_metadata(genre='Movies'))

    def test_get_series_with_min_episodes(self):
        """ Test get_series_with_min_episodes """
        print('testing get_series_with_min_episodes')
        self.assertIsNotNone(
            self.api_wrapper.get_series_with_min_episodes(min_episodes=1))

    # Animax API helper method tests
    def test_get_homepage_slideshow_metadata(self):
        """ Test get_homepage_slideshow_metadata """
        print('testing get_homepage_slideshow_metadata')
        self.assertIsNotNone(
            self.api_wrapper_animax.get_homepage_slideshow_metadata())

    def test_get_show_genres(self):
        """ Test get_show_genres """
        print('testing get_show_genres')
        self.assertIsNotNone(
            self.api_wrapper_animax.get_show_genres())

    def test_get_shows_metadata(self):
        """ Test get_shows_metadata """
        print('testing get_shows_metadata')
        self.assertIsNotNone(
            self.api_wrapper_animax.get_shows_metadata())


if __name__ == '__main__':
    unittest.main()
