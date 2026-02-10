"""
Seed dummy territory data for testing.

Usage:
  docker-compose exec -T web python manage.py shell < scripts/seed_territories.py
"""
from apps.territories.models import District, Precinct, Region

# --- Regions ---
regions_data = [
    {"name": "Tbilisi", "name_ka": "თბილისი", "code": "01"},
    {"name": "Adjara", "name_ka": "აჭარა", "code": "02"},
    {"name": "Imereti", "name_ka": "იმერეთი", "code": "03"},
    {"name": "Kakheti", "name_ka": "კახეთი", "code": "04"},
    {"name": "Kvemo Kartli", "name_ka": "ქვემო ქართლი", "code": "05"},
]

regions = {}
for data in regions_data:
    region, created = Region.objects.get_or_create(code=data["code"], defaults=data)
    regions[data["code"]] = region
    status = "CREATED" if created else "EXISTS"
    print(f"  [{status}] Region: {region.name} ({region.code})")

# --- Districts ---
districts_data = [
    # Tbilisi
    {"region_code": "01", "name": "Vake", "name_ka": "ვაკე", "cec_code": "01.01"},
    {"region_code": "01", "name": "Saburtalo", "name_ka": "საბურთალო", "cec_code": "01.02"},
    {"region_code": "01", "name": "Isani", "name_ka": "ისანი", "cec_code": "01.03"},
    {"region_code": "01", "name": "Gldani", "name_ka": "გლდანი", "cec_code": "01.04"},
    {"region_code": "01", "name": "Didube", "name_ka": "დიდუბე", "cec_code": "01.05"},
    # Adjara
    {"region_code": "02", "name": "Batumi", "name_ka": "ბათუმი", "cec_code": "02.01"},
    {"region_code": "02", "name": "Kobuleti", "name_ka": "ქობულეთი", "cec_code": "02.02"},
    # Imereti
    {"region_code": "03", "name": "Kutaisi", "name_ka": "ქუთაისი", "cec_code": "03.01"},
    {"region_code": "03", "name": "Zestaponi", "name_ka": "ზესტაფონი", "cec_code": "03.02"},
    # Kakheti
    {"region_code": "04", "name": "Telavi", "name_ka": "თელავი", "cec_code": "04.01"},
    {"region_code": "04", "name": "Sighnaghi", "name_ka": "სიღნაღი", "cec_code": "04.02"},
    # Kvemo Kartli
    {"region_code": "05", "name": "Rustavi", "name_ka": "რუსთავი", "cec_code": "05.01"},
    {"region_code": "05", "name": "Marneuli", "name_ka": "მარნეული", "cec_code": "05.02"},
]

districts = {}
for data in districts_data:
    region = regions[data["region_code"]]
    defaults = {
        "region": region,
        "name": data["name"],
        "name_ka": data["name_ka"],
    }
    district, created = District.objects.get_or_create(
        cec_code=data["cec_code"], defaults=defaults
    )
    districts[data["cec_code"]] = district
    status = "CREATED" if created else "EXISTS"
    print(f"  [{status}] District: {district.name} ({district.cec_code})")

# --- Precincts ---
precincts_data = [
    # Vake
    {"district_code": "01.01", "name": "Vake #1", "name_ka": "ვაკე #1", "cec_code": "01.01.001", "lat": 41.7068, "lng": 44.7631},
    {"district_code": "01.01", "name": "Vake #2", "name_ka": "ვაკე #2", "cec_code": "01.01.002", "lat": 41.7085, "lng": 44.7590},
    {"district_code": "01.01", "name": "Vake #3", "name_ka": "ვაკე #3", "cec_code": "01.01.003", "lat": 41.7102, "lng": 44.7555},
    # Saburtalo
    {"district_code": "01.02", "name": "Saburtalo #1", "name_ka": "საბურთალო #1", "cec_code": "01.02.001", "lat": 41.7270, "lng": 44.7470},
    {"district_code": "01.02", "name": "Saburtalo #2", "name_ka": "საბურთალო #2", "cec_code": "01.02.002", "lat": 41.7290, "lng": 44.7440},
    # Isani
    {"district_code": "01.03", "name": "Isani #1", "name_ka": "ისანი #1", "cec_code": "01.03.001", "lat": 41.6920, "lng": 44.8050},
    {"district_code": "01.03", "name": "Isani #2", "name_ka": "ისანი #2", "cec_code": "01.03.002", "lat": 41.6940, "lng": 44.8080},
    # Gldani
    {"district_code": "01.04", "name": "Gldani #1", "name_ka": "გლდანი #1", "cec_code": "01.04.001", "lat": 41.7600, "lng": 44.8200},
    # Didube
    {"district_code": "01.05", "name": "Didube #1", "name_ka": "დიდუბე #1", "cec_code": "01.05.001", "lat": 41.7300, "lng": 44.7800},
    # Batumi
    {"district_code": "02.01", "name": "Batumi #1", "name_ka": "ბათუმი #1", "cec_code": "02.01.001", "lat": 41.6168, "lng": 41.6367},
    {"district_code": "02.01", "name": "Batumi #2", "name_ka": "ბათუმი #2", "cec_code": "02.01.002", "lat": 41.6200, "lng": 41.6400},
    # Kobuleti
    {"district_code": "02.02", "name": "Kobuleti #1", "name_ka": "ქობულეთი #1", "cec_code": "02.02.001", "lat": 41.8120, "lng": 41.7760},
    # Kutaisi
    {"district_code": "03.01", "name": "Kutaisi #1", "name_ka": "ქუთაისი #1", "cec_code": "03.01.001", "lat": 42.2679, "lng": 42.6946},
    {"district_code": "03.01", "name": "Kutaisi #2", "name_ka": "ქუთაისი #2", "cec_code": "03.01.002", "lat": 42.2700, "lng": 42.7000},
    # Zestaponi
    {"district_code": "03.02", "name": "Zestaponi #1", "name_ka": "ზესტაფონი #1", "cec_code": "03.02.001", "lat": 42.1100, "lng": 43.0500},
    # Telavi
    {"district_code": "04.01", "name": "Telavi #1", "name_ka": "თელავი #1", "cec_code": "04.01.001", "lat": 41.9198, "lng": 45.4731},
    # Sighnaghi
    {"district_code": "04.02", "name": "Sighnaghi #1", "name_ka": "სიღნაღი #1", "cec_code": "04.02.001", "lat": 41.6167, "lng": 45.9214},
    # Rustavi
    {"district_code": "05.01", "name": "Rustavi #1", "name_ka": "რუსთავი #1", "cec_code": "05.01.001", "lat": 41.5495, "lng": 44.9939},
    # Marneuli
    {"district_code": "05.02", "name": "Marneuli #1", "name_ka": "მარნეული #1", "cec_code": "05.02.001", "lat": 41.4730, "lng": 44.8040},
]

for data in precincts_data:
    district = districts[data["district_code"]]
    defaults = {
        "district": district,
        "name": data["name"],
        "name_ka": data["name_ka"],
        "latitude": data["lat"],
        "longitude": data["lng"],
    }
    precinct, created = Precinct.objects.get_or_create(
        cec_code=data["cec_code"], defaults=defaults
    )
    status = "CREATED" if created else "EXISTS"
    print(f"  [{status}] Precinct: {precinct.name} ({precinct.cec_code})")

print(f"\nDone! {Region.objects.count()} regions, {District.objects.count()} districts, {Precinct.objects.count()} precincts")
