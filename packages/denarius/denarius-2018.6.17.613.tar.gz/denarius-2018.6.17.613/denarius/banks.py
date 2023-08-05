# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# banks                                                                        #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program provides banking and other utilities.                           #
#                                                                              #
# copyright (C) 2018 William Breaden Madden, Liam Moore                        #
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

from difflib import SequenceMatcher
import logging
import os
import re
import requests
import sys

import pandas as pd
import pyprel
from pymonzo import MonzoAPI
import technicolor

name        = "banks"
__version__ = "2018-06-03T1823Z"

log = logging.getLogger(__name__)
log.addHandler(technicolor.ColorisingStreamHandler())
log.setLevel(logging.INFO)

def bank_access_ok(
    bank = None
    ):
    """
    Check bank API access.
    """
    try:
        if bank == "Monzo":     df = transactions_DataFrame_Monzo()
        if bank == "RBS":       df = transactions_DataFrame_RBS()
        if bank == "Santander": df = transactions_DataFrame_Santander()
        if bank == "Starling":  df = transactions_DataFrame_Starling()
        if isinstance(df, pd.DataFrame):
            return True
        else:
            return False
    except:
        log.error("error -- no bank access")
        return False

def transactions_DataFrame_Monzo(
    print_table          = False
    ):
    """
    Return a DataFrame of bank account transactions.
    """
    # API
    try:
        monzo = MonzoAPI()
        transactions = [transaction._raw_data for transaction in monzo.transactions()]
    except:
        log.error("error accessing Monzo API")
        return False
    # DataFrame
    df = pd.DataFrame(columns = [
        "datetime",
        "amount",
        "description",
        "notes",
        "counterparty_reference",
        "counterparty_account_number",
        "counterparty_sort_code",
        "counterparty_name",
        "currency",
        "category",
        "scheme",
        "id"
    ])
    for transaction in transactions:
        try:
            counterparty_account_number = transaction["counterparty"]["account_number"]
            counterparty_sort_code      = transaction["counterparty"]["sort_code"]
            counterparty_name           = transaction["counterparty"]["name"]
            counterparty_reference      = transaction["description"]
        except:
            counterparty_account_number = "-"
            counterparty_sort_code      = "-"
            counterparty_name           = "-"
            counterparty_reference      = "-"
        try:
            try:
                counterparty_account_number = transaction["counterparty"]["account_number"]
                counterparty_sort_code      = transaction["counterparty"]["sort_code"]
                counterparty_name           = transaction["counterparty"]["name"]
                counterparty_reference      = transaction["description"]
            except:
                counterparty_account_number = "-"
                counterparty_sort_code      = "-"
                counterparty_name           = "-"
                counterparty_reference      = "-"
            df = df.append(
                {
                    "datetime"                   : pd.to_datetime(transaction["created"]).to_pydatetime(),
                    "amount"                     : float(transaction["amount"]) / float(100),
                    "description"                : transaction["description"],
                    "notes"                      : transaction["notes"],
                    "counterparty_reference"     : counterparty_reference,
                    "counterparty_account_number": counterparty_account_number,
                    "counterparty_sort_code"     : counterparty_sort_code,
                    "counterparty_name"          : counterparty_name,
                    "currency"                   : transaction["currency"],
                    "category"                   : transaction["category"],
                    "scheme"                     : transaction["scheme"],
                    "id"                         : transaction["id"]
                },
                ignore_index = True
            )
        except:
            log.error("error -- transactions DataFrame Monzo")
            pass
    if print_table:
        print(table_transactions(df = df))
    return df

