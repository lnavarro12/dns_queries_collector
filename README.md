

# DNS Query Collector

This script processes a BIND server log file containing DNS queries and sends them to the Lumu API for further analysis. It includes functions for formatting queries, handling API requests, and generating analytics on the processed data.

## Table of Contents

	Installation
	Usage
	Functions
	Error Handling
	Requirements
	License

## Installation

To run this script, ensure you have Docker installed. You may also need to install the required packages, which can be done using the docker-compose:

```bash
docker compose up
```
This will install all the libreries that are in the requirements.txt

Usage

	1.	Prepare Your Environment: Make sure you have the utils module and constants file as they are required for the script to function properly.

	2.	Run the docker-compose: Use this command to build and start the container.

	3.	View the Output: The script will process the queries and output analytics regarding the DNS queries processed, including the count and percentage of unique clients.


## Functions

- parse_arguments(): Parses command line arguments for the path to the BIND server log file.

- formatting_queries(query: str) -> dict: Formats a single DNS query and extracts relevant information, returning it as a dictionary.

- process_queries(queries: str): Processes the BIND server log file, formatting each line into a structured query and sending batches to the Lumu API.

- chunk_queries(queries: list): Divides the processed queries into chunks for sending to the Lumu API.

- send_queries(queries: list): Sends the DNS queries to the Lumu API and handles the response.

- analitics_overview(queries: list): Analyzes the DNS queries, providing statistics on unique client IPs and names.

- main(): The main entry point of the script. It orchestrates the parsing, processing, and analysis of DNS queries.

## Error Handling

The script handles several potential errors:

	•	FileNotFoundError: If the specified log file does not exist.
	•	UnicodeDecodeError: If there are issues decoding a line in the log file.
	•	General Exceptions: When sending queries to the Lumu API, any exceptions will be logged with an error message.

Requirements

	•	Python 3.x
	•	pandas library