# Beanquery MCP

The Beancount MCP Server is an experimental implementation of the [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol) designed to interface with [Beancount](https://beancount.github.io/) ledger files. Leveraging the [Beancount Query Language (BQL)](https://beancount.github.io/docs/beancount_query_language.html) and the [beanquery](https://github.com/beancount/beanquery) tool, this server enables seamless querying and analysis of financial data stored in Beancount format. By integrating MCP, the server facilitates standardized communication between AI assistants and Beancount ledgers, enhancing the accessibility and utility of financial data.

Note: This server is experimental and may undergo significant changes. It is recommended to use it in a development environment and provide feedback for further improvements.

A generated sample ledger can be found in [sample.bean](sample.bean)

### Available Resources and Tools

- **Tools**:
  - `set_ledger_file`: Set the Beancount ledger file to use for queries (if not set via environment variable).
  - `run_query`: Run a BQL query against the loaded Beancount file.
- **Resources**:
  - `beanquery://tables`: Get a list of tables that BQL can access.
  - `beanquery://accounts`: Get a list of accounts in the loaded Beancount file.

## Setup

### Prerequisites

- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/) for managing Python projects (recommended)

## Usage

### Running the Server

1. **Development Mode**:
   Use the MCP Inspector to test and debug your server:
   ```bash
   mcp dev server.py
   ```

2. **Claude Desktop Integration**:
   Install the server into Claude Desktop:
   ```bash
   mcp install server.py
   ```

   - **Custom Name**:
     ```bash
     mcp install server.py --name "Beanquery MCP Server"
     ```

   - **Environment Variables**:
     ```bash
     mcp install server.py -v BEANCOUNT_LEDGER=/path/to/your/ledger.bean
     mcp install server.py -f .env
     ```

## Testing

Run the test suite using `pytest`:
```bash
pytest server_test.py
```

## Contributing

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature description"
   ```
4. Push to your branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.