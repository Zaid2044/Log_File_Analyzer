import re
from collections import Counter
import argparse
import traceback
from datetime import datetime, timezone

LOG_PATTERN_STR = r'''
    ^
    (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) 
    \s+-\s+ 
    ([\w.-]+|\S+) 
    \s+
    \[([^\]]+)\] 
    \s+
    "
    (GET|POST|PUT|DELETE|HEAD|OPTIONS) 
    \s+
    ([^"\s]+) 
    \s+
    (HTTP/\d\.\d) 
    "
    \s+
    (\d{3}) 
    \s+
    ([-\d]+) 
    \s+
    "([^"]*)" 
    \s+
    "([^"]*)" 
    $
'''
LOG_PATTERN = re.compile(LOG_PATTERN_STR, re.VERBOSE)

def parse_datetime_argument(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S') 
    except ValueError:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            print(f"Warning: Invalid date format for '{date_str}'. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS.")
            return None

def parse_log_line(line):
    match = LOG_PATTERN.match(line)
    if match:
        raw_timestamp_str = match.group(3)
        parsed_timestamp_obj = None 
        try:
            aware_dt = datetime.strptime(raw_timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
            parsed_timestamp_obj = aware_dt.astimezone(timezone.utc).replace(tzinfo=None)
        except ValueError as e:
            print(f"Warning: Could not parse log timestamp '{raw_timestamp_str}': {e}")

        return {
            "ip_address": match.group(1),
            "username": match.group(2),
            "timestamp_str": raw_timestamp_str,
            "timestamp_obj": parsed_timestamp_obj,
            "method": match.group(4),
            "uri": match.group(5),
            "http_version": match.group(6),
            "status_code": match.group(7),
            "bytes_sent": match.group(8),
            "referer": match.group(9),
            "user_agent": match.group(10),
        }
    return None

def analyze_log_files(log_file_paths, top_n=5, start_filter_dt=None, end_filter_dt=None):
    all_parsed_data = []
    total_processed_lines = 0
    total_unparsed_lines = 0 
    total_filtered_out_by_date = 0

    for log_file_path in log_file_paths:
        parsed_in_current_file = 0
        unparsed_in_current_file = 0
        filtered_out_in_current_file = 0
        try:
            with open(log_file_path, 'r') as f:
                print(f"\n--- Analyzing log file: {log_file_path} ---")
                for line_number, line in enumerate(f, 1):
                    total_processed_lines +=1
                    line = line.strip()
                    if not line:
                        continue

                    parsed_data = parse_log_line(line)
                    if parsed_data:
                        log_entry_dt = parsed_data.get("timestamp_obj")
                        if log_entry_dt: 
                            if start_filter_dt and log_entry_dt < start_filter_dt:
                                filtered_out_in_current_file += 1
                                continue 
                            if end_filter_dt:
                                if log_entry_dt > end_filter_dt:
                                    filtered_out_in_current_file += 1
                                    continue
                            
                            parsed_in_current_file += 1
                            all_parsed_data.append(parsed_data)
                        else:
                            unparsed_in_current_file += 1
                    else: 
                        unparsed_in_current_file += 1
            
            print(f"Finished {log_file_path}: Parsed&Kept {parsed_in_current_file}, FilteredOutByDate {filtered_out_in_current_file}, Unparsable/NoTimestamp {unparsed_in_current_file}")
            total_unparsed_lines += unparsed_in_current_file
            total_filtered_out_by_date += filtered_out_in_current_file

        except FileNotFoundError:
            print(f"Error: Log file not found at '{log_file_path}'")
            continue 
        except Exception as e:
            print(f"An unexpected error occurred with {log_file_path}: {e}")
            traceback.print_exc()
    
    print(f"\n--- Overall Summary ---")
    print(f"Total lines processed from all files: {total_processed_lines}")
    print(f"Total lines successfully parsed and kept for analysis: {len(all_parsed_data)}")
    if total_filtered_out_by_date > 0:
        print(f"Total lines filtered out by date range: {total_filtered_out_by_date}")
    if total_unparsed_lines > 0:
        print(f"Total lines failed to parse or had missing timestamps: {total_unparsed_lines}")

    if not all_parsed_data:
        print("\nNo data available for analysis after parsing and filtering.")
        return

    print("\n--- Combined Log Analysis Report (Filtered) ---")

    total_requests = len(all_parsed_data)
    print(f"Total Requests in selected range: {total_requests}")

    ip_addresses = [entry['ip_address'] for entry in all_parsed_data]
    ip_counts = Counter(ip_addresses)
    print(f"\nTop {top_n} IP Addresses:")
    for ip, count in ip_counts.most_common(top_n):
        print(f"  {ip}: {count} requests")

    status_codes = [entry['status_code'] for entry in all_parsed_data]
    status_code_counts = Counter(status_codes)
    print("\nRequests by Status Code:")
    for code, count in status_code_counts.most_common():
        print(f"  Status {code}: {count} requests")

    requested_uris = [entry['uri'] for entry in all_parsed_data]
    uri_counts = Counter(requested_uris)
    print(f"\nTop {top_n} Requested URIs:")
    for uri, count in uri_counts.most_common(top_n):
        print(f"  {uri}: {count} requests")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze web server log files with date filtering.")
    parser.add_argument("log_files",
                        metavar="LOG_FILE",
                        type=str,
                        nargs='+',
                        help="Path to one or more log files to analyze.")
    parser.add_argument("-n", "--top",
                        type=int,
                        default=5,
                        help="Number of top results to show for IPs and URIs (default: 5).")
    parser.add_argument("--start-date",
                        type=str,
                        help="Filter logs FROM this date/time (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS). Inclusive.")
    parser.add_argument("--end-date",
                        type=str,
                        help="Filter logs UP TO this date/time (YYYY-MM-DD or YYYY-MM-DDTHH:M M:SS). Inclusive.")
    
    args = parser.parse_args()

    start_filter = parse_datetime_argument(args.start_date)
    end_filter = parse_datetime_argument(args.end_date)

    analyze_log_files(args.log_files, args.top, start_filter, end_filter)