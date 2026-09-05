SHELL := /bin/sh

PNPM ?= pnpm
NPM ?= npm
NPM_CACHE ?= $(CURDIR)/.npm-cache
TOKEN_NPMRC ?= $(CURDIR)/.npmrc.token
ifneq ($(strip $(NPM_TOKEN)),)
NPM_USERCONFIG ?= $(TOKEN_NPMRC)
else
NPM_USERCONFIG ?=
endif
ifdef NPM_USERCONFIG
NPM_RUN := npm_config_cache=$(NPM_CACHE) npm_config_userconfig=$(NPM_USERCONFIG) $(NPM)
else
NPM_RUN := npm_config_cache=$(NPM_CACHE) $(NPM)
endif
NPM_LOGIN_RUN := npm_config_cache=$(NPM_CACHE) $(NPM)
TAG ?= latest
PREID ?= beta
PRERELEASE_TAG ?= beta

.DEFAULT_GOAL := help

.PHONY: help install dev typecheck build check pack preflight clean \
	sync-github-public publish-readme \
	login login-legacy whoami publish publish-beta publish-current publish-current-beta \
	publish-dry-run publish-beta-dry-run \
	prepare-npm-auth check-clean check-npm-auth version-patch version-minor version-major version-beta \
	release release-patch release-minor release-major release-beta

help:
	@printf "%s\n" "Usage: make <target>"
	@printf "%s\n" ""
	@printf "%s\n" "Development:"
	@printf "  %-24s %s\n" "install" "Install dependencies with pnpm."
	@printf "  %-24s %s\n" "dev" "Start the development server or playground."
	@printf "  %-24s %s\n" "typecheck" "Run type checks."
	@printf "  %-24s %s\n" "build" "Build the package."
	@printf "  %-24s %s\n" "check" "Run typecheck and build."
	@printf "%s\n" ""
	@printf "%s\n" "Packaging:"
	@printf "  %-24s %s\n" "pack" "Run checks and create a local .tgz package."
	@printf "  %-24s %s\n" "preflight" "Alias of pack for release verification."
	@printf "  %-24s %s\n" "clean" "Remove dist and local .tgz packages."
	@printf "  %-24s %s\n" "sync-github-public" "Sync public README and demo images to GitHub only."
	@printf "  %-24s %s\n" "publish-readme" "Alias of sync-github-public."
	@printf "%s\n" ""
	@printf "%s\n" "Publishing:"
	@printf "  %-24s %s\n" "login" "Log in to npm."
	@printf "  %-24s %s\n" "login-legacy" "Log in to npm with username/password prompts."
	@printf "  %-24s %s\n" "whoami" "Show the active npm account. Uses NPM_TOKEN when set."
	@printf "  %-24s %s\n" "publish" "Use NPM_TOKEN when set, bump patch, then publish latest."
	@printf "  %-24s %s\n" "publish-beta" "Require a clean tree, bump prerelease, then publish prerelease tag."
	@printf "  %-24s %s\n" "publish-current" "Use NPM_TOKEN when set and publish the current version."
	@printf "  %-24s %s\n" "publish-current-beta" "Build and publish the current version with PRERELEASE_TAG=beta."
	@printf "  %-24s %s\n" "publish-dry-run" "Build and run npm publish --dry-run."
	@printf "  %-24s %s\n" "publish-beta-dry-run" "Build and run npm publish --dry-run with PRERELEASE_TAG=beta."
	@printf "%s\n" ""
	@printf "%s\n" "Versioned releases:"
	@printf "  %-24s %s\n" "release-patch" "Require a clean tree, bump patch, then publish latest."
	@printf "  %-24s %s\n" "release-minor" "Require a clean tree, bump minor, then publish latest."
	@printf "  %-24s %s\n" "release-major" "Require a clean tree, bump major, then publish latest."
	@printf "  %-24s %s\n" "release-beta" "Require a clean tree, bump prerelease, then publish prerelease tag."
	@printf "%s\n" ""
	@printf "%s\n" "Options:"
	@printf "  %-24s %s\n" "TAG=<dist-tag>" "Override npm dist-tag for publish targets."
	@printf "  %-24s %s\n" "PREID=<id>" "Override prerelease id for release-beta. Default: beta."
	@printf "  %-24s %s\n" "PRERELEASE_TAG=<tag>" "Override prerelease npm dist-tag. Default: beta."
	@printf "  %-24s %s\n" "NPM_CACHE=<path>" "Override npm cache path. Default: .npm-cache."
	@printf "  %-24s %s\n" "ALLOW_DIRTY=1" "Skip the clean worktree guard for versioned releases."

