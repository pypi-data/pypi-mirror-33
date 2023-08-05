# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).
From http://keepachangelog.com

## 3.4.0 - 2018-06-16
### Fixed
- Add missing post-up handling (thansk @patrickcjh)
- Increased portability using short args (thanks @lucascoelhof)


## 3.3.0 - 2018-01-27
### Added
- wpa-conf to adapter and reader/writer. (thanks @mikeodr)

### Fixed
- parsing of options dict as 'bridge-opts' as this is the true attribute
	 title when reading it back from 'attributes' accessor. (thanks @mikeodr)
- existing parsing of set_options for dns-search. (thanks @mikeodr)


## 3.2.1 - 2018-01-18
### Fixed
- Bug with new ability to add comments


## 3.2.0 - 2018-01-18
### Added
- Ability to provide header comments (thanks @mikeodr)
- Parsing of 'dns-search' (thanks @mikeodr)
- Adding missing option 'bridge_maxwait' to interfaces writer. (thanks @mikeodr)

### Fixed
- Only one DNS IP was being read or written by the library. (thanks @Jude188)
- Strict ordering of dns-search option after the dns-namerservers  (thanks @mikeodr)


## 3.1.0 - 2017-03-01
### Added
- Docs to read the docs :-)
- Class can be imported more easily as in the example : from debinterface import Interfaces
- DeprecationWarning for hotplug key, will be changed to allow-hotplug in 4.0

### Changed
- PR from mchubby: chmod destination file to 0644
- dnsmasqRange.rm_itf_range returns False is nothing was changed
- Removed validation code from NetworkAdapter to its own class
- Do not backup/restore if creating a new interfaces file

### Fixed
- shutil.copy is replaced by os.rename which is atomic
- bad if/else
- failing tests
- NetworkAdapter : missing pre-down, post-up functions
- ifup command was not an absolute path (thanks @ymolinet)


## 3.0.1 - 2016-09-15
### Fixed
- wrong paramter to ifup, thanks dimagafurov


## 3.0 - 2016-08-15
### Changed
- Makes flake8 happy
- REMOVED compatibility with python 2.6


## 2.3 - 2016-08-07
### Changed
- Code is ready to be deployed to PyPi


## 2.2 - 2016-07-22
### Changed
- InterfacesWritter : uses ifup --no-act to check for /etc/network/interfaces validity
- adapter : it is possible to access its properties


## 2.1 - 2016-07-10
### Added
- a changelog...

### Changed
- toolutils : safe_subprocess : enforce shell command being an array
- interfacesWriter : uses 'ifup -a --no-act' to check the interfaces file just written.


## 2.0-beta - 2014-09-01
### Changed
- refactoring which breaks retrocompatibility


## 1.0 - 2012-12-15
### Added
- Read, writing, and editing supported.
- Specify file locations in constants.py
