
## Release 1.10.3 (2021-08-03T18:18:56)
### Features
* update the dependencies of the overlays (#734)

## Release 1.2.0 (2019-06-20T12:31:22)
* :pushpin: Automatic update of dependency thoth-common from 0.8.11 to 0.9.0
* Add build trigger with generic webhook
* :pushpin: Automatic update of dependency virtualenv from 16.6.0 to 16.6.1
* :pushpin: Automatic update of dependency pip-tools from 3.7.0 to 3.8.0
* :pushpin: Automatic update of dependency thoth-common from 0.8.7 to 0.8.11
* Fix component label so that solver names are correctly parsed
* Solver is a standalone container, not sidecar
* Check if the given package in the given version was solved by specific solver
* modify link
* Retry if subgraph check API does not respond with correct status code
* :sparkles: a little bit more verbosity
* :bug: we need to provide a pull secret
* :sparkles: using some proper labels
* :green_heart: fixed a major yaml lint bear error
* :sparkles: added solver for UBI8-Py36
* :pushpin: Automatic update of dependency requests from 2.21.0 to 2.22.0
* :pushpin: Automatic update of dependency virtualenv from 16.5.0 to 16.6.0
* :pushpin: Automatic update of dependency thoth-common from 0.8.5 to 0.8.7
* :pushpin: Automatic update of dependency pip-tools from 3.6.1 to 3.7.0
* Minor fix to display correct release in title of docs html
* :pushpin: Automatic update of dependency pip-tools from 3.6.0 to 3.6.1
* :pushpin: Automatic update of dependency virtualenv from 16.4.3 to 16.5.0
* :pushpin: Automatic update of dependency autopep8 from 1.4.3 to 1.4.4
* :pushpin: Automatic update of dependency thoth-common from 0.8.4 to 0.8.5
* Automatic update of dependency thoth-common from 0.8.3 to 0.8.4
* Automatic update of dependency thoth-common from 0.8.2 to 0.8.3
* Automatic update of dependency pip-tools from 3.5.0 to 3.6.0
* Automatic update of dependency thoth-common from 0.8.1 to 0.8.2
* added the registry, why the hell the jobs needs that...
* :sparkles: added ImageStream namespace and tag
* Automatic update of dependency thoth-python from 0.4.6 to 0.5.0
* Add Thoth's configuration file
* Automatic update of dependency thoth-common from 0.7.1 to 0.8.1
* Use Sphinx for documentation
* Automatic update of dependency pip-tools from 3.4.0 to 3.5.0
* Minor fixes in implementation
* Install thoth-python, use Python3.6 in virtual env
* Fix logical error due to which we did not resolve transitive deps locally
* Automatic update of dependency virtualenv from 16.4.1 to 16.4.3
* Cleanup successful solver jobs after 2 hours
* Restart solver run if anything goes wrong
* Automatic update of dependency virtualenv from 16.4.0 to 16.4.1
* Automatic update of dependency pip-tools from 3.3.2 to 3.4.0
* using the correct name now
* added f28, f29 solvers, relocked pipfile
* Automatic update of dependency thoth-common from 0.6.0 to 0.7.1
* Automatic update of dependency thoth-analyzer from 0.1.0 to 0.1.2
* Automatic update of dependency pip-tools from 3.2.0 to 3.3.2
* Automatic update of dependency virtualenv from 16.2.0 to 16.4.0
* It's already 2019
* Automatic update of dependency pipdeptree from 0.13.1 to 0.13.2
* Automatic update of dependency thoth-common from 0.5.0 to 0.6.0
* Format using black
* Add venv to ignore file for local runs
* Fix debug message printed
* Use solver naming convention
* Pass solver job identifier for workload operator
* Update job-template.yaml
* Automatic update of dependency virtualenv from 16.1.0 to 16.2.0
* Automatic update of dependency pip-tools from 3.1.0 to 3.2.0
* Automatic update of dependency requests from 2.20.1 to 2.21.0
* hotfixed coala error
* Automatic update of dependency thoth-common from 0.4.6 to 0.5.0
* Graph sync operator was renamed
* Mark solver for cleanup
* Register solver for operator handling
* Introduce subgraph check API parameter in template
* Add check for subgraph checks
* Restore correctly environment in case of any exception

## Release 1.2.1 (2019-07-16T19:43:35)
* Include MANIFEST.in file
* :pushpin: Automatic update of dependency virtualenv from 16.6.1 to 16.6.2
* :pushpin: Automatic update of dependency thoth-common from 0.9.2 to 0.9.3
* :pushpin: Automatic update of dependency thoth-common from 0.9.1 to 0.9.2
* :pushpin: Automatic update of dependency thoth-common from 0.9.0 to 0.9.1
* Configure pod ttl to be same as job ttl
* Quote package name in case of no releases found
* Fix permission denied when installing to venv

## Release 1.2.2 (2019-07-22T21:06:26)
* Be more precise with the exception raised
* :pushpin: Automatic update of dependency thoth-common from 0.9.3 to 0.9.4
* :pushpin: Automatic update of dependency pip-tools from 3.8.0 to 3.9.0

## Release 1.4.0 (2019-11-08T11:54:53)
* Add README metadata based on the current implementation
* Move also pipdeptree installation into a pre-built virtualenv
* Provide an option to pass pre-built virtualenvironment
* Rewrite solver to use packaging instead of pip internals
* Provide information if the given package was found on the index
* Aggregate information which is a list of strings
* Lower requests for running solver jobs
* Remove ttl configuration for cleanup
* updated templates with annotations and param thoth-advise-value
* :pushpin: Automatic update of dependency pytest from 5.2.1 to 5.2.2
* Fixing metadata part, missed previously
* Dot not allowed in container name as per DNS-1123
* Install py3.6 as base python in f29
* Updated Imagestream from ubi to rhel
* Correctly report issues when aggregating metadata for old packages
* Name Conversion of ubi to rhel 8.0
* Update the cmd as python in all solver images
* Update the cmd as python
* :pushpin: Automatic update of dependency virtualenv from 16.7.6 to 16.7.7
* :pushpin: Automatic update of dependency thoth-python from 0.6.4 to 0.6.5
* :pushpin: Automatic update of dependency virtualenv from 16.7.5 to 16.7.6
* :pushpin: Automatic update of dependency pip-tools from 4.1.0 to 4.2.0
* Be consistent with index_url and package_version
* Add a test for checks that packages of this solver do not affect the inspected ones
* Reverse order of imports
* Log warning if found version does not match the one requested
* Show more debug messages to debug instrumented virtual environments
* Show more debug messages to debug instrumented virtual environments
* Log warning if found version does not match the one requested
* :pushpin: Automatic update of dependency thoth-common from 0.9.12 to 0.9.14
* :pushpin: Automatic update of dependency thoth-python from 0.6.3 to 0.6.4
* :pushpin: Automatic update of dependency pytest-cov from 2.7.1 to 2.8.1
* :pushpin: Automatic update of dependency pytest from 5.2.0 to 5.2.1
* :pushpin: Automatic update of dependency thoth-common from 0.9.11 to 0.9.12
* Adjust testsuite respecting key names
* Be backwards compatible with older versions of solver
* Log warning if the given package cannot be parsed
* Bump solver version
* Adjust testsuite to be backwards compatible
* Be backwards compatible with older release
* Add test for parsing extra and extras
* Remove responses from requirements
* Drop subgraph checks
* Update README file description
* Adjust testsuite accordingly


## Release 1.4.1 (2019-12-05T19:07:50)
* :pushpin: Automatic update of dependency thoth-analyzer from 0.1.5 to 0.1.6
* Propagate information whether the given package and version is provided by index
* Change Sphinx theme
* :pushpin: Automatic update of dependency thoth-common from 0.9.20 to 0.9.21
* :pushpin: Automatic update of dependency importlib-metadata from 1.1.2 to 1.2.0
* :pushpin: Automatic update of dependency importlib-metadata from 1.1.0 to 1.1.2
* :pushpin: Automatic update of dependency thoth-common from 0.9.19 to 0.9.20
* :pushpin: Automatic update of dependency importlib-metadata from 1.0.0 to 1.1.0
* :pushpin: Automatic update of dependency importlib-metadata from 0.23 to 1.0.0
* :pushpin: Automatic update of dependency mypy from 0.740 to 0.750
* :pushpin: Automatic update of dependency thoth-common from 0.9.17 to 0.9.19
* :pushpin: Automatic update of dependency thoth-analyzer from 0.1.4 to 0.1.5
* :pushpin: Automatic update of dependency thoth-common from 0.9.16 to 0.9.17
* Propagate document id into job
* :pushpin: Automatic update of dependency pytest from 5.3.0 to 5.3.1
* :pushpin: Automatic update of dependency virtualenv from 16.7.7 to 16.7.8
* :pushpin: Automatic update of dependency pytest from 5.2.4 to 5.3.0
* :pushpin: Automatic update of dependency pytest from 5.2.3 to 5.2.4
* :pushpin: Automatic update of dependency pytest from 5.2.2 to 5.2.3
* :pushpin: Automatic update of dependency thoth-common from 0.9.15 to 0.9.16
* f30 & f31  based solver images
* :pushpin: Automatic update of dependency thoth-common from 0.9.14 to 0.9.15
* Document how to create and install solver in Thoth
* explicitly using a specific python binary
* introduced rhel81 solver, and fixed rhel80 solver (by building from earlier tag)
* Be explicit with Python installation used
* :sparkles: build from the latest release of ubi8
* Fix issues with solver venv installation
* Fix permission issues in solver runs
* Upgrade setuptools present in the base image on build
* Fix complains during uploads to PyPI
* Release of version 1.4.0
* :pushpin: Automatic update of dependency thoth-python from 0.6.5 to 0.7.1
* Update the README file to show how to run solver locally
* Add README metadata based on the current implementation
* Move also pipdeptree installation into a pre-built virtualenv
* Provide an option to pass pre-built virtualenvironment
* Rewrite solver to use packaging instead of pip internals
* Provide information if the given package was found on the index
* Aggregate information which is a list of strings
* Lower requests for running solver jobs
* Remove ttl configuration for cleanup
* updated templates with annotations and param thoth-advise-value
* :pushpin: Automatic update of dependency pytest from 5.2.1 to 5.2.2
* Fixing metadata part, missed previously
* Dot not allowed in container name as per DNS-1123
* Install py3.6 as base python in f29
* Updated Imagestream from ubi to rhel
* Correctly report issues when aggregating metadata for old packages
* Name Conversion of ubi to rhel 8.0
* Update the cmd as python in all solver images
* Update the cmd as python
* :pushpin: Automatic update of dependency virtualenv from 16.7.6 to 16.7.7
* :pushpin: Automatic update of dependency thoth-python from 0.6.4 to 0.6.5
* :pushpin: Automatic update of dependency virtualenv from 16.7.5 to 16.7.6
* :pushpin: Automatic update of dependency pip-tools from 4.1.0 to 4.2.0
* Be consistent with index_url and package_version
* Add a test for checks that packages of this solver do not affect the inspected ones
* Reverse order of imports
* Log warning if found version does not match the one requested
* Show more debug messages to debug instrumented virtual environments
* Show more debug messages to debug instrumented virtual environments
* Log warning if found version does not match the one requested
* :pushpin: Automatic update of dependency thoth-common from 0.9.12 to 0.9.14
* :pushpin: Automatic update of dependency thoth-python from 0.6.3 to 0.6.4
* :pushpin: Automatic update of dependency pytest-cov from 2.7.1 to 2.8.1
* :pushpin: Automatic update of dependency pytest from 5.2.0 to 5.2.1
* :pushpin: Automatic update of dependency thoth-common from 0.9.11 to 0.9.12
* Adjust testsuite respecting key names
* Be backwards compatible with older versions of solver
* Log warning if the given package cannot be parsed
* Bump solver version
* Adjust testsuite to be backwards compatible
* Be backwards compatible with older release
* Add test for parsing extra and extras
* Remove responses from requirements
* Drop subgraph checks
* Update README file description
* Adjust testsuite accordingly
* Adjust how marker evaluation is shown in the output
* Update Pipfile.lock
* Add testsuite for new implementation
* Update README file to state current changes in data aggregation
* Aggregate package metadata for markers and extras
* :pushpin: Automatic update of dependency thoth-common from 0.9.10 to 0.9.11
* Add testsuite for new implementation
* Aggregate package metadata for markers and extras
* Update README file to state current changes in data aggregation
* Revert "WIP: Aggregate package metadata for markers and extras"
* Aggregate package metadata for markers and extras
* :pushpin: Automatic update of dependency thoth-analyzer from 0.1.3 to 0.1.4
* Fix duration calculation
* Add duration to Solver
* Fix gathering of hashes for packages which have different versions on PyPI
* Use only ubi based image in job
* :pushpin: Automatic update of dependency thoth-python from 0.6.2 to 0.6.3
* :pushpin: Automatic update of dependency thoth-analyzer from 0.1.2 to 0.1.3
* :pushpin: Automatic update of dependency thoth-common from 0.9.9 to 0.9.10
* :pushpin: Automatic update of dependency thoth-common from 0.9.8 to 0.9.9
* Implicitly turn off subgraph checks if transitive will not be resolved
* Fix issue when fetcher kwargs are set to None
* :pushpin: Automatic update of dependency thoth-python from 0.6.1 to 0.6.2
* :pushpin: Automatic update of dependency virtualenv from 16.7.4 to 16.7.5
* :pushpin: Automatic update of dependency pip-tools from 4.0.0 to 4.1.0
* :pushpin: Automatic update of dependency virtualenv from 16.7.3 to 16.7.4
* Check if the given package is provided by index
* Perform backoff and fix connection only errors
* Correctly propagate fetcher kwargs
* :pushpin: Automatic update of dependency virtualenv from 16.7.2 to 16.7.3
* Increase memory requests due to OOM in the cluster
* Do sub-graph checks also on direct dependencies
* Be consistent with labels on solvers
* Change exception type to handle it
* Turn debugs into warnings
* Retry if client gets disconnected
* :pushpin: Automatic update of dependency thoth-common from 0.9.7 to 0.9.8
* :pushpin: Automatic update of dependency thoth-common from 0.9.6 to 0.9.7
* :pushpin: Automatic update of dependency thoth-python from 0.6.0 to 0.6.1
* :pushpin: Automatic update of dependency thoth-common from 0.9.5 to 0.9.6
* :pushpin: Automatic update of dependency virtualenv from 16.7.1 to 16.7.2
* :pushpin: Automatic update of dependency pip-tools from 3.9.0 to 4.0.0
* :pushpin: Automatic update of dependency virtualenv from 16.7.0 to 16.7.1
* :pushpin: Automatic update of dependency thoth-common from 0.9.4 to 0.9.5
* :pushpin: Automatic update of dependency thoth-python from 0.5.0 to 0.6.0
* :pushpin: Automatic update of dependency virtualenv from 16.6.2 to 16.7.0
* Release of version 1.2.2
* Be more precise with the exception raised
* :pushpin: Automatic update of dependency thoth-common from 0.9.3 to 0.9.4
* :pushpin: Automatic update of dependency pip-tools from 3.8.0 to 3.9.0
* Release of version 1.2.1
* Include MANIFEST.in file
* :pushpin: Automatic update of dependency virtualenv from 16.6.1 to 16.6.2
* :pushpin: Automatic update of dependency thoth-common from 0.9.2 to 0.9.3
* :pushpin: Automatic update of dependency thoth-common from 0.9.1 to 0.9.2
* :pushpin: Automatic update of dependency thoth-common from 0.9.0 to 0.9.1
* Release of version 1.2.0
* Configure pod ttl to be same as job ttl
* Quote package name in case of no releases found
* Fix permission denied when installing to venv
* :pushpin: Automatic update of dependency thoth-common from 0.8.11 to 0.9.0
* Add build trigger with generic webhook
* :pushpin: Automatic update of dependency virtualenv from 16.6.0 to 16.6.1
* :pushpin: Automatic update of dependency pip-tools from 3.7.0 to 3.8.0
* :pushpin: Automatic update of dependency thoth-common from 0.8.7 to 0.8.11
* Fix component label so that solver names are correctly parsed
* Solver is a standalone container, not sidecar
* Check if the given package in the given version was solved by specific solver
* modify link
* Retry if subgraph check API does not respond with correct status code
* :sparkles: a little bit more verbosity
* :bug: we need to provide a pull secret
* :sparkles: using some proper labels
* :green_heart: fixed a major yaml lint bear error
* :sparkles: added solver for UBI8-Py36
* :pushpin: Automatic update of dependency requests from 2.21.0 to 2.22.0
* :pushpin: Automatic update of dependency virtualenv from 16.5.0 to 16.6.0
* :pushpin: Automatic update of dependency thoth-common from 0.8.5 to 0.8.7
* :pushpin: Automatic update of dependency pip-tools from 3.6.1 to 3.7.0
* Minor fix to display correct release in title of docs html
* :pushpin: Automatic update of dependency pip-tools from 3.6.0 to 3.6.1
* :pushpin: Automatic update of dependency virtualenv from 16.4.3 to 16.5.0
* :pushpin: Automatic update of dependency autopep8 from 1.4.3 to 1.4.4
* :pushpin: Automatic update of dependency thoth-common from 0.8.4 to 0.8.5
* Automatic update of dependency thoth-common from 0.8.3 to 0.8.4
* Automatic update of dependency thoth-common from 0.8.2 to 0.8.3
* Automatic update of dependency pip-tools from 3.5.0 to 3.6.0
* Automatic update of dependency thoth-common from 0.8.1 to 0.8.2
* added the registry, why the hell the jobs needs that...
* :sparkles: added ImageStream namespace and tag
* Automatic update of dependency thoth-python from 0.4.6 to 0.5.0
* Add Thoth's configuration file
* Automatic update of dependency thoth-common from 0.7.1 to 0.8.1
* Use Sphinx for documentation
* Automatic update of dependency pip-tools from 3.4.0 to 3.5.0
* Minor fixes in implementation
* Install thoth-python, use Python3.6 in virtual env
* Fix logical error due to which we did not resolve transitive deps locally
* Automatic update of dependency virtualenv from 16.4.1 to 16.4.3
* Cleanup successful solver jobs after 2 hours
* Restart solver run if anything goes wrong
* Automatic update of dependency virtualenv from 16.4.0 to 16.4.1
* Automatic update of dependency pip-tools from 3.3.2 to 3.4.0
* using the correct name now
* added f28, f29 solvers, relocked pipfile
* Automatic update of dependency thoth-common from 0.6.0 to 0.7.1
* Automatic update of dependency thoth-analyzer from 0.1.0 to 0.1.2
* Automatic update of dependency pip-tools from 3.2.0 to 3.3.2
* Automatic update of dependency virtualenv from 16.2.0 to 16.4.0
* It's already 2019
* Automatic update of dependency pipdeptree from 0.13.1 to 0.13.2
* Automatic update of dependency thoth-common from 0.5.0 to 0.6.0
* Format using black
* Add venv to ignore file for local runs
* Fix debug message printed
* Use solver naming convention
* Pass solver job identifier for workload operator
* Update job-template.yaml
* Automatic update of dependency virtualenv from 16.1.0 to 16.2.0
* Automatic update of dependency pip-tools from 3.1.0 to 3.2.0
* Automatic update of dependency requests from 2.20.1 to 2.21.0
* hotfixed coala error
* Automatic update of dependency thoth-common from 0.4.6 to 0.5.0
* Graph sync operator was renamed
* Mark solver for cleanup
* Register solver for operator handling
* Introduce subgraph check API parameter in template
* Add check for subgraph checks
* Restore correctly environment in case of any exception
* Support pip in version 10 and above
* fixed some coala errors, and ignoring the rest
* fixed coala errors, and a little bit of black reformating
* fixed coala errors
* added a pyproject.toml to keep black happy
* Incorporate index url in releases fetcher
* Automatic update of dependency thoth-common from 0.4.5 to 0.4.6
* Adjust error report message
* Increase liveness probes for now
* Increase memory limits to reduce OOM kills
* Install pipdeptree before obtaining env info
* Remove duplicit definition
* Adjust solver output to be compatible with sync
* Enable trusted hosts by default
* Do not forget thoth-python dependency
* Fix setup.py packages
* fixed the component value
* updated coala file and using the thoth zuul jobs
* added Fedora 28 and removed Fedora 26
* moved these files required for local hacking/building
* Introduce THOTH_SOLVER_INDEXES variable in template
* Accept indexes as a comma separated values
* Unresolvable packages have also index assigned
* Source can be derived from solver
* Restructure python solver module
* Cross-index solving with hashes gathering
* Add long description for PyPI
* Automatic update of dependency thoth-common from 0.4.4 to 0.4.5
* Automatic update of dependency thoth-common from 0.4.3 to 0.4.4
* Automatic update of dependency thoth-common from 0.4.2 to 0.4.3
* Automatic update of dependency thoth-common from 0.4.1 to 0.4.2
* Automatic update of dependency thoth-common from 0.4.0 to 0.4.1
* Automatic update of dependency autopep8 from 1.4.2 to 1.4.3
* if error is not fatal, loglevel has been replaced with warning
* Do not print matching solved packages on new line
* Automatic update of dependency thoth-common from 0.3.16 to 0.4.0
* Automatic update of dependency virtualenv from 16.0.0 to 16.1.0
* Automatic update of dependency thoth-common from 0.3.15 to 0.3.16
* Automatic update of dependency thoth-common from 0.3.14 to 0.3.15
* Fix splitting packages in requirements
* Automatic update of dependency thoth-common from 0.3.13 to 0.3.14
* Automatic update of dependency thoth-common from 0.3.12 to 0.3.13
* fixed a typo
* Automatic update of dependency autopep8 from 1.4.1 to 1.4.2
* Automatic update of dependency thoth-common from 0.3.11 to 0.3.12
* Automatic update of dependency autopep8 from 1.4 to 1.4.1
* Automatic update of dependency thoth-analyzer from 0.0.7 to 0.1.0
* fixed coala errors
* removed f26 part, added sentry
* Automatic update of dependency thoth-common from 0.3.10 to 0.3.11
* Automatic update of dependency thoth-common from 0.3.9 to 0.3.10
* Automatic update of dependency thoth-common from 0.3.8 to 0.3.9
* Automatic update of dependency thoth-common from 0.3.7 to 0.3.8
* Automatic update of dependency thoth-common from 0.3.6 to 0.3.7
* Automatic update of dependency pip-tools from 3.0.0 to 3.1.0
* Automatic update of dependency pipdeptree from 0.13.0 to 0.13.1
* Rename template to reflect its semantics
* Move from Pods to Jobs
* Automatic update of dependency thoth-common from 0.3.5 to 0.3.6
* Be more verbose about what is going on
* Update README file
* Automatic update of dependency thoth-common from 0.3.2 to 0.3.5
* Automatic update of dependency thoth-common from 0.3.1 to 0.3.2
* Automatic update of dependency click from 6.7 to 7.0
* Automatic update of dependency pip-tools from 2.0.2 to 3.0.0
* Automatic update of dependency thoth-common from 0.3.0 to 0.3.1
* Adjust .gitignore
* Fix restart policy configuration
* Automatic update of dependency thoth-common from 0.2.7 to 0.3.0
* Automatic update of dependency thoth-common from 0.2.6 to 0.2.7
* Automatic update of dependency thoth-common from 0.2.5 to 0.2.6
* Automatic update of dependency autopep8 from 1.3.5 to 1.4
* Automatic update of dependency thoth-common from 0.2.4 to 0.2.5
* Automatic update of dependency thoth-common from 0.2.3 to 0.2.4
* put it in zuul's core queue
* Automatic update of dependency thoth-common from 0.2.2 to 0.2.3
* Increase memory for builds of f26 solver
* Remove Travis CI completely
* State all solvers and template parameters
* Be consistent with naming
* Update requirements.txt respecting requirements in Pipfile
* Automatic update of dependency thoth-common from 0.2.1 to 0.2.2
* Release of version 1.1.0
* Add resources needed for build
* Adjust template labels
* Pod template fix
* Introduce solver pod template
* Automatic update of dependency thoth-common from 0.2.0 to 0.2.1
* Automatic update of dependency thoth-common from 0.2.0 to 0.2.1
* Automatic update of dependency thoth-common from 0.2.0 to 0.2.1
* Initial dependency lock
* adding all the files we need to zuul. fixing coala errors. closes https://github.com/thoth-station/solver/issues/44
* Delete Pipfile.lock for relocking dependencies
* Automatic update of dependency thoth-common from 0.0.9 to 0.1.0
* /usr/bin/python3 is being removed
* Automatic update of dependency thoth-analyzer from 0.0.6 to 0.0.7
* Automatic update of dependency thoth-common from 0.0.8 to 0.0.9
* Automatic update of dependency pipdeptree from 0.12.1 to 0.13.0
* Automatic update of dependency thoth-common from 0.0.7 to 0.0.8
* Automatic update of dependency thoth-common from 0.0.6 to 0.0.7
* Automatic update of dependency thoth-analyzer from 0.0.5 to 0.0.6
* Automatic update of dependency pip-tools from 2.0.1 to 2.0.2
* Automatic update of dependency thoth-common from 0.0.3 to 0.0.6
* Automatic update of dependency virtualenv from 15.2.0 to 16.0.0
* Do not restrict Thoth packages
* Remove pip from Pipfile
* Update thoth-common for rsyslog logging
* Remove dependencies.yml
* Use coala for code checks
* added templates so that they can be used by playbooks or CI
* we are not using it right now
* Keep track of unparsed packages
* Simplify error handling
* Be more verbose about parsed requirement
* Mark packages that couldn't be found as unresolvable
* Mark packages that couldn't be found as unresolvable
* Add license headers
* Use proper LICENSE file
* Use proper license in setup.py
* adding the OWNERS file
* Use Thoth's common logging
* Version 1.0.2
* Fix wrong string format
* Respect transition to a new org
* Version 1.0.1
* Quote user's input
* Fix missing requirements
* Do not compute hashes for now
* Version 1.0.0
* Remove unused imports
* Reduce with count
* Specify user and workdir explicitly
* Do not use user flag, run in venv instead
* Add pip-compile logic
* Fix env variable name
* State only direct dependencies in requirements.txt
* Version 1.0.0rc2
* Update analyzer version
* Do not use zip files
* Create initial dependencies.yml config
* Version 1.0.0rc1
* Create thoth.solver package
* Update requirements to reflect current state
* Use thoth.analyzer module
* Remove unused utils module
* Helper tempdir is not used anymore
* Build images in Travis CI
* Adjust package name
* Fix issue where transitive dependencies didn't have resolved versions
* Let a user write to directory when run on OpenShift
* Store resolved versions for the given package
* Rename key to reflect its semantics
* Do not run solver under root
* Log resolved versions of a package
* Do not store installed version info of dependencies
* Check hashes of artifacts
* Fix wrong debug report
* Unify errors structure with actual results
* Packages in the initial listing were also seen
* Restore environment after installation
* Do not install deps into virtualenv
* Exclude transitive dependencies if requested
* Do not add packages with no name
* Fix wrong module call
* Report endpoint response
* Fix split of envvar
* Requirements should be accepted via env var in raw format
* Add dockerfiles
* Accept parameters via envvars
* Adjust README file
* Fix referencing wrong attributes
* Be able to submit results to a remote API
* Implement dependency exploring
* Remove unused import
* Use PypiDependency solver to solve requirement specification
* Be consistent with the parser output
* Fix empty line requirement
* Add metadata to computed results
* Provide a way to run thoth-solver in a container
* Make thoth-solver installable
* Add missing requirements
* We do not care about actual package names returned
* Add README file
* Introduce exclude packages option
* Initial implementation import

## Release 1.5.0 (2020-01-08T18:08:54)
* :pushpin: Automatic update of dependency thoth-python from 0.8.0 to 0.9.0
* :pushpin: Automatic update of dependency packaging from 19.2 to 20.0
* Format using black, add ignore comments for dict specific types
* Move package parsing logic to thoth-python
* :pushpin: Automatic update of dependency thoth-common from 0.9.22 to 0.9.23
* :pushpin: Automatic update of dependency thoth-python from 0.7.1 to 0.8.0
* :pushpin: Automatic update of dependency pytest-timeout from 1.3.3 to 1.3.4
* Increase memory requirements for solvers
* Decrease liveness probe to avoid long-living jobs
* Happy new year!
* Use arbitrary equality for solvers
* Solver Fedora 31 with Python 3.7
* :pushpin: Automatic update of dependency mypy from 0.760 to 0.761
* :pushpin: Automatic update of dependency mypy from 0.750 to 0.760
* :pushpin: Automatic update of dependency virtualenv from 16.7.8 to 16.7.9
* :pushpin: Automatic update of dependency pytest from 5.3.1 to 5.3.2
* :pushpin: Automatic update of dependency thoth-common from 0.9.21 to 0.9.22
* :pushpin: Automatic update of dependency importlib-metadata from 1.2.0 to 1.3.0
* Do not install docs
* Bump version in templates
* Adjust image streams
* Build Fedora 30 and 31 with Python 3.8
* Use Python 3.8 instead of Python 3.7
* :pushpin: Automatic update of dependency thoth-analyzer from 0.1.6 to 0.1.7
* Add Thamos documentation
* Point documentation to other libraries
* Add Google Analytics
* changed the line lenght a little
* fixed two typos
* some better formating
* using the garbage collector to delete successfull workflows 🚚
* :green_heart: removed the debug code
* :green_heart: added coverage saving as xml
* :green_heart: fixed three D300
* this is an array not an object
* added THOTH_FORCE_SYNC
* :sparkles: added the OpenShift Template for the Argo Workflow
* all solver jobs for production and stage cluster

## Release 1.5.1 (2020-03-30T12:29:05)
* :pushpin: Automatic update of dependency importlib-metadata from 1.5.0 to 1.6.0
* Add .github files
* Fix detection of libraries that are shared with thoth-solver itself
* Missing paranthesis prevent sync in Ceph
* Adjust strings
* Add env variables to graph-sync
* remove jobs from template
* Remove default values
* Add correct image url with parameters
* Introduce variables for storage on Ceph
* Add solvers
* Adjust template for solvers
* :pushpin: Automatic update of dependency thoth-common from 0.10.8 to 0.10.9
* :pushpin: Automatic update of dependency thoth-common from 0.10.7 to 0.10.8
* :pushpin: Automatic update of dependency pytest-mypy from 0.4.2 to 0.5.0
* :pushpin: Automatic update of dependency requests from 2.22.0 to 2.23.0
* Use solver-workload-operator name for stage solver jobs
* :pushpin: Automatic update of dependency thoth-common from 0.10.6 to 0.10.7
* :pushpin: Automatic update of dependency thoth-common from 0.10.5 to 0.10.6
* Update .thoth.yaml
* :pushpin: Automatic update of dependency thoth-common from 0.10.4 to 0.10.5
* :pushpin: Automatic update of dependency thoth-common from 0.10.3 to 0.10.4
* :pushpin: Automatic update of dependency thoth-common from 0.10.2 to 0.10.3
* Adjust name and volume in templates
* :pushpin: Automatic update of dependency thoth-common from 0.10.1 to 0.10.2
* :pushpin: Automatic update of dependency thoth-common from 0.10.0 to 0.10.1
* :pushpin: Automatic update of dependency pytest from 5.3.4 to 5.3.5
* :pushpin: Automatic update of dependency thoth-common from 0.9.31 to 0.10.0
* :pushpin: Automatic update of dependency importlib-metadata from 1.4.0 to 1.5.0
* Add parameter to sync only on graph database
* :pushpin: Automatic update of dependency thoth-common from 0.9.30 to 0.9.31
* :pushpin: Automatic update of dependency thoth-common from 0.9.29 to 0.9.30
* :pushpin: Automatic update of dependency packaging from 20.0 to 20.1
* :pushpin: Automatic update of dependency pytest from 5.3.3 to 5.3.4
* :pushpin: Automatic update of dependency thoth-common from 0.9.28 to 0.9.29
* :pushpin: Automatic update of dependency autopep8 from 1.4.4 to 1.5
* Update template name
* :pushpin: Automatic update of dependency pytest from 5.3.2 to 5.3.3
* Standardize solver name variable
* Rename solver-rhel-8.0 to solver-rhel-8
* :pushpin: Automatic update of dependency thoth-common from 0.9.27 to 0.9.28
* standardize templates
* Add workflows templates
* :pushpin: Automatic update of dependency thoth-common from 0.9.26 to 0.9.27
* :pushpin: Automatic update of dependency thoth-analyzer from 0.1.7 to 0.1.8
* :pushpin: Automatic update of dependency thoth-common from 0.9.25 to 0.9.26
* :pushpin: Automatic update of dependency thoth-common from 0.9.24 to 0.9.25
* :pushpin: Automatic update of dependency importlib-metadata from 1.3.0 to 1.4.0
* :pushpin: Automatic update of dependency thoth-common from 0.9.23 to 0.9.24
* :pushpin: Automatic update of dependency thoth-python from 0.9.0 to 0.9.1

## Release 1.5.2 (2020-04-21T10:17:29)
* :pushpin: Automatic update of dependency autopep8 from 1.5.1 to 1.5.2
* :pushpin: Automatic update of dependency thoth-python from 0.9.1 to 0.9.2
* :pushpin: Automatic update of dependency virtualenv from 20.0.17 to 20.0.18
* :pushpin: Automatic update of dependency virtualenv from 20.0.16 to 20.0.17
* :pushpin: Automatic update of dependency thoth-common from 0.12.8 to 0.12.9
* consistency in using secrets
* :pushpin: Automatic update of dependency thoth-common from 0.12.7 to 0.12.8
* Give solver 30 minutes to compute results
* :pushpin: Automatic update of dependency thoth-common from 0.12.6 to 0.12.7
* :pushpin: Automatic update of dependency autopep8 from 1.5 to 1.5.1
* Setup workflow TTL strategy to reduce preassure causing OOM
* Fix when no output was produced and JSON flag was set to true
* :pushpin: Automatic update of dependency pytest-mypy from 0.6.0 to 0.6.1
* :pushpin: Automatic update of dependency virtualenv from 20.0.15 to 20.0.16
* Use RHEL 8
* More resources for bigger stacks
* :pushpin: Automatic update of dependency thoth-common from 0.12.5 to 0.12.6
* :pushpin: Automatic update of dependency thoth-common from 0.12.4 to 0.12.5
* :pushpin: Automatic update of dependency pytest-mypy from 0.5.0 to 0.6.0
* :pushpin: Automatic update of dependency thoth-common from 0.10.11 to 0.12.4
* :pushpin: Automatic update of dependency virtualenv from 20.0.10 to 20.0.15
* Remove hack/ as it is no longer needed
* :pushpin: Automatic update of dependency pytest from 5.4.0 to 5.4.1

## Release 1.6.0 (2020-07-30T18:17:09)
* :alien: support solver image build with ci pipeline
* :mega: thoth solver dockerfiles (#597)
* :pushpin: Automatic update of dependency pytest from 6.0.0 to 6.0.1 (#596)
* :pushpin: Automatic update of dependency virtualenv from 20.0.27 to 20.0.28 (#595)
* Fix mypy errors for duplicate imports
* :pushpin: Automatic update of dependency pytest from 5.4.3 to 6.0.0
* :pushpin: Automatic update of dependency thoth-common from 0.14.2 to 0.16.0
* Make thoth-solver work with Python 3.8+
* :pushpin: Automatic update of dependency pytest-timeout from 1.4.1 to 1.4.2 (#583)
* :pushpin: Automatic update of dependency virtualenv from 20.0.26 to 20.0.27 (#582)
* :pushpin: Automatic update of dependency thoth-common from 0.14.1 to 0.14.2 (#581)
* Add environment marker for importlib-metadata (#585)
* :pushpin: Automatic update of dependency mypy from 0.781 to 0.782
* :pushpin: Automatic update of dependency virtualenv from 20.0.25 to 20.0.26 (#578)
* Remove templates that are handled by thoth-application (#577)
* :pushpin: Automatic update of dependency thoth-common from 0.13.12 to 0.14.1 (#576)
* Fixed precommit errors (#575)
* Update OWNERS
* :pushpin: Automatic update of dependency virtualenv from 20.0.24 to 20.0.25
* :pushpin: Automatic update of dependency importlib-metadata from 1.6.1 to 1.7.0
* :pushpin: Automatic update of dependency virtualenv from 20.0.21 to 20.0.24
* :pushpin: Automatic update of dependency thoth-python from 0.9.2 to 0.10.0
* :pushpin: Automatic update of dependency thoth-common from 0.13.8 to 0.13.12
* :pushpin: Automatic update of dependency mypy from 0.780 to 0.781
* :pushpin: Automatic update of dependency pytest-cov from 2.9.0 to 2.10.0
* :pushpin: Automatic update of dependency pipdeptree from 0.13.2 to 1.0.0
* :pushpin: Automatic update of dependency requests from 2.23.0 to 2.24.0
* :pushpin: Automatic update of dependency pytest-timeout from 1.3.4 to 1.4.1
* Keep workflows for SLI
* :pushpin: Automatic update of dependency importlib-metadata from 1.6.0 to 1.6.1
* :pushpin: Automatic update of dependency mypy from 0.770 to 0.780
* :pushpin: Automatic update of dependency pytest from 5.4.2 to 5.4.3
* added a 'tekton trigger tag_release pipeline issue'
* :pushpin: Automatic update of dependency autopep8 from 1.5.2 to 1.5.3
* :pushpin: Automatic update of dependency thoth-common from 0.13.7 to 0.13.8
* introduce ttl for workflow
* introduce logic for gc and workflows life
* :pushpin: Automatic update of dependency thoth-common from 0.13.6 to 0.13.7
* :pushpin: Automatic update of dependency pytest-cov from 2.8.1 to 2.9.0
* :pushpin: Automatic update of dependency thoth-common from 0.13.5 to 0.13.6
* :pushpin: Automatic update of dependency thoth-common from 0.13.4 to 0.13.5
* :pushpin: Automatic update of dependency thoth-common from 0.13.3 to 0.13.4
* :pushpin: Automatic update of dependency virtualenv from 20.0.20 to 20.0.21
* :pushpin: Automatic update of dependency packaging from 20.3 to 20.4
* :bug: :fire: hotfix for the BC
* :arrow_up: relocked dependencies due to jsonformatter
* a lot of reformatting by black and pre-commit
* added Fedora32 Python 3.8 and 3.7 solver buildconfigs
* :pushpin: Automatic update of dependency thoth-common from 0.13.1 to 0.13.2
* :pushpin: Automatic update of dependency thoth-common from 0.13.0 to 0.13.1
* :pushpin: Automatic update of dependency click from 7.1.1 to 7.1.2
* :pushpin: Automatic update of dependency pytest-mypy from 0.6.1 to 0.6.2
* :pushpin: Automatic update of dependency thoth-common from 0.12.10 to 0.13.0
* :pushpin: Automatic update of dependency thoth-common from 0.12.9 to 0.12.10
* Propagate information about platform from solver run
* Add workflow timeout to avoid solver running for many hours and stopping other pending solvers to start

## Release 1.6.1 (2020-09-09T12:39:54)
### Features
* Add a link to TDS article
### Improvements
* Do not use environment marker for importlib-metadata
### Automatic Updates
* :pushpin: Automatic update of dependency pytest-venv from 0.2 to 0.2.1 (#606)
* :pushpin: Automatic update of dependency virtualenv from 20.0.29 to 20.0.30 (#605)
* :pushpin: Automatic update of dependency autopep8 from 1.5.3 to 1.5.4 (#604)
* :pushpin: Automatic update of dependency virtualenv from 20.0.28 to 20.0.29 (#602)

## Release 1.6.2 (2020-09-10T06:47:59)
### Features
* Add version in info log
### Improvements
* Correct typo

## Release 1.6.3 (2020-11-16T10:49:35)
### Features
* :guardsman: update maintainers
* :turtle: solver based on ubi8 and python38 (#639)
* Extend README with dependency info
### Automatic Updates
* :pushpin: Automatic update of dependency requests from 2.24.0 to 2.25.0 (#645)
* :pushpin: Automatic update of dependency requests from 2.24.0 to 2.25.0 (#640)
* :pushpin: Automatic update of dependency thoth-common from 0.20.2 to 0.20.4 (#641)
* :pushpin: Automatic update of dependency pytest from 6.1.1 to 6.1.2 (#642)
* :pushpin: Automatic update of dependency pytest-mypy from 0.7.0 to 0.8.0 (#643)
* :pushpin: Automatic update of dependency mypy from 0.782 to 0.790 (#638)
* :pushpin: Automatic update of dependency mypy from 0.782 to 0.790 (#637)
* :pushpin: Automatic update of dependency virtualenv from 20.0.33 to 20.1.0 (#636)
* :pushpin: Automatic update of dependency thoth-common from 0.20.0 to 0.20.2 (#635)
* :pushpin: Automatic update of dependency virtualenv from 20.0.31 to 20.0.33 (#632)
* :pushpin: Automatic update of dependency virtualenv from 20.0.31 to 20.0.33 (#631)
* :pushpin: Automatic update of dependency virtualenv from 20.0.31 to 20.0.33 (#630)
* :pushpin: Automatic update of dependency pytest from 6.0.2 to 6.1.1 (#629)
* :pushpin: Automatic update of dependency thoth-python from 0.10.1 to 0.10.2 (#628)
* :pushpin: Automatic update of dependency virtualenv from 20.0.31 to 20.0.33 (#627)
* :pushpin: Automatic update of dependency thoth-python from 0.10.1 to 0.10.2 (#626)
* :pushpin: Automatic update of dependency thoth-common from 0.19.0 to 0.20.0 (#625)
* :pushpin: Automatic update of dependency importlib-metadata from 1.7.0 to 2.0.0 (#624)
* :pushpin: Automatic update of dependency pytest from 6.0.1 to 6.0.2
* :pushpin: Automatic update of dependency thoth-common from 0.18.3 to 0.19.0
* :pushpin: Automatic update of dependency thoth-common from 0.17.3 to 0.18.3

## Release 1.7.0 (2021-02-08T18:14:57)
### Features
* Adjust tests to cover pre-releases correctly
* Explicitly turn on pre-releases in Python dependency parser
* Remove old Fedora S2I images
* :arrow_up: Automatic update of dependencies by kebechet. (#664)
* Adjust links and link to solvers built on quay (#656)
* :arrow_up: Automatic update of dependencies by kebechet. (#653)
* update .thoth.yaml (#651)
* port to python 38 (#650)
### Improvements
* Update README and remove old build section
* Add bits needed for s2i integration (#662)
### Non-functional
* Add pull request template for the repo (#658)

## Release 1.7.1 (2021-03-04T19:36:46)
### Features
* :arrow_up: Automatic update of dependencies by Kebechet (#680)
* Fix CI failures (#679)
* Execute solvers with app script to call solver python cli
* :arrow_up: Automatic update of dependencies by Kebechet (#675)
* :arrow_up: Automatic update of dependencies by Kebechet (#674)
* update the base image with new version for solvers
* update aicoe-ci configuration to support overlays build (#673)
* Run pytest with Python 3.8 (#672)

## Release 1.7.2 (2021-03-05T16:38:34)
### Features
* Skip thoth-solver in the environment packages report

## Release 1.8.0 (2021-05-06T13:35:35)
### Features
* Provide an ability to limit output
* :arrow_up: Automatic update of dependencies by Kebechet (#695)
* Address review comments
* Improvements to docs
* :arrow_up: Automatic update of dependencies by Kebechet (#693)

## Release 1.9.0 (2021-05-24T20:41:38)
### Features
* :arrow_up: Automatic update of dependencies by Kebechet (#705)
* Compute packages available in analyzed Python package release
* Metadata now gather also description (#707)
* :hatched_chick: update the prow resource limits
* :arrow_up: remove resources spec so that namespace defaults are used
* :arrow_up: Automatic update of dependencies by Kebechet (#698)
* Use thoth.solver logger in the CLI setup
### Improvements
* Remove unused ignore comment
### Other
* Raise on exit code propagating a signal from operating system (#704)

## Release 1.10.0 (2021-06-03T18:56:18)
### Features
* :arrow_up: Automatic update of dependencies by Kebechet
* Update .thoth.yaml
* Update .aicoe-ci.yaml
* Add Fedora 34 based on Python 3.9 solver
* Remove unecessary whitespace (#710)

## Release 1.10.1 (2021-06-08T14:21:17)
### Features
* :panda_face: support solver fedora 34 python 3.9 with thoth services
* :arrow_up: Automatic update of dependencies by Kebechet

## Release 1.10.2 (2021-07-21T19:08:44)
### Features
* Add types-setuptools
* Fix import statement
* :arrow_up: Automatic update of dependencies by Kebechet
* :arrow_up: Automatic update of dependencies by Kebechet
* kebechet issue templates for ease trigger
* :arrow_up: Automatic update of dependencies by Kebechet (#724)
* :arrow_up: Automatic update of dependencies by Kebechet (#721)
* add priority/critical-urgent label to all bot related issue templates
* Adjust copyright notice in headers
* Remove Fedora 31 + Python 3.7 it went EOL
### Bug Fixes
* Import statement fix
