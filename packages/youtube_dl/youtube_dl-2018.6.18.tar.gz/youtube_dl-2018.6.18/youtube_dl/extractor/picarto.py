# coding: utf-8
from __future__ import unicode_literals

import time

from .common import InfoExtractor
from ..compat import compat_str
from ..utils import (
    ExtractorError,
    js_to_json,
    try_get,
    update_url_query,
    urlencode_postdata,
)


class PicartoIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www.)?picarto\.tv/(?P<id>[a-zA-Z0-9]+)'
    _TEST = {
        'url': 'https://picarto.tv/Setz',
        'info_dict': {
            'id': 'Setz',
            'ext': 'mp4',
            'title': 're:^Setz [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}$',
            'timestamp': int,
            'is_live': True
        },
        'skip': 'Stream is offline',
    }

    @classmethod
    def suitable(cls, url):
        return False if PicartoVodIE.suitable(url) else super(PicartoIE, cls).suitable(url)

    def _real_extract(self, url):
        channel_id = self._match_id(url)
        stream_page = self._download_webpage(url, channel_id)

        if '>This channel does not exist' in stream_page:
            raise ExtractorError(
                'Channel %s does not exist' % channel_id, expected=True)

        player = self._parse_json(
            self._search_regex(
                r'(?s)playerSettings\[\d+\]\s*=\s*(\{.+?\}\s*\n)', stream_page,
                'player settings'),
            channel_id, transform_source=js_to_json)

        if player.get('online') is False:
            raise ExtractorError('Stream is offline', expected=True)

        cdn_data = self._download_json(
            'https://picarto.tv/process/channel', channel_id,
            data=urlencode_postdata({'loadbalancinginfo': channel_id}),
            note='Downloading load balancing info')

        def get_event(key):
            return try_get(player, lambda x: x['event'][key], compat_str) or ''

        params = {
            'token': player.get('token') or '',
            'ticket': get_event('ticket'),
            'con': int(time.time() * 1000),
            'type': get_event('ticket'),
            'scope': get_event('scope'),
        }

        prefered_edge = cdn_data.get('preferedEdge')
        default_tech = player.get('defaultTech')

        formats = []

        for edge in cdn_data['edges']:
            edge_ep = edge.get('ep')
            if not edge_ep or not isinstance(edge_ep, compat_str):
                continue
            edge_id = edge.get('id')
            for tech in cdn_data['techs']:
                tech_label = tech.get('label')
                tech_type = tech.get('type')
                preference = 0
                if edge_id == prefered_edge:
                    preference += 1
                if tech_type == default_tech:
                    preference += 1
                format_id = []
                if edge_id:
                    format_id.append(edge_id)
                if tech_type == 'application/x-mpegurl' or tech_label == 'HLS':
                    format_id.append('hls')
                    formats.extend(self._extract_m3u8_formats(
                        update_url_query(
                            'https://%s/hls/%s/index.m3u8'
                            % (edge_ep, channel_id), params),
                        channel_id, 'mp4', preference=preference,
                        m3u8_id='-'.join(format_id), fatal=False))
                    continue
                elif tech_type == 'video/mp4' or tech_label == 'MP4':
                    format_id.append('mp4')
                    formats.append({
                        'url': update_url_query(
                            'https://%s/mp4/%s.mp4' % (edge_ep, channel_id),
                            params),
                        'format_id': '-'.join(format_id),
                        'preference': preference,
                    })
                else:
                    # rtmp format does not seem to work
                    continue
        self._sort_formats(formats)

        mature = player.get('mature')
        if mature is None:
            age_limit = None
        else:
            age_limit = 18 if mature is True else 0

        return {
            'id': channel_id,
            'title': self._live_title(channel_id),
            'is_live': True,
            'thumbnail': player.get('vodThumb'),
            'age_limit': age_limit,
            'formats': formats,
        }


class PicartoVodIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www.)?picarto\.tv/videopopout/(?P<id>[^/?#&]+)'
    _TESTS = [{
        'url': 'https://picarto.tv/videopopout/ArtofZod_2017.12.12.00.13.23.flv',
        'md5': '3ab45ba4352c52ee841a28fb73f2d9ca',
        'info_dict': {
            'id': 'ArtofZod_2017.12.12.00.13.23.flv',
            'ext': 'mp4',
            'title': 'ArtofZod_2017.12.12.00.13.23.flv',
            'thumbnail': r're:^https?://.*\.jpg'
        },
    }, {
        'url': 'https://picarto.tv/videopopout/Plague',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)

        vod_info = self._parse_json(
            self._search_regex(
                r'(?s)#vod-player["\']\s*,\s*(\{.+?\})\s*\)', webpage,
                video_id),
            video_id, transform_source=js_to_json)

        formats = self._extract_m3u8_formats(
            vod_info['vod'], video_id, 'mp4', entry_protocol='m3u8_native',
            m3u8_id='hls')
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': video_id,
            'thumbnail': vod_info.get('vodThumb'),
            'formats': formats,
        }
