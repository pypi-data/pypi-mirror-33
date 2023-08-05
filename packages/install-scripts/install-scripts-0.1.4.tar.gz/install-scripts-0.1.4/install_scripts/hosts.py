"""LICENSE
Copyright 2017 Hermann Krumrey <hermann@krumreyh.com>

This file is part of install-scripts.

install-scripts is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

install-scripts is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with install-scripts.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from subprocess import Popen


def block_reddit():
    """
    Blocks reddit.com via the hosts file
    :return: None
    """
    block_domain("reddit.com")
    for subdomain in ["www", "np", "blog", "fr", "pay", "es", "en-us", "en",
                      "ru", "us", "de", "dd", "no", "pt", "ww", "ss", "4x",
                      "sv", "nl", "hw", "hr"]:
        block_domain(subdomain + ".reddit.com")


def block_domain(domain: str):
    """
    Blocks a domain using the hosts file
    :param domain: The domain to block
    :return: None
    """
    # Have to use a subprocess due to sudo
    Popen("sudo bash -c \"echo -e '\\n127.0.0.1\\t\\t"
          + domain + "\\n' >> /etc/hosts\"", shell=True).wait()
