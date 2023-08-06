# Bindings

This repository attempts to automate the release process of Stripe API language
bindings.

## Overview

These are the languages with an automated release:

* https://github.com/stripe/stripe-java
* https://github.com/stripe/stripe-php
* https://github.com/stripe/stripe-node
* https://github.com/stripe/stripe-ruby
* https://github.com/stripe/stripe-python

## Prerequisites

Most bindings releases require credentials found in `~/.stripe2`. See [this
installation guide][stripe2] if you don't have that set-up already.

You'll also need to have the repository for the language you're trying to
release cloned to `~/stripe` before continuing.

## Basic Usage

Release a new binding version:

    bin/upload_bindings --all 1.28.0 python

If something fails during one of the latter steps like uploading to a third
party package manager, the "finalize" step can be re-run for the current
version of a binding:

    bin/upload_bindings --finalize python

You can also release to code.stripe.com with Henson normally:

    henson deploy --prod bindings-srv

### Generating 

The project also contains a script that allows a new CA bundle to be generated
for use with our various bindings:

    bin/generate_ca_certificates

## Language-specific Instructions

Unfortunately due to language complexities and varying package ownership
schemes across ecosystems, not all bindings releases will work out of the box.
This section describes any additional setup that each language may need (and is
not yet complete).

### Go

The Go bindings should be located in `$GOPATH` instead of in the normal
`~/stripe` (this is due to convention in how Go projects are developed). Make
sure that this command works for you:

    go get -u github.com/stripe/stripe-go

### Java

Bindings are maintained on code.stripe.com and Nexus.

The Nexus credentials in `~/.stripe2` must currently be symlinked to your own
home directory due to limitations in Maven:

    mkdir -p ~/.m2
    ln -s ~/.stripe2/.m2/settings.xml ~/.m2

### Node

Bindings are maintained on code.stripe.com and [NPM][npm].

You need to have an NPM account and be registered as an owner for the `stripe`
package. A current owner can do this for you like so:

    npm owner add <username> stripe

### PHP

Bindings are maintained on code.stripe.com and Packagist.

Packagist automatically picks up on git tags, and has no additional
credentials, so no additional steps are required.

### Python

Bindings are maintained on code.stripe.com and PyPi.

You'll need Python 2 and 3. On OSX (for example), those can be installed with
something like this:

    brew install python python3

You'll also need `setuptools`:

    pip install --upgrade setuptools

Make sure that you have credentials for PyPi (you may need to ask someone for
access if you don't have it already):

    fetch-password pypi > ~/.stripe2/.pypirc

After fetching those credentails, you will have to edit the file to add a
`[server-login]` header so that it looks like:

    [server-login]
    Username: stripe
    Password: XXX

### Ruby

An API key for Rubygems comes with the `~/.stripe2` directory.

If you just cloned down a `~/.stripe2` though, you may need to fix permissions
before Rubygems allows you to push:

    chmod 600 /Users/brandur/.stripe2/.gem/credentials

[npm]: https://www.npmjs.com/
[stripe2]: https://hackpad.corp.stripe.com/9gAOKCtGBvX
