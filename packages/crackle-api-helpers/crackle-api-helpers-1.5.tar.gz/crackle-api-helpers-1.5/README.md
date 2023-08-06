## README

1. `python`
2. `from crackle_api_helpers.api_wrapper import APIWrapper`
3. `wrapper = APIWrapper()`

## Example usage

 
if using a framework: 
`config = host_api_ps4()`  

or if using shell:  
`from collections import namedtuple ` 
`apiconfig = namedtuple('apiconfig','host partner_id secret geo_code')  `
`config = apiconfig('http://ios-api-us.crackle.com', '<PARTNER_ID>', '<SECRET>', 'US')`

 then:
`a = APIWrapper(config)` 
`a.find_media_with_min_duration()`  

## Available API methods:

Auth:
- register_config()
- register_quick()
- login(email, password)
- logout(user_id)
- deactivate(user_id)

Video:
- find_media()  
        Find any media item  
        returns: ('media_id', 'short_name', 'media_duration')

- find_media_without_adverts()  
        Find a media item without any adverts  
        returns: ('media_id', 'short_name', 'media_duration')

- find_media_with_preroll()  
        Find a media item with a preroll  
        returns: ('media_id', 'short_name')
 
- find_media_without_preroll()  
        Find a media item without a preroll  
        returns: ('media_id', 'short_name')

- find_media_with_two_midrolls()  
        Find a media item with at least two midrolls  
        returns: ('media_id', 'short_name', [midroll timestamps (seconds)])
        
- find_media_with_rating(rating)  
        Find a media item with the given rating  
        rating: 'Not Rated', 'PG' 'PG-13', 'TV-14', 'R'  
        returns: ('media_id', 'short_name')  
        
- find_media_with_min_duration(min_duration_mins)  
        Find a media item with the minimum duration  
        min_duration: minimum duration in minutes  
        returns: ('media_id', 'short_name')  

- find_media_with_subtitles()  
        Find a media item with subtitles   
        returns: ('media_id', 'short_name')  

Other:
- get_watchnow_tray_metadata()
        Get metatdata for all items in a Watch Now tray (slot)
        Platforms - iOS
        returns: list of dictionaries. one dictionary per item.

- get_genre_carousel_metadata(genre)
        Get metadata for all items in a Genre page (TV, Movies) Spotlight carousel
        Platforms - iOS
        genre: TV, Movies
        returns: list of dictionaries. one dictionary per item.

- def get_genre_all_metadata(genre):
        Get the metadata for all items on a TV or Movies page
        Platforms - iOS
        genre: TV, Movies
        returns: list of dictionaries. one dictionary per item.

- def get_series_with_min_episodes(self, min_episodes=1, auth=False):
        Get the metadata for all TV episodes that have at least
        min_episodes episodes
        returns: list of dictionaries. one dictionary per item


Animax specific:
- get_homepage_slideshow_metadata()
        Get metadata for all items in the homepage top slideshow
        platforms - Animax web
        ui component - Homepage slideshow
        returns: list of dictionaries. one dictionary per item

- get_show_genres()
        Get a list of all known Show genres
        returns: list of dictionaries. one dictionary per item

- get_shows_metadata()
        Get metadata for all Shows
        platforms - Animax web
        ui component - Show page media grid
        video_type: 'all', full', 'clips', 'trailers'
        genre: 'all' or an integer genre id returned from get_shows_genres()
        sort: date-desc, date-asc, alpha-asc, alpha-desc
        count: max number of items to retrieve
        returns: list of dictionaries. one dictionary per item

- get_auth_pin()
        Get the authorisation pin code from the send-pin endpoint

## Unit tests

`python tests.py TestHelpers`
