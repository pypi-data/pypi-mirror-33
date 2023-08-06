#!/usr/bin/env python3

# pylint:disable=line-too-long
"""
The tool to check domains or IP availability.

::


    :::::::::  :::   ::: :::::::::: :::    ::: ::::    :::  ::::::::  :::::::::: :::::::::  :::        ::::::::::
    :+:    :+: :+:   :+: :+:        :+:    :+: :+:+:   :+: :+:    :+: :+:        :+:    :+: :+:        :+:
    +:+    +:+  +:+ +:+  +:+        +:+    +:+ :+:+:+  +:+ +:+        +:+        +:+    +:+ +:+        +:+
    +#++:++#+    +#++:   :#::+::#   +#+    +:+ +#+ +:+ +#+ +#+        +#++:++#   +#++:++#+  +#+        +#++:++#
    +#+           +#+    +#+        +#+    +#+ +#+  +#+#+# +#+        +#+        +#+    +#+ +#+        +#+
    #+#           #+#    #+#        #+#    #+# #+#   #+#+# #+#    #+# #+#        #+#    #+# #+#        #+#
    ###           ###    ###         ########  ###    ####  ########  ########## #########  ########## ##########

This submodule will give us the interface for VPN connection.

Author:
    Nissar Chababy, @funilrys, contactTATAfunilrysTODTODcom

Special thanks:
    https://pyfunceble.readthedocs.io/en/dev/special-thanks.html

Contributors:
    http://pyfunceble.readthedocs.io/en/dev/special-thanks.html

Project link:
    https://github.com/funilrys/PyFunceble

Project documentation:
    https://pyfunceble.readthedocs.io

Project homepage:
    https://funilrys.github.io/PyFunceble/

License:
::


    MIT License

    Copyright (c) 2017-2018 Nissar Chababy

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""
# pylint: enable=line-too-long

from tempfile import mkstemp
from base64 import b64decode

import PyFunceble
from PyFunceble import OrderedDict, directory_separator, path, requests, sleep
from PyFunceble.helpers import Dict, Download, Regex, File, Command


class VPN(object):
    """
    This class will help us interract with VPN connection.
    """

    def __init__(self):
        self.api_url = "http://www.vpngate.net/api/iphone/"
        self.countries_regex = "|".join(PyFunceble.CONFIGURATION["countries"])
        self.waiting_time = 30
        self.vpn_backup_file = PyFunceble.CURRENT_DIRECTORY + directory_separator + PyFunceble.OUTPUTS[
            "default_files"
        ][
            "vpn"
        ]

    def _is_needed(self, element):
        """
        This method check if a given element is relevant for the data we 
        are working with.

        Argument:
            - element: str
                The element to check.
        """

        if element[-1] not in ["", "*", "*vpn_servers"]:
            data = element[-1].split(",")

            if "CountryShort" in data or Regex(
                data[6], self.countries_regex, return_data=False
            ).match():
                return data

    def _extract_vpn_list(self):
        """
        This method will get the list of available VPN.
        """

        result = []

        for line in Download(self.api_url).to_list():
            result.append(line.split("\n"))

        return list(filter(lambda x: x, list(map(self._is_needed, result))))

    def _get_server_with_better_score(self, data, country_code):
        """
        This method return the server with the better score based on the given data.

        Argument:
            - data: dict
                A mirror of the extracted data.
            - country_code: str
                The country code to get.
        """

        identifiers = []
        scores = []

        for identifier, info in data.items():
            if info["CountryShort"] == country_code:
                identifiers.append(identifier)
                scores.append(int(info["Score"]))

        return data[identifiers[scores.index(max(scores))]]

    def generate_list_of_needed(self):
        """
        This method filter and generate the list of server so we only get the list of
        needed country.
        """

        result = OrderedDict()
        needed = OrderedDict()

        extracted = self._extract_vpn_list()
        keys = extracted[0]

        del extracted[0]

        identifier = 0
        for server in extracted:
            result[identifier] = OrderedDict(zip(keys, server))

            identifier += 1

        for country_code in PyFunceble.CONFIGURATION["countries"]:
            needed[country_code] = self._get_server_with_better_score(
                result, country_code
            )

        Dict(needed).to_json(self.vpn_backup_file)

    def _get_current_ip(self):
        """
        This method will get the current IP.
        """

        headers = {"User-Agent": "curl/7.30.0"}
        data = requests.get("https://ipinfo.io", headers=headers)

        if data.status_code == 200:
            info = data.json()
            return (info["ip"], info["country"])

        raise Exception("Unable to get IP address.")

    def connect(self, country_code):
        """
        This method will connect to the VPN with the given contry code.
        """
        if path.isfile(self.vpn_backup_file):
            _, temporary_file_path = mkstemp(None, "PyFunceble_")
            ip_before = self._get_current_ip()

            data = Dict().from_json(File(self.vpn_backup_file).read())[country_code]

            to_write = b64decode(data["OpenVPN_ConfigData_Base64"]).decode(
                "utf-8"
            ).replace(
                "\r", ""
            )
            to_write += "\nscript-security 2"
            to_write += "\nup /etc/openvpn/client/client.up"
            to_write += "\ndown /etc/openvpn/client/client.down"

            File(temporary_file_path).write(to_write)

            command_to_execute = "sudo openvpn --config %s" % temporary_file_path
            proc = Command(command_to_execute).in_background()

            sleep(self.waiting_time)
            ip_after = self._get_current_ip()

            if ip_before[0] != ip_after[0]:
                if ip_after[-1] == country_code:
                    print("Preparing cleaning")
                    Command().kill_process(proc)
                    print("done")
                else:
                    Command(None).kill_process(proc)
                    raise Exception(
                        "Expected country code: %s, got: %s"
                        % (repr(country_code), repr(ip_after[-1]))
                    )

            else:
                Command(None).kill_process(proc)
                raise Exception("IP not changed.")

        else:
            raise Exception("Unable to locate %s" % repr(self.vpn_backup_file))
