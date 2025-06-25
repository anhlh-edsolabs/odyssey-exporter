# Aptos NFT Exporter

This script fetches all NFT token data for a given collection from the Aptos mainnet and exports it to a JSON or CSV file.

## Getting Started

### Prerequisites

- Python 3.x

### Setup

1. **Create a virtual environment:**

    On macOS and Linux:

    ```bash
    python3 -m venv venv
    ```

    On Windows:

    ```bash
    python -m venv venv
    ```

2. **Activate the virtual environment:**

    On macOS and Linux:

    ```bash
    source venv/bin/activate
    ```

    On Windows:

    ```bash
    .\\venv\\Scripts\\activate
    ```

3. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

You can run the Python script directly or use the provided `run.sh` CLI script.

### Using the CLI script (Recommended)

Before first use, make the script executable:

```bash
chmod +x run.sh
```

Then, you can run the script like this:

```bash
./run.sh <COLLECTION_ID> [OPTIONS]
```

The CLI script handles activating the virtual environment automatically.

### Examples using the CLI

**Export to JSON (default):**

```bash
./run.sh 0xb6ec8db6f21f7f39172ee28d8a751a7f1b51f7b8bc864b06ce4010d52ab0ffa8
```

This will create `tokens.json`.

**Export to a specific CSV file:**

```bash
./run.sh 0xb6ec8db6f21f7f39172ee28d8a751a7f1b51f7b8bc864b06ce4010d52ab0ffa8 -o my_collection -f csv
```

This will create `my_collection.csv`.

### Using the Python script directly

Once the setup is complete, you can run the script with the following command:

```bash
python main.py <COLLECTION_ID> [OPTIONS]
```

### Arguments

- `COLLECTION_ID`: (Required) The collection ID (Object address) of the NFT collection you want to export.

### Options

- `-o, --output <FILENAME>`: (Optional) The name of the output file, without the file extension. Defaults to `tokens`.
- `-f, --format <FORMAT>`: (Optional) The format of the output file. Choose between `json` or `csv`. Defaults to `json`.

### Examples

**Export to JSON (default):**

```bash
python main.py 0xb6ec8db6f21f7f39172ee28d8a751a7f1b51f7b8bc864b06ce4010d52ab0ffa8
```

This will create `tokens.json`.

**Export to a specific JSON file:**

```bash
python main.py 0xb6ec8db6f21f7f39172ee28d8a751a7f1b51f7b8bc864b06ce4010d52ab0ffa8 -o my_collection
```

This will create `my_collection.json`.

**Export to a CSV file:**

```bash
python main.py 0xb6ec8db6f21f7f39172ee28d8a751a7f1b51f7b8bc864b06ce4010d52ab0ffa8 -f csv
```

This will create `tokens.csv`.

**Export to a specific CSV file:**

```bash
python main.py 0xb6ec8db6f21f7f39172ee28d8a751a7f1b51f7b8bc864b06ce4010d52ab0ffa8 -o my_collection -f csv
```

This will create `my_collection.csv`.
