import setuptools,sys,os.path
from sphinx.setup_command import BuildDoc
cmdclass = { 'doc': BuildDoc, 'cov': BuildDoc }
from webcli.utils.git import versiontag

version = versiontag().version()
dirty = (version.local.value is not None)

short_version = repr(version.release)
version = str(version)

name = 'neze-webcli'
author='Clement Durand',
doc_opt = {
    'project': ('setup.py',name),
    'version': ('setup.py',short_version),
    'release': ('setup.py',version),
    'source_dir': ('setup.py','doc'),
}
cov_opt = dict(doc_opt)
cov_opt.update({
    'builder': ('setup.py','coverage'),
})

if len(sys.argv) < 2:
    if dirty:
        sys.stderr.write('Dirty tree.\n')
        sys.exit(1)
    wheel = '-'.join([name.replace('-','_'),version,'py3','none','any'])+'.whl'
    sdist = '-'.join([name,version])+'.tar.gz'
    dist = 'dist'
    print(os.path.join(dist,wheel))
    print(os.path.join(dist,sdist))
    sys.exit(0)


with open("webcli/__version__.py", "w") as vf:
    vf.write("__VERSION__='{}'\n".format(version))

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=name,
    version=version,
    author=author,
    author_email="durand.clement.13@gmail.com",
    description="Utility suite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
    ),
    entry_points={
        'console_scripts': [
            'transmission = webcli.cli.transmission:main',
            'gitlab = webcli.cli.gitlab:main',
            'git-piptag = webcli.cli.git_piptag:main',
            'wcc = webcli.cli.wcc:main',
        ]
    },
    install_requires=['requests','PyYAML'],
    cmdclass=cmdclass,
    command_options={
        'doc': doc_opt,
        'cov': cov_opt,
    }
)
