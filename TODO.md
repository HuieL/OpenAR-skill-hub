# OpenAR Skill Hub — Agent X 工作台（TODO 与里程碑）

本文件只在本仓库的 `todo` 分支维护，**永不合入 `main`**（`main` 是对外发布内容，必须干净）。
派工与验收由 OpenRA Review 负责；OpenRA 主仓库的 `TODO.md` 只记录 X 的一行状态与交接 SHA。

规格（以 OpenRA 主仓为准，勿复制）：`docs/skill-extension-hub-design.md`、`docs/skill-extension-hub-todo.md`（HUB-00…10）、`docs/hub-00-reuse-map.md`（C 的现状复用表）。

## 0. 角色与边界

- **X 负责本仓库的全部内容**：目录结构、条目（entries）、schema、生成的 `skills.json` 索引、校验脚本、CI、贡献说明、播种与发布。
- **不负责**：OpenRA 侧的 registry 客户端/安装/版本/回滚（C）、Hub UI（G+D）、Extension（Y 的 `OpenAR-extension-hub`）。
- **协作**：
  - X 定义 skill 条目 schema；**C 的 registry 客户端读取它**，schema 每次变更先在 OpenRA 主仓 TODO 的 M-HUB 行与 C 对齐，并在 PR 描述里写 `schemaVersion`。
  - 与 Y 共用同一份「条目公共核心字段」（id/kind/name/summary/source/version/license/review/compat）；字段名与语义两仓必须一致，改动需两边同 PR 描述互相引用。
  - 其他 agent（H/I/J/C 等）要上架自己的 skill：在本仓推 `agent-<x>/<topic>` 分支，X 先做内容审查，Review 最终合入 `main`。
- **分支与合入**：只推 `agent-x/<topic>` 分支；**不直接推 `main`**；Review（OpenRA 审查负责人）审查后合入。每个分支一个主题，小提交。
- **main 只放发布内容**：README、LICENSE、`skills.json`、`entries/`、`schemas/`、`scripts/`（校验/生成）、`.github/workflows/`。不放 TODO、回执、证据、验收记录、个人笔记（这些放 OpenRA 主仓 `docs/acceptance/`）。
- **安全**：不提交任何 token/凭据；CI 校验 job 无写权限、无 secrets，不执行 PR 中的脚本/安装命令；第三方内容逐条核许可，不整库复制上游。

## 1. 当前事实（2026-10-12）

- 本仓库为空（无任何分支）。GitHub 默认分支在 `main` 建立后由用户设为 `main`。
- OpenRA 内置 skill（随 App 发布，`agent-skills/`）：17 个 ora-* 核心 + `diagram-design`（cathrynlavery/diagram-design@7a2e2217，**MIT**，已 vendored）。
- OpenRA curated（编译期内置，`src/local/curated_skills_data/`）：`officecli-academic-paper`、`officecli-data-dashboard`（iOfficeAI/AionCore@4a707fc）、`human-writing`（KKKKhazix/human-writing@4fda173f，MIT）。
- H 已准备 `ora-craft-suite` skill（OpenRA 分支 `agent-h/craft-suite-skill`，等本仓 main 建好后转为条目）。
- C 的 registry 客户端（HUB-01）尚未实现；它将按 commit SHA 固定读取本仓 `skills.json` 并逐条校验 sha256。

## 2. 里程碑

| 里程碑 | 内容 | 通过条件 |
| --- | --- | --- |
| **SX-M0 骨架** | 目录、schema、索引生成与校验、CI、README/LICENSE、贡献说明 | Review 合入后成为 `main`；`scripts/validate` 本地与 CI 都过；空索引合法 |
| **SX-M1 首批条目（HUB-M1 的 skill 半）** | 播种：`diagram-design`、`human-writing`、`officecli-academic-paper`、`officecli-data-dashboard`、`ora-craft-suite`；核心 ora-* 以 `delivery: bundled` 只读登记 | C 的客户端在固定 SHA 读到索引、sha256 全部吻合；OpenRA 能从本仓安装 `diagram-design` 并在会话中按需使用、升级、回滚（由 C/A 验收） |
| **SX-M2 可贡献** | 社区/私有来源说明、条目弃用/高风险标记、版本更新流程、更新检查所需的元数据 | 一个外部贡献样例从 PR 到合入走通；CI 不执行 PR 代码 |

