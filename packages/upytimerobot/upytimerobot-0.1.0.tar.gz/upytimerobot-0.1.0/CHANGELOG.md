# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Add support to add new Monitors
- Add support to edit existing Monitors
- Add support to delete existing Monitors
- Add support to add new Alert Contacts
- Add support to edit existing Alert Contacts
- Add support to delete existing Alert Contacts
- Add support to add new Maintenance Windows
- Add support to edit existing Maintenance Windows
- Add support to delete existing Maintenance Windows
- Add support to add new Public Status Pages
- Add support to edit existing Public Status Pages
- Add support to delete existing Public Status Pages
- Make the module work as a standalone script

## [0.1.0] - 2018-06-18
This is functional module already, one can query all the information regarding `account`, `monitors`, `alert contacts`, `maintenance windows` and `public status pages`.

Also, the functions are all well documented, containing all the possible parameters that can be used to each of the queries available.  

### Added
- Add `constants` file to hold parameters options 
### Changed
- Renamed some internal usage methods to differentiate from the public ones
- Improved documentation on the existing methods
- Way of import some of the libraries
- `.get_monitors_by_name`: Changed validation if a monitor was recovered
- `.get_monitors_by_id`: Changed validation if a monitor was recovered

## 0.0.1 - 2018-06-15

The very beginning of this module, it arrives with all possible queries already done.  There are few documentation regarding the class and methods being implemented.
 
### Added
- Initial commit
- Config file to host API key and other options
- All read only API calls are implemented:
  - `getMonitors`
  - `getAccountDetails`
  - `getAlertContacts`
  - `getMWindows`
  - `getPSPs`

[0.0.2]: https://gitlab.com/fboaventura/upytimerobot/compare/0.0.1...0.0.2
[Unreleased]: https://gitlab.com/fboaventura/upytimerobot/compare/0.0.1...master
