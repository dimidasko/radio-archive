# radio-archive
Searchable archive of favorite radio shows

ERT, the Greek National Radio service offers amazing content for Greek speaking listeners through the webiste
https://www.ertecho.gr/
and the ertecho mobile app. However, both of them are missing useful features
- there is no way to easily follow your preferred shows
- the weekly program has no link to the show pages
- the search feature is not very effective in finding sessions based on their detailed descriptions
- the network streaming player does not cache audio very well and this blocks sound on bluetooth devices while walking about with weak network connectivity and sound never recovers even when connectivity is restored

This project is an attempt to provide a better experience for the radio listeners by allowing easier access to radio streaming of personally favorite shows without the hassle of searching through the archives of all the offered shows every time to find the newly available sessions. Network streaming functions much better with default mobile browser audio player for mp3 urls, with no hickups due to network connectivity.

## Files
The project has these main parts
- index.html the main web app code which is served at https://dimidasko.github.io/radio-archive/
- active_shows.json is a selection of favorite radio shows which the web app loads by default to allow easy navigation and session search
- available_shows.json is a list of all radio shows in all main radio stations of ertecho to allow easy discovery of new interesting shows
- discover-shows.py is a python script to create the available_shows.json
- update-archive.py is a python script to create bookmarks of previously aired sessions of favorite shows
- other json files are the archives of previously aired sessions 

## Disclaimer
The web app relies on published data, all available through the ertecho website. It is merely a bookmarking application to allow easy navigation through personal preferences for radio shows. If you are as frustrated as I was trying to listen to ertecho radio shows on the go, fork and use with your preferred shows in active_shows.json
