# 用法：make package <skill-name>
# 示例：make package leap-slide

DIST_DIR ?= dist
ACTIONS := package list verify clean help
SKILL_GOALS := $(filter-out $(ACTIONS),$(MAKECMDGOALS))
SKILL_FROM_GOAL := $(word 1,$(SKILL_GOALS))
ifneq ($(strip $(SKILL_FROM_GOAL)),)
override SKILL := $(SKILL_FROM_GOAL)
endif
PACKAGE := $(DIST_DIR)/$(SKILL).zip
PACKAGE_ABS := $(abspath $(PACKAGE))

ifneq ($(filter package list verify clean,$(MAKECMDGOALS)),)
ifneq ($(words $(SKILL_GOALS)),0)
ifneq ($(words $(SKILL_GOALS)),1)
$(error 一次只能指定一个 skill，例如：make package leap-slide)
endif
.PHONY: $(SKILL_GOALS)
$(SKILL_GOALS):
	@:
endif
endif

.PHONY: package list verify clean help

define require_skill
	@set -eu; \
	skill="$(SKILL)"; \
	case "$$skill" in \
	  ''|.*|*/*|*[!a-z0-9-]*) \
	    echo "错误：请指定根目录下的小写连字符 skill 名称，例如：make package leap-slide" >&2; exit 2 ;; \
	esac; \
	if [ ! -d "$$skill" ] || [ ! -f "$$skill/SKILL.md" ]; then \
	  echo "错误：未找到 skill '$$skill' 或其 SKILL.md" >&2; exit 2; \
	fi
endef

package:
	$(call require_skill)
	@mkdir -p "$(DIST_DIR)"
	@rm -f "$(PACKAGE)"
	@cd "$(SKILL)" && \
	if [ -e .git ]; then \
	  git ls-files -z --cached --others --exclude-standard -- \
	    ':(exclude)Makefile' ':(exclude).gitignore' | \
	    xargs -0 -r zip -q "$(PACKAGE_ABS)"; \
	else \
	  find . -type f \
	    ! -path './.git/*' \
	    ! -path './.codegraph/*' \
	    ! -path './dist/*' \
	    ! -path './.venv/*' \
	    ! -path './.pytest_cache/*' \
	    ! -path './.mypy_cache/*' \
	    ! -path './.ruff_cache/*' \
	    ! -path './node_modules/*' \
	    ! -path './htmlcov/*' \
	    ! -path '*/__pycache__/*' \
	    ! -path './Makefile' \
	    ! -path './.gitignore' \
	    ! -name '.coverage' \
	    ! -name '*.pyc' \
	    ! -name '*.pyo' \
	    ! -name '.DS_Store' \
	    ! -name 'Thumbs.db' \
    -print0 | \
	    xargs -0 -r zip -q "$(PACKAGE_ABS)"; \
	fi
	@$(MAKE) --no-print-directory verify "$(SKILL)"
	@echo "已生成 $(PACKAGE)"

list:
	$(call require_skill)
	@cd "$(SKILL)" && \
	if [ -e .git ]; then \
	  git ls-files --cached --others --exclude-standard -- \
	    ':(exclude)Makefile' ':(exclude).gitignore'; \
	else \
	  find . -type f \
	    ! -path './.git/*' \
	    ! -path './.codegraph/*' \
	    ! -path './dist/*' \
	    ! -path './.venv/*' \
	    ! -path './.pytest_cache/*' \
	    ! -path './.mypy_cache/*' \
	    ! -path './.ruff_cache/*' \
	    ! -path './node_modules/*' \
	    ! -path './htmlcov/*' \
	    ! -path '*/__pycache__/*' \
	    ! -path './Makefile' \
	    ! -path './.gitignore' \
	    ! -name '.coverage' \
	    ! -name '*.pyc' \
	    ! -name '*.pyo' \
	    ! -name '.DS_Store' \
	    ! -name 'Thumbs.db' \
    -print | sed 's#^\./##' | sort; \
	fi

verify:
	$(call require_skill)
	@if [ ! -f "$(PACKAGE)" ]; then \
	  echo "错误：未找到 $(PACKAGE)，请先运行 make package $(SKILL)" >&2; exit 2; \
	fi
	@unzip -tq "$(PACKAGE)"
	@if ! unzip -Z1 "$(PACKAGE)" | grep -Fxq 'SKILL.md'; then \
	  echo "错误：压缩包缺少 SKILL.md" >&2; exit 1; \
	fi
	@echo "压缩包校验通过：$(PACKAGE)"

clean:
	$(call require_skill)
	@rm -f "$(PACKAGE)"
	@echo "已清理 $(PACKAGE)"

help:
	@printf '%s\n' \
	  '用法：' \
	  '  make package <skill-name>  打包为 dist/<skill-name>.zip' \
	  '  make list <skill-name>     列出将被打包的文件' \
	  '  make verify <skill-name>   校验已有压缩包' \
	  '  make clean <skill-name>    删除对应压缩包'
