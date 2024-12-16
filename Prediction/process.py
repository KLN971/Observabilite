import json
import re
import pandas as pd
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig

# Configuration de Drain3
config = TemplateMinerConfig()
config.load("drain3.ini")
config.profiling_enabled = True
drain_parser = TemplateMiner(config=config)

# Définition des regex log_pattern_type_1 et log_pattern_type_2
log_pattern_type_1 = re.compile(
        r'{"body":"(?P<Body>(?:(?!" ).)+)",'
        r'"attributes":\{"log\.file\.name":"(?P<LogFileName>[^"]+)"\}'  # Capture du champ log.file.name
    )

log_pattern_type_2 = re.compile(

    r'{"body":"(?P<Body>[^"]+)",'  # Capture du champ body
    r'"traceid":"(?P<TraceID>[a-f0-9]+)",'  # Capture du champ traceid
    r'"spanid":"(?P<SpanID>[a-f0-9]+)",'  # Capture du champ spanid
    r'"severity":"(?P<Severity>[a-z]+)",'  # Capture du champ severity
    r'"flags":(?P<Flags>\d+),'  # Capture du champ flags
    r'"attributes":\{"log\.type":"(?P<LogType>[^"]+)"\},'  # Capture du champ log.type
    r'"resources":(?P<Resources>\{[^\}]+\}),'  # Capture du champ service.name
    r'"instrumentation_scope":\{"name":"(?P<InstrumentationName>[^"]+)"\}}'  # Capture du champ instrumentation_scope

)

templates = {}
parsed_events = []

# Nettoyer le fichier CSV
with open("logs_de_base_projet.csv", "r", encoding="utf-8") as f:
    cleaned_lines = []
    for line in f:
        # 🔥 1. Supprimer les guillemets au début et à la fin
        line = line.strip().strip('"')

        # 🔥 2. Transformer 4 guillemets ("""") en 2 guillemets ("")
        line = line.replace('""', '"')
        line = line.replace('""""', '""')
        cleaned_lines.append(line)

# Écrire le fichier propre
with open("logs_de_base_projet_clean.csv", "w", encoding="utf-8") as f:
    f.write("\n".join(cleaned_lines))
# Charger le fichier propre avec pandas
logs_df = pd.read_csv("logs_de_base_projet_clean.csv", sep=",", encoding="utf-8", header=0, quotechar='"', doublequote=True)

for i, row in logs_df.iterrows():
    line = row['Line'].lower()  # On cible uniquement la colonne 'Line'

    if i % 10000 == 0:
        print(f"Matching line {i}")
    match1 = log_pattern_type_1.match(line)
    match2 = log_pattern_type_2.match(line)
    if match1:
        log_content = match1.group("Body")
        drain_parser.add_log_message(log_content)
    elif match2:
        log_content = match2.group("Body")
        drain_parser.add_log_message(log_content)
    else:
        print(f"No match for line {i}: {line}")

for i, row in logs_df.iterrows():
    line = row['Line'].lower()  # On cible uniquement la colonne 'Line'
    timestamp_str = row['Time']

    if i % 10000 == 0:
        print(f"Parsing line {i}")
    match1 = log_pattern_type_1.match(line)
    match2 = log_pattern_type_2.match(line)
    log_data = None
    if match1:
        log_data = match1.groupdict()
    elif match2:
        log_data = match2.groupdict()
    if log_data:
        log_content = log_data.get("Body", "")
        result = drain_parser.match(log_content)
        if result:
            template_id = result.cluster_id
            anomaly = 1 if pd.to_datetime(timestamp_str) >= pd.to_datetime('2024-12-14 16:02:20.629') and pd.to_datetime(
                timestamp_str) < pd.to_datetime('2024-12-14 16:02:30') or pd.to_datetime(timestamp_str) >= pd.to_datetime('2024-12-14 16:07:20.629') and pd.to_datetime(
                timestamp_str) < pd.to_datetime('2024-12-14 16:07:22')  else 0
            template_description = result.get_template()
            parsed_events.append({
                "Timestamp": timestamp_str,
                "Template ID": template_id,
                "Anomaly": anomaly
            })
            if template_id not in templates:
                templates[template_id] = template_description
        else:
            print(f"No template found for line {i}: {line}")
    else:
        print(f"No match for line {i}: {line}")