## 3. 任务

### SX-00 骨架（NOW）
- [ ] 目录：
  ```
  README.md
  LICENSE                      # 仓库元数据与脚本：MIT；条目内容各按其上游许可
  skills.json                  # 由 scripts 从 entries 生成，禁止手改
  entries/skills/<id>/entry.json
  entries/skills/<id>/skill/   # 仅当 skill 正文由本仓托管时（维护者自有的小 skill）
  schemas/skill-entry.schema.json
  scripts/build-index.(py|mjs) scripts/validate.(py|mjs)
  .github/workflows/validate.yml
  CONTRIBUTING.md
  ```
- [ ] `entry.json` 字段（与 Y 共用核心 + skill 专属）：
  - 核心：`schemaVersion`(=1)、`id`（命名空间，如 `openra.diagram-design`；与显示名分离、全局唯一、不复用）、`kind`(="skill")、`name`（**一个简短英文名，所有语言相同**）、`summary`（可含 5 语言 `i18n`：en/zh-CN/ja/ko/es，只本地化描述）、`source`{`repo`,`path`,`revision`(40 位 commit SHA，禁止 main/latest/可变 tag)}、`version`（上游自报，没有则用 revision）、`license`(SPDX)+`licenseFile`、`review`{`status`: unreviewed|reviewed|deprecated|high-risk, `reviewedRevision`, `reviewer`}、`compat`{`minHost`,`harnesses`}
  - skill 专属：`delivery`: `bundled`（随 App，不可单独安装，只展示）| `hub`（可安装）；`files[]`{`path`,`sha256`,`bytes`,`executable`}（完整必要文件清单与哈希，含 scripts/references/assets；没有的目录不列）；`totalBytes`；`requires`（依赖的 extension/CLI/MCP 的 id，仅声明，不自动安装）；`permissionsNote`（SKILL.md 里 allowed-tools 等只是声明，不是本机批准）
- [ ] `skills.json`：按 id 排序的轻量投影（id/name/summary/delivery/version/revision/entryPath/entrySha256），由 build-index 生成；validate 检查与 entries 一致、无重复 id、无未知字段、sha256 对得上、路径无 `..`/绝对路径/符号链接、单条目大小上限（建议 ≤2 MiB）。
- [ ] CI：`pull_request` 只读校验（`permissions: contents: read`，无 secrets，不运行条目内脚本，不安装依赖之外的任何东西）；固定 action 版本到 SHA。
- [ ] README：Hub 是什么、如何被 OpenRA 读取（固定 revision + sha256）、`delivery` 含义、如何贡献、许可说明。
- 交付：分支 `agent-x/skeleton` → Review 合入成为 `main`。

### SX-01 首批条目（NEXT，SX-00 合入后）
- [ ] `diagram-design`：上游 `cathrynlavery/diagram-design@7a2e2217`，MIT；`files[]` 与 OpenRA `agent-skills/diagram-design/` 逐文件 sha256 一致（以 OpenRA main 实际字节为准）。
- [ ] `human-writing`（MIT，上游 SHA 见 OpenRA curated 数据）、`officecli-academic-paper` / `officecli-data-dashboard`（核对上游许可；安装段落是 OpenRA 的"固定发布版安装"改写形式，条目需说明是改写版并给出原文来源）。
- [ ] `ora-craft-suite`：从 OpenRA `agent-h/craft-suite-skill` 接收（H 提供内容，X 建条目）；displayName 已统一为 "Craft Suite"。
- [ ] 17 个 ora-* 核心：`delivery: bundled`，只登记 id/name/summary/当前 OpenRA 发布 revision，不提供安装文件（随 App 更新）。
- [ ] 每条：许可文件、上游 revision、全部文件哈希；没有确认存在的 URL/版本不得上架。
- 交付：每 1–3 个条目一个分支 `agent-x/seed-<name>`。

