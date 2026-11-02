#!/usr/bin/env python3
"""CodeReady: single-file offline generator for the CE301 question bank.
Run this file with Python. It writes solution.py and the required CSV beside itself.
Only the Python standard library is used.
"""

import ast
import base64
import csv
import gzip
import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
_CURRENT_CSV_COLUMNS = []
_CURRENT_DEMO_ROWS = []

# Compact metadata for all 340 question slips. This allows a question number alone
# to resolve to the right topic, dataset, columns and sample row.
QUESTION_BANK_PAYLOAD = """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"""
QUESTION_BANK = json.loads(gzip.decompress(base64.b64decode(QUESTION_BANK_PAYLOAD)).decode("utf-8"))

DEFAULT_COLUMNS = {
    "rmi_rpc": ["call_id", "client_name", "method_name", "param_value", "timestamp"],
    "multithreading": ["task_id", "thread_name", "burst_ms", "priority", "status"],
    "lamport": ["event_id", "process_id", "event_type", "message_to", "initial_clock"],
    "cristian": ["client_id", "t0_send_ms", "t_server_ms", "t1_recv_ms"],
    "berkeley": ["node_id", "clock_time_sec", "is_faulty"],
    "vector": ["event_id", "process_id", "event_action", "target_process"],
    "ring": ["node_id", "next_node_id", "is_active", "priority_rank"],
    "bully": ["node_id", "is_alive", "is_current_coordinator"],
    "load_balancing": ["job_id", "compute_units", "assigned_worker", "status"],
    "matrix": ["row_id", "col_0", "col_1", "col_2", "col_3"],
}

# The columns each generated program cannot run without.
REQUIRED_COLUMNS = {
    "rmi_rpc": ["call_id", "client_name", "method_name", "param_value"],
    "multithreading": ["task_id", "thread_name", "burst_ms"],
    "lamport": ["event_id", "process_id", "event_type", "message_to"],
    "cristian": ["client_id", "t0_send_ms", "t_server_ms", "t1_recv_ms"],
    "berkeley": ["node_id", "clock_time_sec", "is_faulty"],
    "vector": ["event_id", "process_id", "event_action", "target_process"],
    "ring": ["node_id", "next_node_id", "is_active"],
    "bully": ["node_id", "is_alive"],
    "load_balancing": ["job_id", "compute_units"],
    "matrix": [],
}

# Other names a question may use for the same column.
COLUMN_SYNONYMS = {
    "call_id": ("request_id", "req_id", "rpc_id", "id"),
    "client_name": ("client", "client_id", "caller"),
    "method_name": ("method", "function", "function_name", "procedure", "operation"),
    "param_value": ("param", "params", "parameter", "argument", "arg", "args", "value"),
    "timestamp": ("time", "sent_at", "ts"),
    "task_id": ("job_id", "id"),
    "thread_name": ("thread", "thread_id", "worker", "worker_name"),
    "burst_ms": ("burst", "burst_time", "duration_ms", "duration", "exec_ms", "time_ms"),
    "event_id": ("event", "id"),
    "process_id": ("process", "proc", "pid", "node_id", "node"),
    "event_type": ("event_action", "type", "action"),
    "event_action": ("event_type", "type", "action"),
    "message_to": ("target_process", "target", "to", "receiver", "destination", "dest"),
    "target_process": ("message_to", "target", "to", "receiver", "destination", "dest"),
    "initial_clock": ("start_clock", "clock", "clock_value"),
    "client_id": ("client_name", "client", "id"),
    "t0_send_ms": ("t0", "t0_ms", "t_send", "t_send_ms", "send_time"),
    "t_server_ms": ("t_server", "server_time", "server_time_ms", "tserver"),
    "t1_recv_ms": ("t1", "t1_ms", "t_recv", "t_recv_ms", "recv_time", "receive_time"),
    "node_id": ("process_id", "process", "pid", "node", "id"),
    "clock_time_sec": ("clock_time", "clock_sec", "time_sec", "clock", "time"),
    "is_faulty": ("faulty", "fault", "is_outlier", "outlier"),
    "next_node_id": ("next_id", "next_node", "next"),
    "is_active": ("active", "is_alive", "alive"),
    "priority_rank": ("priority", "rank"),
    "is_alive": ("alive", "is_active", "active"),
    "is_current_coordinator": ("is_coordinator", "current_coordinator", "coordinator",
                               "is_leader", "leader"),
    "job_id": ("task_id", "id"),
    "compute_units": ("units", "job_size", "size", "cost", "load", "weight"),
    "assigned_worker": ("worker", "assigned_to"),
    "row_id": ("row", "id"),
}

# Recognition is scoped to the ten recurring topics, but it matches key words
# rather than whole phrases so that reworded questions are still understood.
TOPIC_PATTERNS = {
    "cristian": r"\bcristian",
    "berkeley": r"\bberkeley",
    "lamport": r"\blamport|\bscalar (timestamp|clock)|\btotal causal order",
    "vector": r"\bvector (clock|time)",
    "bully": r"\bbull(y|ies)\b",
    "ring": r"\bring (algorithm|election|leader|based|of nodes|token)"
            r"|\b(elect|leader|token)\w*\b.*\bring\b|\bring\b.*\b(elect|leader|token)",
    "load_balancing": r"\bload balanc|\bround robin|\bleast connection|\bworkload scheduling",
    "matrix": r"\bmpi\b|\bmatri(x|ces)\b|\bscatter gather\b",
    "rmi_rpc": r"\brpc\b|\brmi\b|\bremote (procedure|method|invocation|call)",
}

