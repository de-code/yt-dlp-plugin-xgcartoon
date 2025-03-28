# pylint: disable=abstract-method

import re
from yt_dlp.extractor.common import InfoExtractor


class LineCartoonVideoIE(InfoExtractor):
    _VALID_URL: str = (
        r'https?://www\.lincartoon\.com/video/(?P<playlist_id>[^/]+)/(?P<id>[^/]+)(?:\.html)'  # type: ignore
    )

    def _real_extract(self, url):
        url_match = self._match_valid_url(url)
        playlist_id = url_match.group('playlist_id')
        display_id = url_match.group('id')
        self.to_screen(f'[info] playlist_id: {playlist_id}')
        webpage = self._download_webpage(url, display_id)

        playlist_title = self._search_regex(
            r'<a[^>]+"breadcrumb-item"[^>]*>([^<]+)</a>[^<]*<li',
            string=webpage,
            name='playlist-title'
        ).strip()
        self.to_screen(f'[info] playlist_title: {playlist_title}')

        title = self._search_regex(
            r'<li[^>]+"breadcrumb-item active"[^>]*>([^<]+)</li>',
            string=webpage,
            name='title'
        ).strip()
        self.to_screen(f'[info] title: {title}')

        player_video_id = self._search_regex(
            r'https://pframe\.xgcartoon\.com/player\.htm\?vid=([^&]+)',
            string=webpage,
            name='player_video_id'
        ).strip()
        self.to_screen(f'player_video_id: {player_video_id}')

        m3u8_url = f'https://xgct-video.vzcdn.net/{player_video_id}/842x480/video.m3u8'
        self.to_screen(f'[info] m3u8_url: {m3u8_url}')

        formats = self._extract_m3u8_formats(
            m3u8_url,
            display_id,
            'mp4',
            'm3u8_native',
            m3u8_id='hls',
            note='Downloading m3u8 information',
            errnote='Unable to download m3u8 information'
        )

        return {
            'id': display_id,
            'title': title,
            'formats': formats
        }


class XgCartoonPlaylistIE(InfoExtractor):
    _VALID_URL: str = r'https?://www\.xgcartoon\.com/detail/(?P<playlist_id>[^/]+)/?$'  # type: ignore
    _REDIRECT_URL = (
        r'/user/page_direct\?cartoon_id=(?P<playlist_id>[^&]+)&(?:amp;)?chapter_id=(?P<id>[^"]+)"'
    )
    _URL_TEMPLATE = r'https://www.lincartoon.com/video/{playlist_id}/{id}.html'

    def _entries(self, webpage):
        for url_match in re.finditer(
            self._REDIRECT_URL,
            webpage
        ):
            yield self.url_result(
                self._URL_TEMPLATE.format(
                    playlist_id=url_match.group('playlist_id'),
                    id=url_match.group('id')
                ),
                LineCartoonVideoIE.ie_key()
            )

    def _real_extract(self, url):
        url_match = self._match_valid_url(url)
        playlist_id = url_match.group('playlist_id')
        self.to_screen(f'[info] playlist_id: {playlist_id}')
        webpage = self._download_webpage(url, playlist_id)

        playlist_title = self._html_search_regex(
            r'<h1[^>]*>([^<]+)</h1>',
            string=webpage,
            name='playlist-title'
        ).strip()
        self.to_screen(f'[info] playlist_title: {playlist_title}')

        entries = list(self._entries(webpage=webpage))

        return self.playlist_result(
            entries,
            playlist_id=playlist_id,
            playlist_title=playlist_title
        )
