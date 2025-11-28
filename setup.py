from setuptools import setup, find_packages

setup(
    name='md-audit',
    version='1.0.0',
    description='Markdown SEO诊断工具',
    author='Claude Code',
    packages=find_packages(),
    install_requires=[
        'pydantic>=2.0.0',
        'python-frontmatter>=1.0.0',
        'markdown>=3.4.0',
        'beautifulsoup4>=4.12.0',
        'openai>=1.0.0',
        'pyyaml>=6.0',
    ],
    entry_points={
        'console_scripts': [
            'md-audit=md_audit.main:main',
        ],
    },
    python_requires='>=3.8',
)