install:
	$(PNPM) install

dev:
	$(PNPM) dev

typecheck:
	$(PNPM) typecheck

build:
	$(PNPM) build

check:
	$(MAKE) typecheck
	$(MAKE) build

pack:
	$(MAKE) check
	$(PNPM) pack

preflight: pack

clean:
	rm -rf dist *.tgz

sync-github-public:
	bash deploy/release/sync-github-public

publish-readme: sync-github-public

login:
	$(NPM_LOGIN_RUN) login

login-legacy:
	$(NPM_LOGIN_RUN) login --auth-type=legacy --registry=https://registry.npmjs.org/

whoami: prepare-npm-auth
	$(NPM_RUN) whoami

prepare-npm-auth:
	@if [ -n "$$NPM_TOKEN" ]; then \
		printf "%s\n" '//registry.npmjs.org/:_authToken=$${NPM_TOKEN}' > "$(TOKEN_NPMRC)"; \
	fi

publish:
	$(MAKE) release-patch

publish-beta:
	$(MAKE) release-beta

publish-current:
	$(MAKE) check-npm-auth
	$(MAKE) check
	$(NPM_RUN) publish --access public --tag $(TAG)
	$(MAKE) clean

publish-current-beta:
	$(MAKE) publish-current TAG=$(PRERELEASE_TAG)

publish-dry-run: prepare-npm-auth check
	$(NPM_RUN) publish --access public --tag $(TAG) --dry-run

publish-beta-dry-run:
	$(MAKE) publish-dry-run TAG=$(PRERELEASE_TAG)

check-clean:
	@if [ "$(ALLOW_DIRTY)" != "1" ] && [ -n "$$(git status --short)" ]; then \
		printf "%s\n" "Working tree is not clean. Commit/stash changes first, or rerun with ALLOW_DIRTY=1."; \
		git status --short; \
		exit 1; \
	fi

check-npm-auth: prepare-npm-auth
	@if ! $(NPM_RUN) whoami >/dev/null 2>&1; then \
		printf "%s\n" "npm auth is invalid. If using a token, export NPM_TOKEN and run 'make whoami'. Otherwise run 'make login' or 'make login-legacy'. If the version was already bumped, retry with 'make publish-current'."; \
		exit 1; \
	fi

version-patch:
	$(NPM_RUN) version patch --no-git-tag-version

version-minor:
	$(NPM_RUN) version minor --no-git-tag-version

version-major:
	$(NPM_RUN) version major --no-git-tag-version

version-beta:
	$(NPM_RUN) version prerelease --preid $(PREID) --no-git-tag-version

release:
	@printf "%s\n" "Choose one of: make release-patch, make release-minor, make release-major, make release-beta"
	@exit 1

release-patch:
	$(MAKE) check-clean
	$(MAKE) check-npm-auth
	$(MAKE) version-patch
	$(MAKE) publish-current TAG=latest

release-minor:
	$(MAKE) check-clean
	$(MAKE) check-npm-auth
	$(MAKE) version-minor
	$(MAKE) publish-current TAG=latest

release-major:
	$(MAKE) check-clean
	$(MAKE) check-npm-auth
	$(MAKE) version-major
	$(MAKE) publish-current TAG=latest

release-beta:
	$(MAKE) check-clean
	$(MAKE) check-npm-auth
	$(MAKE) version-beta PREID=$(PREID)
	$(MAKE) publish-current TAG=$(PRERELEASE_TAG)
