from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
	name="botsfordiscordapi",
	version="0.1",
	description="A bots for discord api handler",
	long_description=long_description,
	url="https://gitlab.com/Luke-6723/botsfordiscordapi",
	author="",
	email="",
	license="",
	packages=[],
	zip_safe=False,
	scripts=["botsfordiscordapi.py"],
	install_requires=[
		"requests",
	]
)