def transactions_DataFrame_RBS(
    filepath_credentials = "~/.rbs",
    print_table          = False
    ):
    """
    Return a DataFrame of bank account transactions.
    """
    # credentials
    if not filepath_credentials:
        filepath_credentials = "~/.rbs"
    filepath_credentials = os.path.expanduser(filepath_credentials)
    if not os.path.isfile(filepath_credentials):
        log.error("no credentials file {filepath} found".format(filepath = filepath_credentials))
        sys.exit()
    with open(filepath_credentials, "r") as file_credentials:
        credentials_string = file_credentials.read()
    credentials = {}
    exec(credentials_string, credentials)
    token        = credentials["token_teller"]
    account_code = credentials["account_code_teller"]
    # API
    try:
        URL      = "https://api.teller.io/accounts/" + account_code + "/transactions"
        headers  = {"Authorization": "Bearer " + token}
        data     = {"" : ""}
        response = requests.get(URL, json = data, headers = headers).json()
    except:
        log.error("error accessing Teller RBS API")
        return False
    # DataFrame
    df = pd.DataFrame(columns = ["date"])
    for transaction in response:
        df = df.append(
            {
                "date"                  : transaction["date"],
                "counterparty_reference": transaction["counterparty"],
                "description"           : transaction["description"],
                "id"                    : transaction["id"],
                "amount"                : float(transaction["amount"])
            },
            ignore_index = True
        )
    if print_table:
        print(table_transactions(df = df))
    return df

def transactions_DataFrame_Starling(
    filepath_credentials = None,
    print_table          = False
    ):
    """
    Return a DataFrame of bank account transactions.
    """
    # credentials
    if not filepath_credentials:
        filepath_credentials = "~/.starling"
    filepath_credentials = os.path.expanduser(filepath_credentials)
    if not os.path.isfile(filepath_credentials):
        log.error("no credentials file {filepath} found".format(filepath = filepath_credentials))
        sys.exit()
    with open(filepath_credentials, "r") as file_credentials:
        token = file_credentials.readline().strip("\n")
    # API
    try:
        URL      = "https://api.starlingbank.com/api/v1/transactions"
        headers  = {"Authorization": "Bearer " + token}
        data     = {"" : ""}
        response = requests.get(URL, json = data, headers = headers).json()
    except:
        log.error("error accessing Starling API")
        return False
    # DataFrame
    df = pd.DataFrame(columns = ["datetime"])
    for transaction in response["_embedded"]["transactions"]:
        df = df.append(
            {
                "datetime"              : pd.to_datetime(transaction["created"]).to_pydatetime(),
                "counterparty_reference": transaction["narrative"],
                "id"                    : transaction["id"],
                "amount"                : float(transaction["amount"]),
                "balance"               : float(transaction["balance"]),
                "currency"              : transaction["currency"]
            },
            ignore_index = True
        )
    if print_table:
        print(table_transactions(df = df))
    return df

def transactions_DataFrame_bank(
    bank                 = None,
    filepath_credentials = None,
    print_table          = False
    ):
    try:
        if bank == "Monzo":
            return transactions_DataFrame_Monzo(
                print_table          = print_table
            )["valid"]
        elif bank == "RBS":
            if not filepath_credentials:
                filepath_credentials = "~/.rbs"
            return transactions_DataFrame_RBS(
                filepath_credentials = filepath_credentials,
                print_table          = print_table
            )["valid"]
        elif bank == "Starling":
            if not filepath_credentials:
                filepath_credentials = "~/.starling"
            return transactions_DataFrame_Starling(
                filepath_credentials = filepath_credentials,
                print_table          = print_table
            )["valid"]
        elif bank == "Santander":
            return transactions_DataFrame_Santander(
                print_table          = print_table
            )["valid"]
        else:
            return False
    except:
        log.error("error -- transactions DataFrame bank")
        return False

def refs_match(
    ref_supplied = None,
    ref_required = None,
    tolerance = 0.85
    ):
    """
    Attempt to determine if references approximately match, returning a boolean
    """
    return SequenceMatcher(None, str(ref_supplied), str(ref_required)).ratio() > tolerance

