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

This submodule will provide the referer extraction interface.

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
# pylint: disable=bad-continuation
import PyFunceble
from PyFunceble import requests
from PyFunceble.helpers import Dict, File
from PyFunceble.status import Status


class Referer(object):  # pragma: no cover
    """
    Get the WHOIS server (referer) of the current domain extension according to
        the IANA database.
    """

    def __init__(self):
        self.domain_extension = PyFunceble.CONFIGURATION["domain"][
            PyFunceble.CONFIGURATION["domain"].rindex(".") + 1:
        ]

        self.ignored_extension = [
            "ad",
            "al",
            "an",
            "ao",
            "aq",
            "arpa",
            "az",
            "ba",
            "bb",
            "bd",
            "bf",
            "bh",
            "bl",
            "bq",
            "bs",
            "bt",
            "bv",
            "cg",
            "ck",
            "cu",
            "cv",
            "cw",
            "cy",
            "dj",
            "doosan",
            "eg",
            "eh",
            "er",
            "et",
            "fk",
            "flsmidth",
            "fm",
            "gb",
            "gm",
            "gn",
            "gp",
            "gr",
            "gt",
            "gu",
            "gw",
            "htc",
            "iinet",
            "jm",
            "jo",
            "kh",
            "km",
            "kp",
            "lb",
            "lr",
            "mc",
            "mh",
            "mil",
            "mm",
            "mt",
            "mv",
            "mw",
            "ne",
            "ni",
            "np",
            "nr",
            "pa",
            "pg",
            "ph",
            "pk",
            "pn",
            "py",
            "sd",
            "sr",
            "ss",
            "sv",
            "sz",
            "tj",
            "tp",
            "tt",
            "va",
            "vi",
            "vn",
            "ye",
            "zw",
        ]

    @classmethod
    def _iana_database(cls):
        """
        Convert `iana-domains-db.json` into a dictionnary.
        """

        file_to_read = PyFunceble.CURRENT_DIRECTORY + PyFunceble.OUTPUTS[
            "default_files"
        ][
            "iana"
        ]

        return Dict().from_json(File(file_to_read).read())

    def get(self):
        """
        Return the referer aka the WHOIS server of the current domain extension.
        """

        if not PyFunceble.CONFIGURATION["no_whois"]:
            if self.domain_extension not in self.ignored_extension:
                referer = None

                if PyFunceble.CONFIGURATION["iana_db"] == {}:
                    PyFunceble.CONFIGURATION["iana_db"].update(self._iana_database())

                if self.domain_extension in PyFunceble.CONFIGURATION["iana_db"]:
                    referer = PyFunceble.CONFIGURATION["iana_db"][self.domain_extension]

                    if referer is None:
                        self.log()
                        return Status(PyFunceble.STATUS["official"]["down"]).handle()

                    return referer

                return Status(PyFunceble.STATUS["official"]["invalid"]).handle()

            return Status(PyFunceble.STATUS["official"]["down"]).handle()

        return None

    def log(self):
        """
        Log if no referer is found for a domain extension.
        """

        if PyFunceble.CONFIGURATION["logs"]:
            logs = "=" * 100
            logs += "\nNo referer found for: %s domains\n" % self.domain_extension
            logs += "=" * 100
            logs += "\n"

            File(
                PyFunceble.CURRENT_DIRECTORY
                + PyFunceble.OUTPUTS["parent_directory"]
                + PyFunceble.OUTPUTS["logs"]["directories"]["parent"]
                + PyFunceble.OUTPUTS["logs"]["directories"]["no_referer"]
                + self.domain_extension
            ).write(
                logs
            )

            if PyFunceble.CONFIGURATION["share_logs"]:
                data_to_share = {"extension": self.domain_extension}

                requests.post(PyFunceble.LINKS["api_no_referer"], data=data_to_share)
