from setuptools import setup, find_packages

setup(
    name="ipmi",
    version="1.1",
    description="A ipmi python client used in NetXMS migrated from perl",
    long_description=(
        "mainly use the /usr/sbin/ipmi-sensors command\n\n"
        "Release Log:\n"
        "1.1: add parameter --filter-by-headers filter the ipmi result by headers\n"
        "1.0: add --ignore-unrecognized-event parameter to ipmi-sensor\n"
        "0.9: add event field to output \n"
        "0.8: add show header switch param \n"
    ),
    url="https://github.com/zhao-ji/check_ipmi_sensor_v3",
    keywords='ipmi netxms',
    author="Trevor Max",
    author_email="me@minganci.org",
    license="MIT",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "ipmi_tool=ipmi:main",
        ],
    },
)