print(f"Found {len(templates)} templates and {len(parsed_events)} parsed events")

parsed_df = pd.DataFrame(parsed_events)
parsed_df.to_csv("logs_parsed.csv", index=False)

with open('templates.json', 'w') as file:
    json.dump(templates, file, indent=4)  # `indent=4` pour mieux formater


def count_within_30sec_or_first_alert(df, time_column='Timestamp', event_column='Template ID', block_size_seconds=30):
    # Convert the time column to datetime format if it isn't already, limiting to HH:MM:SS
    df[time_column] = pd.to_datetime(df[time_column].str.slice(0, 19), format='%Y-%m-%d %H:%M:%S', errors='coerce')

    # Drop rows where the timestamp could not be parsed
    #df = df.dropna(subset=[time_column])

    # Sort the DataFrame by timestamp
    df = df.sort_values(by=[time_column])
    df.to_csv("logs_parsed_sorted.csv", index=False)

    # Round down each timestamp to the nearest 30-second block
    df['Time_Block'] = df[time_column].dt.floor(f'{block_size_seconds}s')

    # Count the number of each type of event in each 30-second block and stop at first anomaly
    block_event_counts = []
    for time_block, group in df.groupby('Time_Block'):
        block_counts = {event_id: 0 for event_id in range(1, 26)}
        anomaly_detected = 0
        for _, row in group.iterrows():
            if anomaly_detected == 1:
                break
            event_id = row[event_column]
            if event_id in block_counts:
                block_counts[event_id] += 1
            if row['Anomaly'] == 1:
                anomaly_detected = 1
        block_counts['Anomaly'] = anomaly_detected
        block_counts['Time_Block'] = time_block
        block_event_counts.append(block_counts)

    block_event_counts_df = pd.DataFrame(block_event_counts)

    # Reorder columns to ensure they are in numeric order from 1 to 25 and include Anomaly and Time_Block
    column_order = ['Time_Block'] + list(range(1, 26)) + ['Anomaly']
    block_event_counts_df = block_event_counts_df[column_order]

    return block_event_counts_df

def count_within_10sec_or_first_alert(df, time_column='Timestamp', event_column='Template ID', block_size_seconds=10):
    # Convert the time column to datetime format if it isn't already, limiting to HH:MM:SS
    #df[time_column] = pd.to_datetime(df[time_column].str.slice(0, 19), format='%Y-%m-%d %H:%M:%S', errors='coerce')

    # Drop rows where the timestamp could not be parsed
    #df = df.dropna(subset=[time_column])

    # Sort the DataFrame by timestamp
    df = df.sort_values(by=[time_column])
    df.to_csv("logs_parsed_sorted.csv", index=False)

    # Round down each timestamp to the nearest 30-second block
    df['Time_Block'] = df[time_column].dt.floor(f'{block_size_seconds}s')

    # Count the number of each type of event in each 30-second block and stop at first anomaly
    block_event_counts = []
    for time_block, group in df.groupby('Time_Block'):
        block_counts = {event_id: 0 for event_id in range(1, 26)}
        anomaly_detected = 0
        for _, row in group.iterrows():
            if anomaly_detected == 1:
                break
            event_id = row[event_column]
            if event_id in block_counts:
                block_counts[event_id] += 1
            if row['Anomaly'] == 1:
                anomaly_detected = 1
        block_counts['Anomaly'] = anomaly_detected
        block_counts['Time_Block'] = time_block
        block_event_counts.append(block_counts)

    block_event_counts_df = pd.DataFrame(block_event_counts)

    # Reorder columns to ensure they are in numeric order from 1 to 25 and include Anomaly and Time_Block
    column_order = ['Time_Block'] + list(range(1, 26)) + ['Anomaly']
    block_event_counts_df = block_event_counts_df[column_order]

    return block_event_counts_df

result_30_df = count_within_30sec_or_first_alert(parsed_df, time_column='Timestamp', event_column='Template ID', block_size_seconds=30)
result_30_df.to_csv("template_counts_error_detection.csv", index=False)

result_10_df = count_within_10sec_or_first_alert(parsed_df, time_column='Timestamp', event_column='Template ID', block_size_seconds=10)
result_10_df.to_csv("template_counts_error_prediction.csv", index=False)
