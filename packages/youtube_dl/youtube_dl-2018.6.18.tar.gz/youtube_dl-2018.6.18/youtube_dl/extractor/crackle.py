# coding: utf-8
from __future__ import unicode_literals, division

import re

from .common import InfoExtractor
from ..compat import (
    compat_str,
    compat_HTTPError,
)
from ..utils import (
    determine_ext,
    float_or_none,
    int_or_none,
    parse_age_limit,
    parse_duration,
    ExtractorError
)


class CrackleIE(InfoExtractor):
    _VALID_URL = r'(?:crackle:|https?://(?:(?:www|m)\.)?(?:sony)?crackle\.com/(?:playlist/\d+/|(?:[^/]+/)+))(?P<id>\d+)'
    _TESTS = [{
        # geo restricted to CA
        'url': 'https://www.crackle.com/andromeda/2502343',
        'info_dict': {
            'id': '2502343',
            'ext': 'mp4',
            'title': 'Under The Night',
            'description': 'md5:d2b8ca816579ae8a7bf28bfff8cefc8a',
            'duration': 2583,
            'view_count': int,
            'average_rating': 0,
            'age_limit': 14,
            'genre': 'Action, Sci-Fi',
            'creator': 'Allan Kroeker',
            'artist': 'Keith Hamilton Cobb, Kevin Sorbo, Lisa Ryder, Lexa Doig, Robert Hewitt Wolfe',
            'release_year': 2000,
            'series': 'Andromeda',
            'episode': 'Under The Night',
            'season_number': 1,
            'episode_number': 1,
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        }
    }, {
        'url': 'https://www.sonycrackle.com/andromeda/2502343',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        country_code = self._downloader.params.get('geo_bypass_country', None)
        countries = [country_code] if country_code else (
            'US', 'AU', 'CA', 'AS', 'FM', 'GU', 'MP', 'PR', 'PW', 'MH', 'VI')

        last_e = None

        for country in countries:
            try:
                media = self._download_json(
                    'https://web-api-us.crackle.com/Service.svc/details/media/%s/%s'
                    % (video_id, country), video_id,
                    'Downloading media JSON as %s' % country,
                    'Unable to download media JSON', query={
                        'disableProtocols': 'true',
                        'format': 'json'
                    })
            except ExtractorError as e:
                # 401 means geo restriction, trying next country
                if isinstance(e.cause, compat_HTTPError) and e.cause.code == 401:
                    last_e = e
                    continue
                raise

            media_urls = media.get('MediaURLs')
            if not media_urls or not isinstance(media_urls, list):
                continue

            title = media['Title']

            formats = []
            for e in media['MediaURLs']:
                if e.get('UseDRM') is True:
                    continue
                format_url = e.get('Path')
                if not format_url or not isinstance(format_url, compat_str):
                    continue
                ext = determine_ext(format_url)
                if ext == 'm3u8':
                    formats.extend(self._extract_m3u8_formats(
                        format_url, video_id, 'mp4', entry_protocol='m3u8_native',
                        m3u8_id='hls', fatal=False))
                elif ext == 'mpd':
                    formats.extend(self._extract_mpd_formats(
                        format_url, video_id, mpd_id='dash', fatal=False))
            self._sort_formats(formats)

            description = media.get('Description')
            duration = int_or_none(media.get(
                'DurationInSeconds')) or parse_duration(media.get('Duration'))
            view_count = int_or_none(media.get('CountViews'))
            average_rating = float_or_none(media.get('UserRating'))
            age_limit = parse_age_limit(media.get('Rating'))
            genre = media.get('Genre')
            release_year = int_or_none(media.get('ReleaseYear'))
            creator = media.get('Directors')
            artist = media.get('Cast')

            if media.get('MediaTypeDisplayValue') == 'Full Episode':
                series = media.get('ShowName')
                episode = title
                season_number = int_or_none(media.get('Season'))
                episode_number = int_or_none(media.get('Episode'))
            else:
                series = episode = season_number = episode_number = None

            subtitles = {}
            cc_files = media.get('ClosedCaptionFiles')
            if isinstance(cc_files, list):
                for cc_file in cc_files:
                    if not isinstance(cc_file, dict):
                        continue
                    cc_url = cc_file.get('Path')
                    if not cc_url or not isinstance(cc_url, compat_str):
                        continue
                    lang = cc_file.get('Locale') or 'en'
                    subtitles.setdefault(lang, []).append({'url': cc_url})

            thumbnails = []
            images = media.get('Images')
            if isinstance(images, list):
                for image_key, image_url in images.items():
                    mobj = re.search(r'Img_(\d+)[xX](\d+)', image_key)
                    if not mobj:
                        continue
                    thumbnails.append({
                        'url': image_url,
                        'width': int(mobj.group(1)),
                        'height': int(mobj.group(2)),
                    })

            return {
                'id': video_id,
                'title': title,
                'description': description,
                'duration': duration,
                'view_count': view_count,
                'average_rating': average_rating,
                'age_limit': age_limit,
                'genre': genre,
                'creator': creator,
                'artist': artist,
                'release_year': release_year,
                'series': series,
                'episode': episode,
                'season_number': season_number,
                'episode_number': episode_number,
                'thumbnails': thumbnails,
                'subtitles': subtitles,
                'formats': formats,
            }

        raise last_e
