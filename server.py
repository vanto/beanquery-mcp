# server.py
import io
import os
from typing import Optional

from beanquery import shell
from mcp.server.fastmcp import FastMCP
from pydantic import Field, FilePath
from pydantic_settings import BaseSettings, SettingsConfigDict
from mcp.server.fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)


class BeanQuerySettings(BaseSettings):
    """Settings for the BeanQuery MCP server."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="BEANCOUNT_", env_file=".env"
    )

    ledger: Optional[FilePath] = Field(
        None, json_schema_extra={"env": "BEANCOUNT_LEDGER"}
    )


# Create an MCP server
mcp = FastMCP("Beanquery MCP", dependencies=["beancount", "beanquery"])
settings = BeanQuerySettings()

logger.info(f"Using ledger file: {settings.ledger}")


# Tools for working with Beanquery
@mcp.tool()
def set_ledger_file(filename: str) -> str:
    """Set the Beancount ledger file to use for queries."""
    # Check if file exists
    if not os.path.exists(filename):
        logger.warning(f"Warning: File {filename} not found.")
        raise FileNotFoundError(f"File {filename} not found.")

    settings.ledger = FilePath(filename)
    logger.info(f"Using ledger file: {filename}.")
    return f"Will use ledger file: {filename}."


@mcp.tool()
def run_query(
    query: str = Field(
        description="The query in Bean Query Language (BQL) in the same way as it can be passed to the beanquery cli"
    ),
) -> str:
    """Run a BQL query against the loaded Beancount file.
    The result will be returned as a string of bean-query's tabular text output."""

    output = io.StringIO()
    if not settings.ledger:
        raise Exception(
            "No ledger file given or file could not be found. Use set_ledger_file to set a path."
        )

    bqshell = shell.BQLShell(
        "beancount:" + settings.ledger.absolute().as_posix(),
        outfile=output,
        format="text",
    )

    logger.debug(f"Running query: {query}.")
    bqshell.onecmd(".set expand true")
    bqshell.onecmd(query)

    result = output.getvalue()
    output.close()

    return result


# Resources for working with Beanquery
@mcp.resource("beanquery://tables")
def get_tables() -> str:
    """Get a list of tables that BQL can access."""
    return run_query(".tables")


@mcp.resource("beanquery://accounts")
def get_accounts() -> str:
    """Get a list of accounts in the loaded Beancount file."""
    return run_query("SELECT DISTINCT account ORDER BY account")
