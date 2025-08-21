import json

def analyze_wallet_activity(wallet_address, tx_data):
    swap_count = sum(1 for tx in tx_data if tx["type"] == "swap")
    dormant_periods = [tx["timestamp"] for tx in tx_data if tx["value"] == 0]

    report = []
    report.append(f"  Toplam Swap Say"s": {swap_count}")
    report.append(f"' Pasif "...lemler: {len(dormant_periods)}")

    high_freq = [tx for tx in tx_data if tx["frequency"] > 10]
    if high_freq:
        report.append(f" Yksek frekansl" i...lem davran"..." tespit edildi.")

    contract_interactions = {tx["to"] for tx in tx_data if tx["type"] == "contract_call"}
    if contract_interactions:
        report.append(f" Etkile...imde bulunulan kontratlar: {len(contract_interactions)} adet.")

    return report
