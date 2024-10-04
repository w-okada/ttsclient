import json
import subprocess

# LGPLはソース開示不要のようだ。soxrはセーフ。
# https://www.it-houmu.com/archives/1902

LICENSE_FILE_FLAT = "licenses_flat.json"
LICENSE_FILE_SORTED_BY_LICENSE = "licenses_by_license.json"

LICENSE_OVERWRITE = [
    {
        "name": "pyworld",
        "license": "MIT",
    }
]

DEV_MODULES = [
    "pyinstaller",
    "pyinstaller-hooks-contrib",
]


def load_existing_licenses(filename: str):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_licenses(filename: str, licenses: dict):
    with open(filename, "w") as file:
        json.dump(licenses, file, indent=2)


def get_license_info():
    result = subprocess.run(["poetry", "run", "pip-licenses", "--format=json", "--order=license"], stdout=subprocess.PIPE)
    return json.loads(result.stdout)


def generate():
    generate_flat_data()
    generate_by_license_data()


def generate_by_license_data():
    existing_licenses = load_existing_licenses(LICENSE_FILE_FLAT)
    sorted_by_license = {}
    for existing_license in existing_licenses:
        name = existing_license["name"]
        if name in DEV_MODULES:
            continue

        version = existing_license["version"]
        license = existing_license["license"]
        license_url = existing_license["licenseURL"]
        repositry = existing_license["repositry"]
        note = ""
        if name in ["Distance"]:
            note = "excluded by pyinstaller"

        if license not in sorted_by_license:
            sorted_by_license[license] = []

        info = {
            "name": name,
            "version": version,
            "licenseURL": license_url,
            "repositry": repositry,
            "note": note,
        }
        sorted_by_license[license].append(info)

    save_licenses(LICENSE_FILE_SORTED_BY_LICENSE, sorted_by_license)


def generate_flat_data():
    existing_licenses = load_existing_licenses(LICENSE_FILE_FLAT)
    new_licenses = get_license_info()

    for license_info in new_licenses:
        name = license_info["Name"]
        version = license_info["Version"]
        license = license_info["License"]

        existing_license = [x for x in existing_licenses if x["name"] == name]
        if len(existing_license) == 0:  # 新規モジュール
            print(f"! !!! ! {name} is new ! !!! !")
            existing_licenses.append({"name": name, "version": version, "license": license, "licenseURL": "http://SHOULD_BE_WRITTEN", "repositry": ""})
        elif len(existing_license) > 1:  # 複数登録されている　⇒　例外
            raise Exception("Duplicate license info")
        else:  # 既に存在している。
            if existing_license[0]["license"] != license:  # 登録されているライセンスが異なる。
                if name in [x["name"] for x in LICENSE_OVERWRITE]:  # 上書き情報がある場合
                    overwrite_info = [x for x in LICENSE_OVERWRITE if x["name"] == name][0]
                    print(f"!!! !!! !!! {name}: Overwrite {license} -> {overwrite_info['license']} !!! !!! !!!")
                    existing_license[0]["license"] = overwrite_info["license"]
                else:
                    raise Exception(f"license is updated! {name}, {existing_license[0]['license']} -> {license}")

    existing_licenses = sorted(existing_licenses, key=lambda x: x["name"])
    save_licenses(LICENSE_FILE_FLAT, existing_licenses)


if __name__ == "__main__":
    generate_flat_data()
