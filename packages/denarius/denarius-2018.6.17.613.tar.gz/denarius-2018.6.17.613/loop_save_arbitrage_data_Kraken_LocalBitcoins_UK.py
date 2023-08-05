#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# loop_save_arbitrage_data_Kraken_LocalBitcoins_UK                             #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program loop records Kraken LocalBitcoins UK arbitrage data.            #
#                                                                              #
# copyright (C) 2017 Will Breaden Madden, wbm@protonmail.ch                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

usage:
    program [options]

options:
    -h, --help      display help message
    --version       display version and exit

    --interval=INT  time between recordings (s)  [default: 30]
"""

name    = "loop_save_arbitrage_data_Kraken_LocalBitcoins_UK"
version = "2017-11-09T1905Z"
logo    = None

import docopt

import denarius

def main(options):

    denarius.loop_save_arbitrage_data_Kraken_LocalBitcoins_UK(
        interval = int(options["--interval"])
    )

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
