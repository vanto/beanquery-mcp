import functools
import textwrap

from pydantic import FilePath
import pytest
from beancount import loader

from server import get_accounts, get_tables, run_query

# test_server.py


@functools.lru_cache(None)
def load():
    entries, errors, options = loader.load_string(
        textwrap.dedent("""
      2022-01-01 open Assets:Checking         USD
      2022-01-01 open Assets:Federal:401k     IRAUSD
      2022-01-01 open Assets:Gold             GLD
      2022-01-01 open Assets:Vacation         VACHR
      2022-01-01 open Assets:Vanguard:RGAGX   RGAGX
      2022-01-01 open Expenses:Commissions    USD
      2022-01-01 open Expenses:Food           USD
      2022-01-01 open Expenses:Home:Rent      USD
      2022-01-01 open Expenses:Taxes:401k     IRAUSD
      2022-01-01 open Expenses:Taxes:Federal  USD
      2022-01-01 open Expenses:Tests          USD
      2022-01-01 open Expenses:Vacation       VACHR
      2022-01-01 open Income:ACME             USD
      2022-01-01 open Income:Gains            USD
      2022-01-01 open Income:Vacation         VACHR

      2022-01-01 * "ACME" "Salary"
        Assets:Checking           10.00 USD
        Income:ACME              -11.00 USD
        Expenses:Taxes:Federal     1.00 USD
        Assets:Federal:401k       -2.00 IRAUSD
        Expenses:Taxes:401k        2.00 IRAUSD
        Assets:Vacation               5 VACHR
        Income:Vacation              -5 VACHR

      2022-01-01 * "Rent"
        Assets:Checking           42.00 USD
        Expenses:Home:Rent        42.00 USD

      2022-01-02 * "Holidays"
        Assets:Vacation              -1 VACHR
        Expenses:Vacation

      2022-01-03 * "Test 01"
        Assets:Checking            1.00 USD
        Expenses:Tests

      2022-01-04 * "My Fovorite Plase" "Eating out alone"
        Assets:Checking            4.00 USD
        Expenses:Food

      2022-01-05 * "Invest"
        Assets:Checking         -359.94 USD
        Assets:Vanguard:RGAGX     2.086 RGAGX {172.55 USD}

      2013-10-23 * "Buy Gold"
        Assets:Checking        -1278.67 USD
        Assets:Gold                   9 GLD {141.08 USD}
        Expenses:Commissions          8.95 USD

      2022-01-07 * "Sell Gold"
        Assets:Gold                 -16 GLD {147.01 USD} @ 135.50 USD
        Assets:Checking         2159.05 USD
        Expenses:Commissions       8.95 USD
        Income:Gains             184.16 USD

      2022-01-08 * "Sell Gold"
        Assets:Gold                 -16 GLD {147.01 USD} @ 135.50 USD
        Assets:Checking         2159.05 USD
        Expenses:Commissions       8.95 USD
        Income:Gains             184.16 USD

      2022-02-01 * "ACME" "Salary"
        Assets:Checking           10.00 USD
        Income:ACME              -11.00 USD
        Expenses:Taxes:Federal     1.00 USD
        Assets:Federal:401k       -2.00 IRAUSD
        Expenses:Taxes:401k        2.00 IRAUSD
        Assets:Vacation               5 VACHR
        Income:Vacation              -5 VACHR

      2022-02-01 * "Rent"
        Assets:Checking           43.00 USD
        Expenses:Home:Rent        43.00 USD

      2022-02-02 * "Test 02"
        Assets:Checking            2.00 USD
        Expenses:Tests

      2030-01-01 query "taxes" "
        SELECT
          date, description, position, balance
        WHERE
          account ~ 'Taxes'
        ORDER BY date DESC
        LIMIT 20"

      2015-01-01 query "home" "
        SELECT
          last(date) as latest,
          account,
          sum(position) as total
        WHERE
          account ~ ':Home:'
        GROUP BY account"

    """)
    )
    return entries, errors, options


@pytest.fixture
def mock_ledger(monkeypatch: pytest.MonkeyPatch):
    """Fixture to mock the _entries global variable."""
    monkeypatch.setattr("server.settings.ledger", FilePath("sample.bean"))


@pytest.fixture
def clear_ledger(monkeypatch: pytest.MonkeyPatch):
    """Fixture to clear the _entries global variable."""
    monkeypatch.setattr("server.settings.ledger", None)


def test_run_query_no_ledger_loaded(clear_ledger: None):
    """Test run_query when no ledger file is loaded."""
    with pytest.raises(Exception) as excinfo:
        run_query("SELECT account WHERE account ~ 'Assets'")
        excinfo.match(
            "No ledger file given or file could not be found. Use set_ledger_file to set a path."
        )


def test_run_query_valid_query(mock_ledger: None):
    """Test run_query with a valid query."""
    query = "SELECT account, sum(position) WHERE account ~ 'Assets' GROUP BY account"
    result = run_query(query)
    assert r"Assets:US:Hooli:Vacation          39     VACHR" in result


def test_get_tables(mock_ledger: None):
    """Test the get_tables resource."""
    result = get_tables()
    assert (
        "accounts\nbalances\ncommodities\ndocuments\nentries\nevents\nnotes\npostings\nprices\ntransactions\n"
        in result
    )  # Ensure the query for tables is executed


def test_get_accounts(mock_ledger: None):
    """Test the get_accounts resource."""
    result = get_accounts()
    assert (
        "Assets:US:BofA:Checking" in result
    )  # Ensure an account from the ledger is present
    assert "Expenses:Food" in result  # Ensure another account is present
