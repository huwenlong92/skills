# 合并到目标项目现有 Makefile；禁止覆盖已有目标。
CF_TARGET ?=
CFOPS = python3 .sdkit/cloudflare/cfops.py
.PHONY: cf-check cf-build cf-preview cf-deploy cf-verify
cf-check:
	$(CFOPS) check --target "$(CF_TARGET)"
cf-build:
	$(CFOPS) build --target "$(CF_TARGET)"
cf-preview:
	$(CFOPS) preview --target "$(CF_TARGET)"
# deploy 自行构建；仅用户明确要求写入时设置 CF_WRITE=1。
cf-deploy:
	@test "$(CF_WRITE)" = 1
	$(CFOPS) deploy --target "$(CF_TARGET)" --expected-sha "$(RELEASE_SHA)" --write
cf-verify:
	$(CFOPS) verify --target "$(CF_TARGET)" --origin "$(CF_ORIGIN)"
