from setuptools import setup

setup(
    name="ecs-ctl",
    version="0.1.0",
    author="Diego A.",
    author_email="diego.acuna@mailbox.org",
    url="https://github.com/diegoacuna/ecs-ctl",
    description="Manage Amazon ECS like with kubectl",
    license='MIT',
    # Dependent packages (distributions)
    install_requires=[
        "boto3",
        "tabulate"
    ],
    scripts=['bin/ecs-ctl']
)
