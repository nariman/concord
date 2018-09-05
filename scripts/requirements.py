# Extracting dependencies from lock file.
# LGTM looks for setup.py or requirements.txt files, but fails.
# We are using Poetry, which has no feature to export dependencies list yet...
# Should be started from the project root.

LOCK_FILE = "pyproject.lock"
REQUIREMENTS_FILE = "requirements.txt"

if __name__ == "__main__":
    import tomlkit

    lockfile = open(LOCK_FILE)
    depsfile = open(REQUIREMENTS_FILE, "w")

    deps = tomlkit.parse(lockfile.read())

    for dep in deps["package"]:
        if dep["category"] == "main":
            depsfile.write(
                "{name}=={version}\n".format(
                    name=dep["name"], version=dep["version"]
                )
            )