# Thread words also appear inside matrix questions, so this topic is only used
# when no other topic matched.
THREAD_PATTERN = r"\bmulti ?thread|\bmutex\b|\bthreads?\b|\bconcurrent processing|\brace condition"

ALGORITHM_LABELS = {
    "rmi_rpc": "RMI / RPC",
    "multithreading": "Multithreading",
    "lamport": "Lamport's Logical Clocks",
    "cristian": "Cristian's Algorithm",
    "berkeley": "Berkeley's Algorithm",
    "vector": "Vector Clocks",
    "ring": "Ring Leader Election",
    "bully": "Bully Leader Election",
    "load_balancing": "Dynamic Load Balancing",
    "matrix": "MPI Matrix Multiplication",
}


def _rows(columns, *values):
    return [dict(zip(columns, row)) for row in values]


# Demonstration data chosen so that each program has something to show:
# a real outlier, concurrent events, a dead node, uneven jobs and so on.
DEMO_ROWS = {
    "rmi_rpc": _rows(
        DEFAULT_COLUMNS["rmi_rpc"],
        ("101", "Client_A", "processData", "450", "10:00:01"),
        ("102", "Client_B", "add", "12;30", "10:00:02"),
        ("103", "Client_C", "multiply", "6;7", "10:00:03"),
        ("104", "Client_D", "square", "9", "10:00:04"),
        ("105", "Client_E", "uppercase", "hello", "10:00:05"),
    ),
    "multithreading": _rows(
        DEFAULT_COLUMNS["multithreading"],
        ("T1", "Worker_1", "200", "HIGH", "PENDING"),
        ("T2", "Worker_2", "150", "MEDIUM", "PENDING"),
        ("T3", "Worker_3", "100", "LOW", "PENDING"),
        ("T4", "Worker_1", "120", "HIGH", "PENDING"),
        ("T5", "Worker_2", "80", "LOW", "PENDING"),
    ),
    "lamport": _rows(
        DEFAULT_COLUMNS["lamport"],
        ("E1", "P1", "SEND", "P2", "0"),
        ("E2", "P2", "RECEIVE", "P1", "0"),
        ("E3", "P2", "SEND", "P3", "0"),
        ("E4", "P3", "RECEIVE", "P2", "0"),
        ("E5", "P1", "LOCAL", "", "0"),
        ("E6", "P3", "LOCAL", "", "0"),
    ),
    "cristian": _rows(
        DEFAULT_COLUMNS["cristian"],
        ("C1", "1000", "1050", "1100"),
        ("C2", "2000", "2090", "2100"),
        ("C3", "3000", "2950", "3080"),
        ("C4", "4000", "4045", "4060"),
        ("C5", "5000", "5100", "5120"),
    ),
    "berkeley": _rows(
        DEFAULT_COLUMNS["berkeley"],
        ("N1", "3600", "FALSE"),
        ("N2", "3605", "FALSE"),
        ("N3", "3595", "FALSE"),
        ("N4", "3610", "FALSE"),
        ("N5", "4000", "TRUE"),
    ),
    "vector": _rows(
        DEFAULT_COLUMNS["vector"],
        ("E1", "P1", "SEND", "P2"),
        ("E2", "P2", "RECEIVE", "P1"),
        ("E3", "P2", "SEND", "P3"),
        ("E4", "P3", "RECEIVE", "P2"),
        ("E5", "P1", "LOCAL", ""),
        ("E6", "P3", "LOCAL", ""),
    ),
    "ring": _rows(
        DEFAULT_COLUMNS["ring"],
        ("1", "2", "TRUE", "85"),
        ("2", "3", "TRUE", "72"),
        ("3", "4", "TRUE", "91"),
        ("4", "5", "TRUE", "68"),
        ("5", "1", "FALSE", "80"),
    ),
    "bully": _rows(
        DEFAULT_COLUMNS["bully"],
        ("1", "TRUE", "FALSE"),
        ("2", "TRUE", "FALSE"),
        ("3", "TRUE", "FALSE"),
        ("4", "FALSE", "FALSE"),
        ("5", "TRUE", "TRUE"),
    ),
    "load_balancing": _rows(
        DEFAULT_COLUMNS["load_balancing"],
        ("J101", "35", "UNASSIGNED", "PENDING"),
        ("J102", "20", "UNASSIGNED", "PENDING"),
        ("J103", "50", "UNASSIGNED", "PENDING"),
        ("J104", "10", "UNASSIGNED", "PENDING"),
        ("J105", "25", "UNASSIGNED", "PENDING"),
        ("J106", "40", "UNASSIGNED", "PENDING"),
    ),
    "matrix": _rows(["row_id"], ("R0",), ("R1",), ("R2",), ("R3",)),
}

