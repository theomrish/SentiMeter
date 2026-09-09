from surprise import surprise_calc
print("report is running")


RELEASES = [
    {"name": "CPI YoY", "prior":3.2,"consensus":2.9,"actual":3.0},
    {"name": "Core CPI YoY", "prior":4.0,"consensus":3.8,"actual":3.7},
    {"name": "Nonfarm Payrolls", "prior":216.0,"consensus":180.0,"actual":254.0},
    {"name": "Unemployment Rate", "prior":4.2,"consensus":4.2,"actual":4.1},
    {"name": "ISM Manufacturing PMI", "prior":48.5,"consensus":47.6,"actual":49.1}
]

print(f"{'Release':<20} {'Level':>9} {'Move':>9} {'Surprise':>9}")
for data in RELEASES:
    facts = surprise_calc(prior=data["prior"],consensus=data["consensus"],actual=data["actual"])
    print(f"{data['name']:<20} {facts.level:>9.2f} {facts.move:>+9.2f} {facts.surprise:>+9.2f}")
