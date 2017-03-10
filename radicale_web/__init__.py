# This file is part of Radicale Web.
# Copyright © 2017 Unrud <unrud@openaliasbox.org>
#
# Radicale Web is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Radicale Web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Radicale Web.  If not, see <http://www.gnu.org/licenses/>.

import os
import posixpath
import radicale
import time

from http import client

VERSION = "2.0.0"

MIMETYPES = {
    ".css": "text/css",
    ".eot": "application/vnd.ms-fontobject",
    ".gif": "image/gif",
    ".html": "text/html",
    ".js": "application/javascript",
    ".manifest": "text/cache-manifest",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".ttf": "application/font-sfnt",
    ".txt": "text/plain",
    ".woff": "application/font-woff",
    ".woff2": "font/woff2",
    ".xml": "text/xml"}
FALLBACK_MIMETYPE = "application/octet-stream"

class Web:
    def __init__(self, configuration, logger):
        self.configuration = configuration
        self.logger = logger
        self.folder = os.path.join(os.path.dirname(__file__), "web")

    def get(self, environ, base_prefix, path, user):
        try:
            filesystem_path = radicale.storage.path_to_filesystem(
                self.folder, path[len("/.web"):])
        except ValueError as e:
            self.logger.debug(e)
            return radicale.NOT_FOUND
        if os.path.isdir(filesystem_path) and not path.endswith("/"):
            location = posixpath.basename(path) + "/"
            return (client.SEE_OTHER,
                    {"Location": location, "Content-Type": "text/plain"},
                    "Redirected to %s" % location)
        if os.path.isdir(filesystem_path):
            filesystem_path = os.path.join(filesystem_path, "index.html")
        if not os.path.isfile(filesystem_path):
            return radicale.NOT_FOUND
        content_type = MIMETYPES.get(
            os.path.splitext(filesystem_path)[1].lower(), FALLBACK_MIMETYPE)
        with open(filesystem_path, "rb") as f:
            answer = f.read()
            last_modified = time.strftime(
                "%a, %d %b %Y %H:%M:%S GMT",
                time.gmtime(os.fstat(f.fileno()).st_mtime))
        headers = {
            "Content-Type": content_type,
            "Last-Modified": last_modified}
        return client.OK, headers, answer
