def analyze_destiny_flux(chain_energy_flow):
    destiny_signals = []
    for event in chain_energy_flow:
        if event['potential'] > 85 and event['visibility'] < 30:
            destiny_signals.append(f"?Y'  G?r1?4nmeyen Kader Tetikleyicisi: {event['id']}")
    return destiny_signals if destiny_signals else ["?Y? Kod ak"+/-...Y"+/-nda ola"Yan1?4st1?4 bir kader tetikleyicisi yok."]










