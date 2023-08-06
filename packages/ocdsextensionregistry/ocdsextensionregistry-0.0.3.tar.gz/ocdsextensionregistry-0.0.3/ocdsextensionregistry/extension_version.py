import re
from io import BytesIO
from urllib.parse import urlparse
from zipfile import ZipFile

import requests


class ExtensionVersion:
    def __init__(self, data):
        """
        Accepts a row from extension_versions.csv and assigns values to properties.
        """
        self.id = data['Id']
        self.date = data['Date']
        self.version = data['Version']
        self.base_url = data['Base URL']
        self.download_url = data['Download URL']
        self._file_cache = {}

    def update(self, other):
        """
        Merges in the properties of another Extension or ExtensionVersion object.
        """
        for k, v in other.as_dict().items():
            setattr(self, k, v)

    def as_dict(self):
        """
        Returns the object's public properties as a dictionary.
        """
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}

    def remote(self, basename):
        """
        Returns the contents of the file within the extension.

        If the extension has a download URL, downloads the ZIP archive and caches all its files' contents. Otherwise,
        downloads and caches the requested file's contents. Raises an HTTPError if a download fails, and a KeyError if
        the requested file isn't in the ZIP archive.
        """
        if basename not in self._file_cache:
            if not self.download_url:
                response = requests.get(self.base_url + basename)
                response.raise_for_status()
                self._file_cache[basename] = response.text
            elif not self._file_cache:
                response = requests.get(self.download_url, allow_redirects=True)
                response.raise_for_status()
                zipfile = ZipFile(BytesIO(response.content))
                names = zipfile.namelist()
                start = len(names[0])
                for name in names[1:]:
                    self._file_cache[name[start:]] = zipfile.read(name).decode('utf-8')

        return self._file_cache[basename]

    @property
    def metadata(self):
        """
        Retrieves and returns the extension's extension.json file as a dict.
        """
        return requests.get(self.base_url + 'extension.json').json()

    @property
    def repository_full_name(self):
        """
        Returns the full name of the extension's repository, which should be a unique identifier on the hosting
        service, e.g. open-contracting/ocds_bid_extension

        Experimental
        """
        return self._repository_property('full_name')

    @property
    def repository_name(self):
        """
        Returns the short name of the extension's repository, i.e. omitting any organizational prefix, which can be
        used to create directories, e.g. ocds_bid_extension

        Experimental
        """
        return self._repository_property('name')

    @property
    def repository_html_page(self):
        """
        Returns the URL to the landing page of the extension's repository, e.g.
        https://github.com/open-contracting/ocds_bid_extension

        Experimental
        """
        return self._repository_property('html_page')

    @property
    def repository_url(self):
        """
        Returns the URL of the extension's repository, in a format that can be input to a VCS program without
        modification, e.g. https://github.com/open-contracting/ocds_bid_extension.git

        Experimental
        """
        return self._repository_property('url')

    def _repository_full_name(self, parsed, config):
        return re.match(config['full_name:pattern'], parsed.path).group(1)

    def _repository_name(self, parsed, config):
        return re.match(config['name:pattern'], parsed.path).group(1)

    def _repository_html_page(self, parsed, config):
        return config['html_page:prefix'] + self._repository_full_name(parsed, config)

    def _repository_url(self, parsed, config):
        return config['url:prefix'] + self._repository_full_name(parsed, config) + config['url:suffix']

    def _repository_property(self, prop):
        parsed = urlparse(self.base_url)
        config = self._configuration(parsed)
        if config:
            return getattr(self, '_repository_' + prop)(parsed, config)
        else:
            raise NotImplementedError("can't determine {} from {}".format(prop, self.base_url))

    def _configuration(self, parsed):
        # Multiple websites are implemented to explore the robustness of the approach.
        #
        # Savannah has both cgit and GitWeb interfaces on the same domain, e.g.
        # "https://git.savannah.gnu.org/cgit/aspell.git/plain/COPYING?h=devel"
        # "https://git.savannah.gnu.org/gitweb/?p=aspell.git;a=blob_plain;f=COPYING;h=b1e3f5a2638797271cbc9b91b856c05ed6942c8f;hb=HEAD"
        #
        # If all interfaces could be disambiguated using the domain alone, we could implement the lookup of the
        # configuration as a dictionary. Since that's not the case, the lookup is implemented as a method.
        netloc = parsed.netloc
        if netloc == 'bitbucket.org':
            # A base URL may look like: https://bitbucket.org/facebook/hgsql/raw/default/
            return {
                'full_name:pattern': r'\A/([^/]+/[^/]+)',
                'name:pattern': r'\A/[^/]+/([^/]+)',
                'html_page:prefix': 'https://bitbucket.org/',
                'url:prefix': 'https://bitbucket.org/',
                'url:suffix': '.git',  # assumes Git not Mercurial, which can't be disambiguated using the base URL
            }
        elif netloc == 'raw.githubusercontent.com':
            # Sample base URL: https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.3/
            return {
                'full_name:pattern': r'\A/([^/]+/[^/]+)',
                'name:pattern': r'\A/[^/]+/([^/]+)',
                'html_page:prefix': 'https://github.com/',
                'url:prefix': 'git@github.com:',
                'url:suffix': '.git',
            }
        elif netloc == 'gitlab.com':
            # A base URL may look like: https://gitlab.com/gitlab-org/gitter/env/raw/master/
            return {
                'full_name:pattern': r'\A/(.+)/raw/',
                'name:pattern': r'/([^/]+)/raw/',
                'html_page:prefix': 'https://gitlab.com/',
                'url:prefix': 'https://gitlab.com/',
                'url:suffix': '.git',
            }