def payment_in_transactions(
    df          = None,
    reference   = None,
    name_payer  = None,
    amount      = None,
    print_table = False
    ):
    """
    Search the fields "counterparty_reference", "description" and "notes" (if it
    exists) for a specified reference in a specified transactions DataFrame. If
    the reference is found, check the amount of the payment is correct by
    comparing the specified amount with the "amount" field. If a payer name is
    specified, check the payer name specified against the payer name of the transaction.

    Return a dictionary of the following form:

    {
        "reference_found"    : bool,         # True if reference found
        "payer_name_match"   : bool or None, # True if payer name matched, False if payer name not matched, None if no payer name to check
        "payer_name_observed": string,       # payer name observed
        "amount_correct"     : bool,         # True if sum of amounts found is amount specified
        "valid"              : bool,         # True if reference found and amount correct
        "transactions"       : DataFrame,    # DataFrame of matches
        "amount_difference"  : float         # difference between amount specified and sum of amounts found
    }
    """
    try:
        reference = str(reference)
        amount    = float(amount)

        # ugly as sin but it's not possible to do pattern matching queries in regular pandas
        matches=pd.DataFrame()
        refs = []

        if "notes" in df.columns:
            refs = refs + list(df["notes"])
        if "description" in df.columns:
            refs = refs + list(df["description"])
        if "counterparty_reference" in df.columns:
            refs = refs + list(df["counterparty_reference"])

        # need to allow case where multiple refs fuzzymatch
        matching_refs = [ref for ref in refs if refs_match(reference, ref)]

        for matching_ref in matching_refs:
            if "notes" in df.columns:
                matches = matches.append(df[(df["notes"].str.contains(matching_ref, na=False))])
            if "description" in df.columns:
                matches = matches.append(df[(df["description"].str.contains(matching_ref, na=False))])
            if "counterparty_reference" in df.columns:
                matches = matches.append(df[(df["counterparty_reference"].str.contains(matching_ref, na=False))])

        reference_found   = not matches.empty
        amount_correct    = sum(matches["amount"].values) == amount

        if name_payer and "counterparty_name" in df.columns:
            payer_name_observed = matches["counterparty_name"].values[0]
            payer_name_match    = names_match(name_1 = name_payer, name_2 = payer_name_observed)
        else:
            payer_name_observed = None
            payer_name_match    = None
        if payer_name_match == None:
            valid = reference_found and amount_correct
        else:
            valid = reference_found and amount_correct and payer_name_match
        amount_difference = amount - sum(matches["amount"].values)
        #if print_table:
        #    #print(table_transactions(df = matches))
        return {
            "reference_found"    : reference_found,
            "payer_name_match"   : payer_name_match,
            "payer_name_observed": payer_name_observed,
            "amount_correct"     : amount_correct,
            "valid"              : valid,
            "amount_difference"  : amount_difference,
            "transactions"       : matches
        }
    except Exception as e:
        print("error evaluating payment_in_transactions", e)
        return {
            "reference_found"    : False,
            "payer_name_match"   : None,
            "payer_name_observed": None,
            "amount_correct"     : False,
            "valid"              : False,
            "amount_difference"  : False,
            "transactions"       : False
        }

def payment_in_transactions_original(
    df          = None,
    reference   = None,
    name_payer  = None,
    amount      = None,
    print_table = False
    ):
    """
    Search the fields "counterparty_reference", "description" and "notes" (if it
    exists) for a specified reference in a specified transactions DataFrame. If
    the reference is found, check the amount of the payment is correct by
    comparing the specified amount with the "amount" field. If a payer name is
    specified, check the payer name specified against the payer name of the transaction.

    Return a dictionary of the following form:

    {
        "reference_found"    : bool,         # True if reference found
        "payer_name_match"   : bool or None, # True if payer name matched, False if payer name not matched, None if no payer name to check
        "payer_name_observed": string,       # payer name observed
        "amount_correct"     : bool,         # True if sum of amounts found is amount specified
        "valid"              : bool,         # True if reference found and amount correct
        "transactions"       : DataFrame,    # DataFrame of matches
        "amount_difference"  : float         # difference between amount specified and sum of amounts found
    }
    """
    try:
        reference = str(reference)
        amount    = float(amount)
        if "notes" in df.columns:
            matches = df[(df["counterparty_reference"].str.contains(reference)) | (df["description"].str.contains(reference)) | (df["notes"].str.contains(reference))]
        elif "description" in df.columns:
            matches = df[(df["counterparty_reference"].str.contains(reference)) | (df["description"].str.contains(reference))]
        else:
            matches = df[(df["counterparty_reference"].str.contains(reference))]
        reference_found   = not matches.empty
        amount_correct    = sum(matches["amount"].values) == amount
        if name_payer and "counterparty_name" in df.columns:
            payer_name_observed = matches["counterparty_name"].values[0]
            payer_name_match    = names_match(name_1 = name_payer, name_2 = payer_name_observed)
        else:
            payer_name_observed = None
            payer_name_match    = None
        if payer_name_match == None:
            valid = reference_found and amount_correct
        else:
            valid = reference_found and amount_correct and payer_name_match
        amount_difference = amount - sum(matches["amount"].values)
        if print_table:
            print(table_transactions(df = matches))
        return {
            "reference_found"    : reference_found,
            "payer_name_match"   : payer_name_match,
            "payer_name_observed": payer_name_observed,
            "amount_correct"     : amount_correct,
            "valid"              : valid,
            "amount_difference"  : amount_difference,
            "transactions"       : matches
        }
    except:
        return {
            "reference_found"    : False,
            "payer_name_match"   : None,
            "payer_name_observed": None,
            "amount_correct"     : False,
            "valid"              : False,
            "amount_difference"  : False,
            "transactions"       : False
        }