### SX-02 可贡献与生命周期（LATER）
- [ ] CONTRIBUTING：开发者在自己仓库托管 skill，向本仓提交条目 PR；本仓只托管维护者自有的小 skill。
- [ ] 弃用/高风险/下架：保留条目与历史 revision，`review.status` 变更说明原因；OpenRA 侧据此提示（C）。
- [ ] 版本更新：新 revision = 新 `source.revision` + 新哈希；旧 revision 保留可回滚。
- [ ] 私有/本地来源说明：本仓不收私有内容，OpenRA 支持用户自加来源（C 实现）。

## 4. 验收与回报
- 每个分支：`scripts/validate` 输出、条目数、是否改 schema（改了需写 schemaVersion 与对 C/Y 的影响）。
- 回报写在 OpenRA 主仓 TODO 的 X 行（只写分支@SHA + 一句结论），不要在本仓 main 写回执。
- 规模：每分支新增手写文件 ≤5、修改 ≤10（条目数据文件除外，但每分支 ≤3 个新条目）。

## 5. OpenRA 主仓上的底座工作（用户 10-12：X/Y 在 OpenRA 分支写入底座以无缝集成）

- 在 OpenRA 只推 `agent-x/<topic>` 分支；Review 审查，Rust 改动进 Mac 门禁 train 后合入。派工以 OpenRA `TODO.md` 的 X 行为准。
- **HUB-01 registry 客户端（X 负责，两个 hub 共用一份实现）**：
  - [ ] 按 commit SHA 读取 `skills.json` 与 Y 仓的 `extensions.json`；逐条校验 entry sha256；拒绝 main/latest/可变 tag 当锁定。
  - [ ] 缓存 last-good 索引与刷新时间，断网不影响已安装能力；条件请求/ETag、限流退避、大小与条目数上限。
  - [ ] 只读：不安装、不执行；安装走 C 的 `acquire::*` + ChangeSet（改 `acquire/*`、`changesets.rs` 需 C 共审）。
  - [ ] fixture 测试（空索引、坏哈希、未知字段、路径穿越、超限）+ 对两真仓的只读探测。
- **HUB-04 skill 加载/编辑**：标准 SKILL.md 及必要 scripts/references/assets；按 revision 管理第三方 skill；只暴露当前 scope 已选 skill 的 metadata，正文按需读取；本地修改产生新本地 revision，升级前展示差异。
- 不碰：Hub UI（G+D）、ExtensionDefinition 契约（G）、扩展安装（Y）。

## 6. HUB-11 Community, Credits & Discovery（后续里程碑 SX-M3/M4；规格 OpenRA `docs/hub-community-discovery.md`）

**SX-00 起就预留署名字段**（避免以后迁移）：entry.json 公共核心加 `authors[]`{name,github}、`maintainers[]`、`contributors[]`、`adapters[]`（OpenRA 适配者）、`registrySubmitter`、`categories[]`；Y 仓同名同义。
- **SX-M3（HUB-M1 通过后，HUB-11 M2 部分）**
  - [ ] 署名校验（CI）：Original Author 必须能在 `source` 仓库的提交/许可/README 中核对；提交者默认只记 `registrySubmitter`，不可自填为 author；纠错走 PR + 原作者或维护者确认。
  - [ ] `community/creators.json`（作者公开资料：名称、GitHub、代表作品 `kind:id`，只放公开信息）、`community/featured.json`（条目、理由、日期、精选者）、`community/collections.json`（标题、说明、策展者、`kind:id` 列表、推荐理由）——两仓的社区数据**只在本仓**，用 `kind:id` 引用 Y 仓条目。
  - [ ] PR 模板与 CONTRIBUTING：新增条目、修正署名、提交合集。
- **SX-M4（HUB-11 M3 部分）**
  - [ ] GitHub Actions 定时生成 `community/discovery.json`：New（首次收录日期）、Recently Updated（可核查 release/commit）、Trending（公开 GitHub 信号，写明指标与窗口，标注 "Trending on GitHub"，不冒充安装量）；给新/小众项目保留曝光位；失败保留上一版；只读公开元数据，固定 action SHA，无写权限外泄。
- 不做：社区服务器、账号、评论库、点赞积分、等级、付费位；不收集私人使用历史/安装记录。
