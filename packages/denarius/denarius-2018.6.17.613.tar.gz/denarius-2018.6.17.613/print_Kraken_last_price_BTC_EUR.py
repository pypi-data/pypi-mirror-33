#!/usr/bin/env python

"""
################################################################################
#                                                                              #
# print_Kraken_last_price_BTC_EUR                                              #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program prints the last Kraken Bitcoin price in Euros.                  #
#                                                                              #
# copyright (C) 2018 William Breaden Madden                                    #
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
"""

import sys

import denarius.Kraken

name    = "print_Kraken_last_price_BTC_EUR"
version = "2018-01-31T0002Z"

def main():

    denarius.Kraken.start_API()
    print(denarius.Kraken.last_price_XBT_EUR())

if __name__ == "__main__":
    main()
