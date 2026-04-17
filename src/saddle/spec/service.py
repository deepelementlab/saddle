"""Simple /spec workflow service."""

from __future__ import annotations

import time
import uuid

from saddle.spec.store import CheckItem, SpecBundle, SpecStore, SpecTask


class SpecService:
    def __init__(self, working_directory: str = "."):
        self._store = SpecStore(working_directory=working_directory)

    def create_bundle(self, user_request: str, session_id: str | None = None) -> SpecBundle:
        sid = session_id or str(uuid.uuid4())
        ts = int(time.time())
        tasks = [
            SpecTask(
                id="T1",
                title="需求澄清与边界确认",
                description="对输入需求做场景、范围、验收边界定义。",
                acceptance_criteria=["明确 in-scope/out-of-scope", "列出关键风险与依赖"],
            ),
            SpecTask(
                id="T2",
                title="实现与集成方案",
                description="给出模块拆分、数据流和接口契约。",
                depends_on=["T1"],
                acceptance_criteria=["完成组件职责划分", "形成接口清单"],
            ),
            SpecTask(
                id="T3",
                title="验证与发布计划",
                description="定义测试策略、回归清单和上线步骤。",
                depends_on=["T2"],
                acceptance_criteria=["给出测试矩阵", "给出回滚方案"],
            ),
        ]
        checklist = [
            CheckItem(id="C1", description="规格覆盖主流程与异常流程", task_ref="T1"),
            CheckItem(id="C2", description="实现方案可落地且可观测", task_ref="T2"),
            CheckItem(id="C3", description="测试与发布步骤完整", task_ref="T3"),
        ]
        spec_md = (
            "# Specification\n\n"
            f"## User Request\n\n{user_request.strip()}\n\n"
            "## Goals\n\n- 交付可运行实现\n- 提供可验证标准\n\n"
            "## Constraints\n\n- 独立运行\n- 开箱即用\n"
        )
        tasks_md = "# Tasks\n\n" + "\n".join(
            [f"- [{t.status}] {t.id} {t.title}" for t in tasks]
        )
        checklist_md = "# Checklist\n\n" + "\n".join(
            [f"- [ ] {c.id} {c.description} (task: {c.task_ref})" for c in checklist]
        )
        bundle = SpecBundle(
            session_id=sid,
            user_request=user_request,
            spec_markdown=spec_md,
            tasks_markdown=tasks_md,
            checklist_markdown=checklist_md,
            created_at=ts,
            tasks=tasks,
            checklist=checklist,
        )
        return self._store.save_bundle(bundle)

    def latest_bundle(self, session_id: str) -> SpecBundle | None:
        return self._store.find_latest_bundle_for_session(session_id=session_id)