DEMO_MATRIX = [[2, 4, 1, 5], [3, 1, 6, 2], [7, 2, 3, 4], [1, 5, 2, 6]]

# These columns count upward from whatever the question's sample row starts at.
SEQUENTIAL_COLUMNS = {"call_id", "task_id", "job_id", "event_id", "client_id", "node_id", "row_id"}


def normalize_topic(value):
    value = value.lower().replace("’", "'")
    value = re.sub(r"['’]s\b", "s", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def matching_topics(text):
    normalized = normalize_topic(text)
    matches = [key for key, pattern in TOPIC_PATTERNS.items() if re.search(pattern, normalized)]
    if not matches and re.search(THREAD_PATTERN, normalized):
        matches = ["multithreading"]
    return matches


def clean_filename(name):
    name = Path(name.strip()).name
    if not name.lower().endswith(".csv"):
        name += ".csv"
    if not re.fullmatch(r"[A-Za-z0-9_.-]+\.csv", name):
        raise ValueError("The CSV filename contains unsupported characters.")
    return name


def extract_topic_text(statement):
    match = re.search(
        r"\bTOPIC\s*:\s*(.*?)(?=Project\s+Domain\s*:|Experiment\s+Aim|[\r\n]|$)",
        statement, re.I,
    )
    return collapse_text(match.group(1)) if match else ""


def remove_project_domain(statement):
    # A domain such as 'Adaptive Load Balancing ...' must not be read as the topic.
    text = statement.replace("’", "'").replace("‘", "'")
    text = re.sub(r"Project\s+Domain\s*:.*?(?=Experiment\s+Aim|\n|$)", " ", text, flags=re.I | re.S)
    return re.sub(r"(?:application\s+)?domain\s+'[^']*'", " ", text, flags=re.I)


def detect_algorithm(statement):
    # An explicit TOPIC line is the strongest signal when the full chit is pasted.
    topic_text = extract_topic_text(statement)
    if topic_text:
        matches = matching_topics(topic_text)
        if len(matches) == 1:
            return matches[0], ALGORITHM_LABELS[matches[0]]

    # If only Q number or a partial chit is supplied, use the embedded question bank.
    question_number = extract_question_number(statement)
    if question_number in QUESTION_BANK:
        algorithm = QUESTION_BANK[question_number]["a"]
        return algorithm, ALGORITHM_LABELS[algorithm]

    matches = matching_topics(remove_project_domain(statement))
    if not matches:
        raise ValueError(
            "I could not identify one of the ten CE301 bank topics. "
            "Paste a question number, the topic line, or the problem statement."
        )
    if len(matches) > 1:
        choices = ", ".join(ALGORITHM_LABELS[key] for key in matches)
        raise ValueError(f"More than one bank topic matched ({choices}). Paste the TOPIC line to disambiguate.")
    return matches[0], ALGORITHM_LABELS[matches[0]]


def extract_question_number(statement):
    match = re.search(r"\b(?:Q|QUESTION|CHIT|SLIP)\s*#?\s*(\d{1,3})\b", statement, re.I)
    if match:
        return match.group(1)
    if re.fullmatch(r"\s*#?\s*\d{1,3}\s*", statement):
        return str(int(statement.strip().lstrip("# ")))
    return None


def collapse_text(value):
    return re.sub(r"\s+", " ", value).strip(" \t\r\n|;")


def extract_project_domain(statement):
    match = re.search(r"Project\s+Domain\s*:\s*(.*?)(?=Experiment\s+Aim|\Z)", statement, re.I | re.S)
    if not match:
        return ""
    value = match.group(1)
    if not re.search(r"Experiment\s+Aim", statement, re.I):
        value = value.splitlines()[0] if value.strip() else ""
    return collapse_text(value)


def extract_experiment_aim(statement):
    match = re.search(
        r"Experiment\s+Aim(?:\s*\([^)]*\))?\s*:\s*(.*?)(?=Required\s+Local\s+CSV\s+Dataset\s*:|$)",
        statement, re.I | re.S,
    )
    return collapse_text(match.group(1)) if match else ""


def extract_expected_output(statement):
    match = re.search(r"Expected\s+Output\s*/\s*Verification\s*:\s*(.*)", statement, re.I | re.S)
    if not match:
        return "", ""
    tail = re.split(r"(?=\bSLIP\s*/\s*CHIT\s+Q\s*\d+\b)", match.group(1), maxsplit=1, flags=re.I)[0]
    instruction_match = re.search(
        r"Ensure\s+the\s+program\s+executes\s+directly\s+within\s+the\s+VS\s+Code\s+terminal[^.]*\.?",
        tail, re.I,
    )
    instruction = collapse_text(instruction_match.group(0)) if instruction_match else ""
    if instruction_match:
        tail = tail[:instruction_match.start()] + tail[instruction_match.end():]
    return collapse_text(tail), instruction


def extract_question_details(statement):
    expected, instruction = extract_expected_output(statement)
    question_number = extract_question_number(statement) or ""
    bank_entry = QUESTION_BANK.get(question_number, {})
    return {
        "question_number": question_number,
        "topic_text": extract_topic_text(statement) or bank_entry.get("t", ""),
        "project_domain": extract_project_domain(statement) or bank_entry.get("d", ""),
        "experiment_aim": extract_experiment_aim(statement) or bank_entry.get("m", ""),
        "expected_output": expected or bank_entry.get("e", ""),
        "execution_instruction": instruction or "Ensure the program executes directly within the VS Code terminal.",
    }


def extract_columns(statement, algorithm, question_number=None):
    match = re.search(r"columns?\b[^\[\]\r\n]{0,20}\[([^\]]+)\]", statement, re.I | re.S)
    if not match:
        # Also accept: columns: a, b, c  /  columns are a, b, c  /  with columns a, b, c
        match = re.search(
            r"columns?\s*(?:are|=|:)?\s*([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)+)", statement, re.I,
        )
    if match:
        fields = [item.strip().strip("'\"`") for item in match.group(1).split(",")]
        fields = [item for item in fields if item]
        if fields:
            return fields
    bank_entry = QUESTION_BANK.get(str(question_number), {}) if question_number else {}
    if bank_entry.get("a") == algorithm:
        return bank_entry["c"][:]
    return DEFAULT_COLUMNS[algorithm][:]


def map_columns(columns, algorithm):
    """Match each column the program reads to the column name used in this question."""
    if algorithm == "matrix":
        if len(columns) < 2:
            raise ValueError("Matrix multiplication needs one row-label column and at least one numeric column.")
        lowered = {column.lower(): column for column in columns}
        for name in ("row_id",) + COLUMN_SYNONYMS["row_id"]:
            if name in lowered:
                return {"row_id": lowered[name]}, False
        # If the question gives a different name for the row label, use its first column.
        return {"row_id": columns[0]}, True

    canonical = DEFAULT_COLUMNS[algorithm]
    mapping = {}
    unused = list(columns)
    for name in canonical:
        for option in (name,) + COLUMN_SYNONYMS.get(name, ()):
            found = next((column for column in unused if column.lower() == option), None)
            if found:
                mapping[name] = found
                unused.remove(found)
                break

    assumed = False
    missing = [name for name in REQUIRED_COLUMNS[algorithm] if name not in mapping]
    if missing and len(columns) == len(canonical):
        # Same number of columns as the bank: fall back to matching them in order.
        for name, column in zip(canonical, columns):
            if name not in mapping and column in unused:
                mapping[name] = column
                unused.remove(column)
                assumed = True
        missing = [name for name in REQUIRED_COLUMNS[algorithm] if name not in mapping]
    if missing and len(missing) == len(unused):
        # Only unknown names are left and they fill the gaps exactly.
        mapping.update(zip(missing, unused))
        assumed = True
        missing = []
    if missing:
        raise ValueError(
            "These columns are needed but could not be found in the question: "
            + ", ".join(missing) + ".\nColumns found: " + ", ".join(columns)
        )
    return mapping, assumed


def extract_csv_name(statement, algorithm, question_number):
    match = re.search(r"([A-Za-z0-9_.-]+\.csv)\b", statement, re.I)
    if match:
        return clean_filename(match.group(1))
    bank_entry = QUESTION_BANK.get(str(question_number), {}) if question_number else {}
    if bank_entry.get("a") == algorithm:
        return bank_entry["f"]
    suffix = f"_{question_number}" if question_number else ""
    return f"{algorithm}{suffix}.csv"


def parse_sample(raw, columns):
    raw = collapse_text(raw)
    try:
        row = next(csv.reader([raw], skipinitialspace=True))
    except (csv.Error, StopIteration):
        return None
    row = [value.strip().strip("'\"`") for value in row]
    return row if len(row) == len(columns) else None


def extract_sample_row(statement, columns, question_number=None, algorithm=None):
    # The row may be wrapped onto a second line, or the whole chit may be one line.
    match = re.search(r"Sample\s*Row\s*:\s*(.*?)(?=Expected\s+Output|\Z)", statement, re.I | re.S)
    if match:
        parsed = parse_sample(match.group(1), columns) or parse_sample(match.group(1).splitlines()[0], columns)
        if parsed:
            return parsed
    bank_entry = QUESTION_BANK.get(str(question_number), {}) if question_number else {}
    if bank_entry.get("a") == algorithm and bank_entry.get("c") == columns:
        return bank_entry.get("s", [])[:]
    return None


def continue_sequence(value, offset):
    match = re.fullmatch(r"(\D*)(\d+)", value)
    if not match:
        return value
    prefix, digits = match.groups()
    width = len(digits) if digits.startswith("0") else 0
    return f"{prefix}{int(digits) + offset:0{width}d}"


def fit_demo_to_sample(rows, sample_values, algorithm):
    """Keep the demonstration rows consistent with the sample row in the question."""
    for name in SEQUENTIAL_COLUMNS:
        if name in sample_values:
            for offset, row in enumerate(rows):
                row[name] = continue_sequence(sample_values[name], offset)

    if algorithm == "ring":
        for index, row in enumerate(rows):
            row["next_node_id"] = rows[(index + 1) % len(rows)]["node_id"]

    if algorithm == "bully" and sample_values.get("is_current_coordinator", "").upper() == "TRUE":
        for row in rows[1:]:
            row["is_current_coordinator"] = "FALSE"

    if algorithm in ("lamport", "vector"):
        target_column = "message_to" if algorithm == "lamport" else "target_process"
        first = sample_values.get("process_id", "")
        second = sample_values.get(target_column, "")
        if first and second and first != second:
            third = next(name for name in ("P1", "P2", "P3", "P4") if name not in (first, second))
            renamed = {"P1": first, "P2": second, "P3": third}
            for row in rows:
                row["process_id"] = renamed[row["process_id"]]
                row[target_column] = renamed.get(row[target_column], row[target_column])


def build_dataset_rows(columns, sample, algorithm, mapping):
    demo = [dict(row) for row in DEMO_ROWS[algorithm]]
    if sample is not None:
        given = dict(zip(columns, sample))
        fit_demo_to_sample(demo, {name: given[column] for name, column in mapping.items()}, algorithm)

    canonical_name = {column: name for name, column in mapping.items()}
    rows = []
    for row_index, demo_row in enumerate(demo):
        row = []
        matrix_column = 0
        for column in columns:
            if column in canonical_name:
                row.append(demo_row.get(canonical_name[column], ""))
            elif algorithm == "matrix":
                row.append(str(DEMO_MATRIX[row_index][matrix_column % 4] + matrix_column // 4))
                matrix_column += 1
            else:
                row.append(f"value_{row_index + 1}")
        rows.append(row)

    if sample is not None:
        rows[0] = sample[:]
    return rows


def create_dataset(path, columns, sample, algorithm, mapping):
    if path.exists():
        # Keep existing user data, but verify that its header matches this question.
        with path.open("r", newline="", encoding="utf-8-sig") as file:
            reader = csv.reader(file, skipinitialspace=True)
            existing_columns = [name.strip() for name in next(reader, [])]
        if existing_columns != columns:
            raise ValueError(
                "A file named " + path.name + " already exists, but its columns do not match this question.\n"
                + "Expected: " + ", ".join(columns) + "\n"
                + "Found: " + ", ".join(existing_columns) + "\n"
                + "Rename or remove the old CSV, then run CodeReady again. The old file was not changed."
            )
        return "Existing CSV found with matching columns. It was kept unchanged."

    rows = build_dataset_rows(columns, sample, algorithm, mapping)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(rows)
    return f"Created a {len(rows)}-row demonstration CSV. Check its values before submission."


def common_header(filename, *modules):
    # The generated solution creates its own demonstration CSV when it first runs.
    imports = "\n".join(f"import {name}" for name in sorted({"csv", *modules}))
    columns_text = repr(_CURRENT_CSV_COLUMNS)
    rows_text = repr(_CURRENT_DEMO_ROWS)
    return f'''{imports}
from pathlib import Path

CSV_FILE = {filename!r}
CSV_PATH = Path(__file__).resolve().parent / CSV_FILE
CSV_COLUMNS = {columns_text}
DEMO_ROWS = {rows_text}


def read_rows():
    # Create the sample CSV only when this solution is executed.
    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_COLUMNS)
            writer.writerows(DEMO_ROWS)
        print(f"Created demonstration dataset: {{CSV_FILE}}")

    # Check that an existing file belongs to this question before reading it.
    with CSV_PATH.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, skipinitialspace=True)
        actual_columns = reader.fieldnames or []
        if [name.strip() for name in actual_columns] != CSV_COLUMNS:
            raise ValueError(
                f"The columns in {{CSV_FILE}} do not match this question. "
                f"Expected: {{', '.join(CSV_COLUMNS)}}. "
                f"Found: {{', '.join(actual_columns)}}."
            )
        return list(reader)


'''


def code_rpc(filename):
    return common_header(filename) + r'''def calculate(method, value):
    # This represents the remote function running on the server.
    if method == "add":
        return sum(float(x) for x in value.replace(";", ",").split(","))
    if method == "multiply":
        result = 1
        for x in value.replace(";", ",").split(","):
            result *= float(x)
        return result
    if method == "square":
        return float(value) ** 2
    if method == "uppercase":
        return value.upper()
    return "Data processed: " + value


def run():
    rows = read_rows()
    print("\nRMI / RPC CLIENT-SERVER SIMULATION")
    for row in rows:
        client = row["client_name"]
        method = row["method_name"].strip().lower()
        value = row["param_value"]
        call_id = row["call_id"]

        print(f"\n[DISPATCH] {client} calls {method} (ID: {call_id})")
        print(f"[MARSHAL] Sending method and parameter: {method}, {value}")
        print("[SERVER] Executing remote function...")
        result = calculate(method, value)
        print(f"[RETURN] Result: {result}")


if __name__ == "__main__":
    run()
'''


def code_threads(filename):
    return common_header(filename, "threading") + r'''def run():
    tasks = read_rows()
    lock = threading.Lock()
    completed = []

    # Each thread processes one task.
    def worker(task):
        task_id = task["task_id"]
        name = task["thread_name"]
        print(f"{name} started {task_id}")

        # Lock protects the shared completed list.
        with lock:
            print(f"{name} acquired lock")
            completed.append(task_id)
            task["status"] = "COMPLETED"
            print(f"{name} released lock")

    print("\nMULTITHREADING WITH MUTEX LOCK")
    threads = []
    for task in tasks:
        t = threading.Thread(target=worker, args=(task,))
        threads.append(t)
        t.start()

    # Wait until every thread finishes.
    for t in threads:
        t.join()

    print("\nCompleted tasks:", completed)
    for task in tasks:
        print(task["task_id"], "->", task["status"])


if __name__ == "__main__":
    run()
'''


def code_lamport(filename):
    return common_header(filename) + r'''def run():
    rows = read_rows()
    clocks = {}
    messages = {}
    events = []

    print("\nLAMPORT LOGICAL CLOCK")
    for row in rows:
        event = row["event_id"]
        process = row["process_id"]
        action = row["event_type"].upper()
        other = row["message_to"].strip()
        clocks.setdefault(process, int(row.get("initial_clock") or 0))

        if action == "SEND":
            clocks[process] += 1
            messages[(process, other)] = clocks[process]
        elif action == "RECEIVE":
            sent_time = messages.get((other, process), 0)
            clocks[process] = max(clocks[process], sent_time) + 1
        else:
            clocks[process] += 1

        print(f"{event} ({process}, {action}) -> Clock: {clocks[process]}")
        events.append((clocks[process], process, event))

    print("\nFINAL CAUSAL ORDER:")
    for timestamp, process, event in sorted(events):
        print(f"{event}: Process {process}, Time {timestamp}")


if __name__ == "__main__":
    run()
'''


def code_cristian(filename):
    return common_header(filename) + r'''def run():
    rows = read_rows()
    print("\nCRISTIAN'S CLOCK SYNCHRONIZATION")

    for row in rows:
        client = row["client_id"]
        t0 = float(row["t0_send_ms"])
        server = float(row["t_server_ms"])
        t1 = float(row["t1_recv_ms"])

        rtt = t1 - t0
        estimated_time = server + rtt / 2
        offset = estimated_time - t1

        print(f"\nClient: {client}")
        print(f"RTT = T1 - T0 = {rtt} ms")
        print(f"Estimated server time = {estimated_time} ms")
        print(f"Clock adjustment = {offset} ms")
        print(f"Corrected client time = {t1 + offset} ms")


if __name__ == "__main__":
    run()
'''


def code_berkeley(filename):
    return common_header(filename) + r'''def run():
    rows = read_rows()
    healthy = []

    print("\nBERKELEY'S CLOCK SYNCHRONIZATION")
    for row in rows:
        node = row["node_id"]
        time_value = float(row["clock_time_sec"])
        faulty = row["is_faulty"].strip().upper() == "TRUE"
        print(f"Node {node}: {time_value} seconds")

        if faulty:
            print(f"Node {node} is faulty and will be ignored")
        else:
            healthy.append(time_value)

    if not healthy:
        print("No healthy clocks found")
        return

    average = sum(healthy) / len(healthy)
    print(f"\nAverage clock time = {average:.2f} seconds")

    for row in rows:
        node = row["node_id"]
        time_value = float(row["clock_time_sec"])
        adjustment = average - time_value
        print(f"Node {node} adjustment = {adjustment:+.2f} seconds")


if __name__ == "__main__":
    run()
'''


def code_vector(filename):
    return common_header(filename) + r'''def happened_before(a, b):
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def run():
    rows = read_rows()
    processes = sorted({r["process_id"] for r in rows} |
                       {r["target_process"] for r in rows if r["target_process"]})
    clocks = {p: [0] * len(processes) for p in processes}
    sent_messages = {}
    history = []

    print("\nVECTOR CLOCKS")
    print("Vector order:", processes)

    for row in rows:
        event = row["event_id"]
        process = row["process_id"]
        action = row["event_action"].upper()
        other = row["target_process"].strip()
        i = processes.index(process)

        if action == "RECEIVE":
            received = sent_messages.get((other, process), [0] * len(processes))
            clocks[process] = [max(a, b) for a, b in zip(clocks[process], received)]
            clocks[process][i] += 1
        else:
            clocks[process][i] += 1
            if action == "SEND":
                sent_messages[(process, other)] = clocks[process][:]

        current = clocks[process][:]
        history.append((event, current))
        print(f"{event} ({process}, {action}) -> {current}")

    print("\nCAUSALITY CHECK:")
    for i in range(len(history)):
        for j in range(i + 1, len(history)):
            e1, v1 = history[i]
            e2, v2 = history[j]
            if happened_before(v1, v2):
                print(f"{e1} happened before {e2}")
            elif happened_before(v2, v1):
                print(f"{e2} happened before {e1}")
            else:
                print(f"{e1} and {e2} are CONCURRENT")


if __name__ == "__main__":
    run()
'''


def code_ring(filename):
    return common_header(filename) + r'''def run():
    rows = read_rows()
    nodes = {}
    for row in rows:
        nodes[row["node_id"]] = {
            "next": row["next_node_id"],
            "active": row["is_active"].strip().upper() == "TRUE"
        }

    active = [n for n in nodes if nodes[n]["active"]]
    failed = [n for n in nodes if not nodes[n]["active"]]
    print("\nRING LEADER ELECTION")
    print("Failed nodes:", failed)

    # If no failure is listed, simulate failure of the highest-ID node.
    if not failed and active:
        failed_node = max(active, key=int)
        nodes[failed_node]["active"] = False
        active.remove(failed_node)
        print("Simulated coordinator failure:", failed_node)

    if not active:
        print("No active nodes available")
        return

    start = active[0]
    current = start
    token = []
    print(f"\nElection token starts at node {start}")

    while current not in token and nodes[current]["active"]:
        token.append(current)
        print("Token visits node:", current)
        next_node = nodes[current]["next"]

        # Skip failed nodes and continue around the ring.
        checked = 0
        while next_node in nodes and not nodes[next_node]["active"] and checked < len(nodes):
            next_node = nodes[next_node]["next"]
            checked += 1
        if next_node not in nodes:
            break
        current = next_node

    leader = max(token, key=int)
    print("Token completed:", token)
    print("Elected coordinator:", leader)


if __name__ == "__main__":
    run()
'''


def code_bully(filename):
    return common_header(filename) + r'''def run():
    rows = read_rows()
    alive = []
    coordinator = None

    for row in rows:
        node = int(row["node_id"])
        if row["is_alive"].strip().upper() == "TRUE":
            alive.append(node)
        if row.get("is_current_coordinator", "").strip().upper() == "TRUE":
            coordinator = node

    print("\nBULLY LEADER ELECTION")
    if coordinator is None:
        coordinator = max(int(r["node_id"]) for r in rows)
    print(f"Coordinator {coordinator} has failed")

    alive = [n for n in alive if n != coordinator]
    if not alive:
        print("No active node can become coordinator")
        return

    initiator = min(alive)
    print(f"Node {initiator} starts election")
    for node in sorted(alive):
        if node > initiator:
            print(f"ELECTION: {initiator} -> {node}")
            print(f"OK: {node} -> {initiator}")

    leader = max(alive)
    print(f"\nCOORDINATOR: Node {leader} announces itself as leader")
    print("New coordinator:", leader)


if __name__ == "__main__":
    run()
'''


def code_load_balancing(filename):
    return common_header(filename) + r'''def run():
    jobs = read_rows()
    workers = ["Worker_1", "Worker_2", "Worker_3"]
    load = {worker: 0 for worker in workers}
    count = {worker: 0 for worker in workers}

    print("\nROUND-ROBIN LOAD BALANCING")
    for i, job in enumerate(jobs):
        worker = workers[i % len(workers)]
        job_id = job["job_id"]
        units = float(job["compute_units"])
        load[worker] += units
        count[worker] += 1
        print(f"Job {job_id} ({units:g} units) assigned to {worker}")

    print("\nFINAL WORKER LOAD:")
    for worker in workers:
        print(f"{worker}: {count[worker]} jobs, {load[worker]:g} units")


if __name__ == "__main__":
    run()
'''


def code_matrix(filename):
    return common_header(filename, "threading") + r'''def run():
    rows = read_rows()
    columns = [c for c in rows[0] if c != "row_id"]
    A = [[float(row[c]) for c in columns] for row in rows]

    # The question supplies one matrix, so use its transpose as matrix B.
    B = [list(col) for col in zip(*A)]
    result = [None] * len(A)

    def multiply_row(i):
        result[i] = []
        for j in range(len(B[0])):
            total = 0
            for k in range(len(B)):
                total += A[i][k] * B[k][j]
            result[i].append(total)

    print("\nMPI MATRIX MULTIPLICATION (SCATTER-GATHER SIMULATION)")
    threads = []
    for i in range(len(A)):
        print(f"Master scatters row {i} to Worker {i + 1}")
        t = threading.Thread(target=multiply_row, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\nMaster gathers the results:")
    for row in result:
        print([round(x, 2) for x in row])


if __name__ == "__main__":
    run()
'''

BUILDERS = {
    "rmi_rpc": code_rpc,
    "multithreading": code_threads,
    "lamport": code_lamport,
    "cristian": code_cristian,
    "berkeley": code_berkeley,
    "vector": code_vector,
    "ring": code_ring,
    "bully": code_bully,
    "load_balancing": code_load_balancing,
    "matrix": code_matrix,
}


def use_question_columns(solution_text, mapping):
    """Replace the template's column names with the ones this question uses."""
    def replace(match):
        return '"' + mapping.get(match.group(1), match.group(1)) + '"'
    return re.sub(r'"([a-z0-9_]+)"', replace, solution_text)


def standardize_solution(solution_text, details, label, filename):
    footer = re.compile(r'if __name__ == "__main__":\s*\n\s*run\(\)\s*$', re.M)
    if not footer.search(solution_text):
        raise ValueError("The selected solution template is missing its executable entry point.")

    standardized_footer = (
        "def main():\n"
        "    try:\n"
        "        run()\n"
        "        return 0\n"
        "    except KeyError as error:\n"
        "        print(f\"Error: the CSV has no column named {error}\")\n"
        "    except (OSError, ValueError, TypeError, csv.Error) as error:\n"
        "        print(f\"Error: {error}\")\n"
        "    return 1\n\n\n"
        "if __name__ == \"__main__\":\n"
        "    raise SystemExit(main())"
    )
    solution_text = footer.sub(standardized_footer, solution_text)

    question = details.get("question_number", "")
    header = [
        "# CE301 lab program",
        f"# Topic: {label}",
        f"# Dataset: {filename}",
    ]
    if question:
        header.insert(1, f"# Question: Q{question}")
    if details.get("project_domain"):
        header.append("# Project domain: " + details["project_domain"])
    if details.get("experiment_aim"):
        header.extend(textwrap.wrap(
            details["experiment_aim"], width=78,
            initial_indent="# Experiment aim: ", subsequent_indent="# ",
        ))

    result = "\n".join(header) + "\n\n" + solution_text
    ast.parse(result)
    return result.rstrip() + "\n"


def generate(statement):
    global _CURRENT_CSV_COLUMNS, _CURRENT_DEMO_ROWS
    algorithm, label = detect_algorithm(statement)
    details = extract_question_details(statement)
    question_number = details["question_number"] or None
    columns = extract_columns(statement, algorithm, question_number)
    if not columns or any(not column.strip() for column in columns):
        raise ValueError("The question does not contain a valid CSV column list.")
    if len({column.lower() for column in columns}) != len(columns):
        raise ValueError("The CSV column list contains duplicate names.")
    mapping, assumed = map_columns(columns, algorithm)
    filename = extract_csv_name(statement, algorithm, question_number)
    sample = extract_sample_row(statement, columns, question_number, algorithm)

    # Keep existing user data. The solution will create a sample CSV only if none exists.
    dataset_path = APP_DIR / filename
    if dataset_path.exists():
        with dataset_path.open("r", newline="", encoding="utf-8-sig") as file:
            existing_columns = [name.strip() for name in next(csv.reader(file), [])]
        if existing_columns != columns:
            raise ValueError(
                f"A file named {filename} already exists with different columns. "
                f"Expected: {', '.join(columns)}. Found: {', '.join(existing_columns)}. "
                "The existing file was not changed."
            )
        dataset_status = "Existing CSV found and preserved."
    else:
        dataset_status = "CSV will be created by solution.py when you run it."

    _CURRENT_CSV_COLUMNS = columns[:]
    _CURRENT_DEMO_ROWS = build_dataset_rows(columns, sample, algorithm, mapping)
    if assumed:
        dataset_status += " Some column names were matched by position."

    solution_text = use_question_columns(BUILDERS[algorithm](filename), mapping)
    solution_text = standardize_solution(solution_text, details, label, filename)
    script_path = APP_DIR / "solution.py"
    script_path.write_text(solution_text, encoding="utf-8")
    return script_path, dataset_path, label, dataset_status, columns, details


def read_statement():
    print("Enter a question number (1-340), or paste the full problem statement:", flush=True)
    try:
        first_line = input().strip()
    except EOFError:
        return ""

    # A number alone is enough; the embedded question bank supplies the details.
    if re.fullmatch(r"Q?\s*\d{1,3}", first_line, re.I):
        return first_line

    print("Continue pasting the statement. Type END on a new line when finished:", flush=True)
    lines = [first_line] if first_line else []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def main():
    # Keep a console that cannot show a character from running without crashing.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    print("\nCodeReady - Simplified CE301 ESE Programs")
    statement = read_statement()
    if not statement:
        print("No problem statement was entered.")
        return 1

    try:
        script, dataset, label, dataset_status, columns, details = generate(statement)
    except Exception as error:
        print("\nCodeReady could not generate the files:")
        print(str(error))
        return 1

    print("\n" + "-" * 62)
    print("Detected topic : " + label)
    if details["question_number"]:
        print("Question       : Q" + details["question_number"])
    if details["project_domain"]:
        print("Project domain : " + details["project_domain"])
    print("Dataset        : " + str(dataset))
    print("CSV columns    : " + ", ".join(columns))
    print("Dataset status : " + dataset_status)
    print("Solution file  : " + str(script))
    print("\nThe solution is saved beside this generator. The CSV will be created when solution.py runs if it is missing.")

    if details["experiment_aim"]:
        print("\nExperiment aim:")
        print(textwrap.fill(details["experiment_aim"], width=76))
    if details["expected_output"]:
        print("\nExpected output / verification:")
        print(textwrap.fill(details["expected_output"], width=76))
    if details["execution_instruction"]:
        print("\nAdditional instruction:")
        print(details["execution_instruction"])

    print("\nGenerated Python code (also saved as solution.py):")
    print("-" * 62)
    print(script.read_text(encoding="utf-8"))
    print("-" * 62)

    try:
        answer = input("Run solution.py now? (y/n): ").strip().lower()
    except EOFError:
        answer = "n"

    if answer == "y":
        print("\nRunning solution.py...\n", flush=True)
        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=str(APP_DIR),
                check=False
            )
            if result.returncode != 0:
                print("The solution finished with exit code " + str(result.returncode))
        except OSError as error:
            print("Could not start solution.py: " + str(error))

    print("\nDone. Your files are:")
    print("  " + script.name)
    print("  " + dataset.name + " (created when solution.py runs if missing)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
