# Advanced Log File Analyzer

A Python script designed to parse and analyze web server log files (e.g., Apache, Nginx common log format). It extracts meaningful statistics, supports processing multiple files, and allows filtering by date/time ranges.

## What is this project?

This tool processes raw log files, which can be voluminous and hard to read, and transforms them into structured data. From this structured data, it generates reports summarizing key metrics such as:
*   Total number of requests.
*   Most frequent IP addresses making requests.
*   Distribution of HTTP status codes (e.g., 200 OK, 404 Not Found, 500 Server Error).
*   Most frequently requested URIs (pages/resources).
The analysis can be narrowed down to specific time windows.

## Where to use?

This script is useful for:
*   **Web Server Monitoring:** Getting a quick overview of server activity.
*   **Troubleshooting:** Identifying problematic IP addresses, frequent errors (like 404s or 500s), or unusual traffic patterns.
*   **Security Analysis:** Spotting potential denial-of-service attempts (many requests from one IP) or scanning activities.
*   **Performance Insights:** Understanding which pages are most popular or which might be causing errors.
*   **Learning:** Demonstrates file I/O, regular expressions, data parsing, data aggregation (`collections.Counter`), command-line argument parsing (`argparse`), and datetime manipulation in Python.

## Features

*   Parses log entries based on a common web server log format.
*   Accepts one or more log files as input via command-line arguments.
*   Calculates and reports:
    *   Total number of requests.
    *   Top N IP addresses by request volume.
    *   Counts for each HTTP status code.
    *   Top N requested URIs.
*   Allows users to specify the "Top N" count for IPs and URIs.
*   Supports filtering log entries by a start date/time and/or an end date/time.
*   Handles timezone differences by normalizing log timestamps to naive UTC for comparison with filter arguments.
*   Provides a summary of parsing success and failures.

## Requirements

*   Python 3.7+ (due to `datetime.timezone.utc` and f-string usage, though adaptable to earlier Python 3 versions with minor changes).
*   No external non-standard libraries are required.

## Setup

1.  Save the script as `analyzer.py`.
2.  Ensure you have log files in a format similar to the common Apache/Nginx log format. A typical line looks like:
    `IP_ADDRESS - USERNAME [TIMESTAMP] "HTTP_METHOD REQUEST_URI HTTP_VERSION" STATUS_CODE BYTES_SENT "REFERER" "USER_AGENT"`
    Example:
    `192.168.1.100 - john [10/Oct/2023:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 1543 "-" "-"`

## How to Use

Open your terminal or command prompt, navigate to the directory containing `analyzer.py`, and use the following command structure:

```bash
python analyzer.py <LOG_FILE_PATH_1> [<LOG_FILE_PATH_2> ...] [OPTIONS]

Positional Arguments:

LOG_FILE_PATH: (Required) Path to one or more log files to analyze. Separate multiple files with spaces.

Optional Arguments:

-h, --help: Show the help message and exit.
-n N, --top N: Number of top results to show for IPs and URIs (default: 5).

--start-date YYYY-MM-DD[THH:MM:SS]: Filter logs FROM this date/time. Entries before this time will be excluded. (e.g., --start-date 2023-10-10 or --start-date 2023-10-10T14:00:00). Inclusive.
--end-date YYYY-MM-DD[THH:MM:SS]: Filter logs UP TO this date/time. Entries after this time will be excluded. (e.g., --end-date 2023-10-10 or --end-date 2023-10-10T18:00:00). Inclusive.

Examples:

Analyze a single log file with default settings:
python analyzer.py /var/log/apache2/access.log

Analyze multiple log files and show top 10 results:
python analyzer.py access.log.1 access.log.2.gz -n 10


(Note: This script does not currently handle .gz compressed files directly. You would need to decompress them first or add decompression logic.)

Analyze logs for a specific date:

python analyzer.py sample.log --start-date 2023-10-10 --end-date 2023-10-10T23:59:59
(To include the entire day of 2023-10-10, ensure the end time covers the end of the day.)

Analyze logs from a specific time onwards:
python analyzer.py server.log --start-date 2023-10-10T15:30:00

How It Works Internally

Argument Parsing: Uses argparse to process command-line arguments (log file paths, top N, date filters).
Date Filter Parsing: Converts user-provided date strings into naive Python datetime objects.
File Iteration: Reads each specified log file line by line.

Log Line Parsing:

Uses a pre-compiled regular expression (LOG_PATTERN) to match and extract fields from each log line.
Converts the log entry's timestamp string (which includes timezone info) into a naive UTC datetime object for consistent comparison.
Date Filtering: If date filters are active, it checks if the log entry's timestamp falls within the specified range. Entries outside the range are skipped.
Data Aggregation: Stores all valid and filtered parsed log entries (as dictionaries) in a list.
Statistics Calculation: Uses collections.Counter to efficiently count occurrences of IP addresses, status codes, and URIs from the aggregated data.
Report Generation: Prints a formatted summary of the analysis to the console.

Future Improvements (TODO)

Support for compressed log files (e.g., .gz).
More sophisticated end-date handling to easily include an entire day.
Output reports to files (e.g., TXT, CSV, JSON).
More advanced error analysis (e.g., top URIs per error code).
Configuration file for custom log patterns or report formats.
Performance optimizations for extremely large files (streaming analysis).

---
