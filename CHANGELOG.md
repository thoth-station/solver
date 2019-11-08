
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