def payment_in_transactions_Monzo(
    reference            = None,
    name_payer           = None,
    amount               = None,
    print_table          = False
    ):
    return payment_in_transactions(
        df          = transactions_DataFrame_Monzo(),
        reference   = reference,
        name_payer  = name_payer,
        amount      = amount,
        print_table = print_table
    )

def payment_in_transactions_RBS(
    reference            = None,
    #name_payer           = None,
    amount               = None,
    filepath_credentials = "~/.rbs",
    print_table          = False
    ):
    return payment_in_transactions(
        df          = transactions_DataFrame_RBS(filepath_credentials = filepath_credentials),
        reference   = reference,
        amount      = amount,
        print_table = print_table
    )

def payment_in_transactions_Starling(
    reference            = None,
    #name_payer           = None,
    amount               = None,
    filepath_credentials = "~/.starling",
    print_table          = False
    ):
    return payment_in_transactions(
        df          = transactions_DataFrame_Starling(filepath_credentials = filepath_credentials),
        reference   = reference,
        amount      = amount,
        print_table = print_table
    )

def payment_in_transactions_bank(
    reference            = None,
    name_payer           = None,
    amount               = None,
    bank                 = None,
    filepath_credentials = None,
    print_table          = False
    ):
    try:
        if bank == "Monzo":
            return payment_in_transactions_Monzo(
                reference            = reference,
                name_payer           = name_payer,
                amount               = amount,
                print_table          = print_table
            )
        elif bank == "RBS":
            return payment_in_transactions_RBS(
                reference            = reference,
                amount               = amount,
                filepath_credentials = filepath_credentials,
                print_table          = print_table
            )
        elif bank == "Starling":
            return payment_in_transactions_Starling(
                reference            = reference,
                amount               = amount,
                filepath_credentials = filepath_credentials,
                print_table          = print_table
            )
        elif bank == "Santander":
            return payment_in_transactions_Santander(
                reference            = reference,
                amount               = amount
            )
        else:
            log.error("error -- bank not specified in payment in transactions bank")
            return False
    except:
        log.error("error -- payment in transactions bank")
        return False

def table_transactions(
    df = None
    ):
    return pyprel.Table(contents = pyprel.table_DataFrame(df = df))

def names_match(
    name_1 = None,
    name_2 = None
    ):
    """
    Attempt to determine if there is an approximate names match. Return True if
    there is a match and return False if there is no match.
    """
    name_1 = re.sub(" +", " ", name_1).upper()
    name_2 = re.sub(" +", " ", name_2).upper()
    name_1 = " ".join([name_1.split()[0], name_1.split()[-1]]).replace("-", " ").strip()
    name_2 = " ".join([name_2.split()[0], name_2.split()[-1]]).replace("-", " ").strip()
    return SequenceMatcher(None, name_1, name_2).ratio() > 0.3
