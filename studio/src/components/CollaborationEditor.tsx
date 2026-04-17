import { lazy, Suspense, useMemo, useState } from "react";
import {
  DndContext,
  type DragEndEvent,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import { SortableContext, arrayMove, sortableKeyboardCoordinates, useSortable, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import type { Lang } from "../i18n";
import { text } from "../i18n";
import type { CollaborationPrimitive, PrimitiveGroupDef, StageCollaboration } from "../types/collaboration";
import { newPrimitiveId } from "../utils/collaboration";
const SchemaFieldEditor = lazy(async () => {
  const m = await import("./SchemaFieldEditor");
  return { default: m.SchemaFieldEditor };
});

interface Props {
  lang: Lang;
  stage: "design" | "develop";
  value: StageCollaboration;
  onChange: (next: StageCollaboration) => void;
}

function PrimitiveSchemaPanel({
  primitive,
  t,
  onPatch,
}: {
  primitive: CollaborationPrimitive;
  t: (typeof text)[Lang];
  onPatch: (id: string, patch: Partial<CollaborationPrimitive>) => void;
}): JSX.Element {
  return (
    <div className="schema-grid schema-grid-advanced">
      <Suspense fallback={<div className="schema-editor-loading">{t.schemaEditorLoading}</div>}>
        <SchemaFieldEditor
          pathId={`${primitive.id}-in`}
          label={t.schemaIn}
          schema={primitive.input_schema}
          onCommit={(next) => onPatch(primitive.id, { input_schema: next })}
          t={t}
        />
        <SchemaFieldEditor
          pathId={`${primitive.id}-out`}
          label={t.schemaOut}
          schema={primitive.output_schema}
          onCommit={(next) => onPatch(primitive.id, { output_schema: next })}
          t={t}
        />
      </Suspense>
    </div>
  );
}

function SortableGroupRow({
  group,
  index,
  total,
  lang,
  onPatchLabel,
  onMove,
  onRemove,
}: {
  group: PrimitiveGroupDef;
  index: number;
  total: number;
  lang: Lang;
  onPatchLabel: (id: string, label: string) => void;
  onMove: (id: string, dir: -1 | 1) => void;
  onRemove: (id: string) => void;
}): JSX.Element {
  const t = text[lang];
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: group.id });
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.92 : 1,
    boxShadow: isDragging ? "0 6px 18px rgba(50, 50, 93, 0.15)" : undefined,
  };
  return (
    <div ref={setNodeRef} style={style} className="group-row sortable-group-row">
      <button type="button" className="drag-handle group-drag-handle" aria-label={t.dragHintGroups} {...attributes} {...listeners}>
        ⠿
      </button>
      <input value={group.label} onChange={(e) => onPatchLabel(group.id, e.target.value)} />
      <span className="group-meta">id: {group.id}</span>
      <button type="button" className="btn btn-secondary btn-compact" disabled={index === 0} onClick={() => onMove(group.id, -1)}>
        ↑
      </button>
      <button
        type="button"
        className="btn btn-secondary btn-compact"
        disabled={index === total - 1}
        onClick={() => onMove(group.id, 1)}
      >
        ↓
      </button>
      <button type="button" className="btn btn-secondary btn-compact" onClick={() => onRemove(group.id)}>
        {t.removeGroup}
      </button>
    </div>
  );
}

function SortablePrimitiveRow({
  primitive,
  lang,
  groupOptions,
  onPatch,
  onRemove,
}: {
  primitive: CollaborationPrimitive;
  lang: Lang;
  groupOptions: { id: string; label: string }[];
  onPatch: (id: string, patch: Partial<CollaborationPrimitive>) => void;
  onRemove: (id: string) => void;
}): JSX.Element {
  const t = text[lang];
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: primitive.id });
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    boxShadow: isDragging ? "0 8px 24px rgba(50,50,93,0.2)" : undefined,
  };
  const [schemaOpen, setSchemaOpen] = useState(false);

  return (
    <div ref={setNodeRef} style={style} className="primitive-card">
      <div className="primitive-card-head">
        <button type="button" className="drag-handle" aria-label={t.dragHint} {...attributes} {...listeners}>
          ⠿
        </button>
        <div className="primitive-fields">
          <label className="inline-label">
            {t.primKey}
            <input value={primitive.key} onChange={(e) => onPatch(primitive.id, { key: e.target.value })} />
          </label>
          <label className="inline-label">
            {t.primLabel}
            <input value={primitive.label} onChange={(e) => onPatch(primitive.id, { label: e.target.value })} />
          </label>
          <label className="inline-label">
            {t.primGroup}
            <select
              value={primitive.group_id ?? ""}
              onChange={(e) => onPatch(primitive.id, { group_id: e.target.value === "" ? null : e.target.value })}
            >
              <option value="">{t.primUngrouped}</option>
              {groupOptions.map((g) => (
                <option key={g.id} value={g.id}>
                  {g.label}
                </option>
              ))}
            </select>
          </label>
        </div>
        <button type="button" className="btn btn-secondary btn-compact" onClick={() => onRemove(primitive.id)}>
          {t.removePrimitive}
        </button>
      </div>
      <div className="constraints-block">
        <div className="constraints-head">
          <span>{t.constraints}</span>
          <button
            type="button"
            className="btn btn-secondary btn-compact"
            onClick={() => onPatch(primitive.id, { constraints: [...primitive.constraints, ""] })}
          >
            {t.addConstraint}
          </button>
        </div>
        {primitive.constraints.map((c, idx) => (
          <div key={`${primitive.id}-c-${idx}`} className="constraint-row">
            <input
              value={c}
              onChange={(e) => {
                const next = [...primitive.constraints];
                next[idx] = e.target.value;
                onPatch(primitive.id, { constraints: next });
              }}
            />
            <button
              type="button"
              className="btn btn-secondary btn-compact"
              onClick={() => {
                const next = primitive.constraints.filter((_, j) => j !== idx);
                onPatch(primitive.id, { constraints: next });
              }}
            >
              ×
            </button>
          </div>
        ))}
      </div>
      <button type="button" className="btn btn-secondary btn-compact schema-toggle" onClick={() => setSchemaOpen(!schemaOpen)}>
        {schemaOpen ? t.hideSchemas : t.showSchemas}
      </button>
      {schemaOpen && <PrimitiveSchemaPanel primitive={primitive} t={t} onPatch={onPatch} />}
    </div>
  );
}

export function CollaborationEditor({ lang, stage, value, onChange }: Props): JSX.Element {
  const t = text[lang];
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 6 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const formatEntries = useMemo(() => Object.entries(value.collaboration_format), [value.collaboration_format]);

  const setFormat = (entries: [string, string][]): void => {
    onChange({ ...value, collaboration_format: Object.fromEntries(entries.filter(([k]) => k.trim() !== "")) });
  };

  const patchPrimitive = (id: string, patch: Partial<CollaborationPrimitive>): void => {
    onChange({
      ...value,
      primitives: value.primitives.map((p) => (p.id === id ? { ...p, ...patch } : p)),
    });
  };

  const removePrimitive = (id: string): void => {
    onChange({ ...value, primitives: value.primitives.filter((p) => p.id !== id) });
  };

  const addPrimitive = (): void => {
    const key = `custom_step_${value.primitives.length + 1}`;
    const np: CollaborationPrimitive = {
      id: newPrimitiveId(stage),
      key,
      label: t.newPrimitiveLabel,
      group_id: value.groups[0]?.id ?? null,
      constraints: [],
      input_schema: { type: "object", additionalProperties: true, properties: {} },
      output_schema: { type: "object", additionalProperties: true, properties: {} },
    };
    onChange({ ...value, primitives: [...value.primitives, np] });
  };

  const onDragEndGroups = (event: DragEndEvent): void => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const ordered = [...value.groups].sort((a, b) => a.order - b.order);
    const oldIndex = ordered.findIndex((g) => g.id === active.id);
    const newIndex = ordered.findIndex((g) => g.id === over.id);
    if (oldIndex < 0 || newIndex < 0) return;
    const reordered = arrayMove(ordered, oldIndex, newIndex);
    const orderById = new Map(reordered.map((g, i) => [g.id, i]));
    onChange({
      ...value,
      groups: value.groups.map((g) => ({ ...g, order: orderById.get(g.id) ?? g.order })),
    });
  };

  const onDragEndPrimitives = (event: DragEndEvent): void => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const oldIndex = value.primitives.findIndex((p) => p.id === active.id);
    const newIndex = value.primitives.findIndex((p) => p.id === over.id);
    if (oldIndex < 0 || newIndex < 0) return;
    onChange({ ...value, primitives: arrayMove(value.primitives, oldIndex, newIndex) });
  };

  const sortedGroups = [...value.groups].sort((a, b) => a.order - b.order);

  const moveGroup = (id: string, dir: -1 | 1): void => {
    const ordered = [...value.groups].sort((a, b) => a.order - b.order);
    const idx = ordered.findIndex((g) => g.id === id);
    const j = idx + dir;
    if (idx < 0 || j < 0 || j >= ordered.length) return;
    const a = ordered[idx];
    const b = ordered[j];
    const next = value.groups.map((g) => {
      if (g.id === a.id) return { ...g, order: b.order };
      if (g.id === b.id) return { ...g, order: a.order };
      return g;
    });
    onChange({ ...value, groups: next });
  };

  const addGroup = (): void => {
    const id = newPrimitiveId("group");
    const order = value.groups.length ? Math.max(...value.groups.map((g) => g.order)) + 1 : 0;
    onChange({
      ...value,
      groups: [...value.groups, { id, label: lang === "zh" ? "新分组" : "New group", order }],
    });
  };

  const removeGroup = (id: string): void => {
    onChange({
      ...value,
      groups: value.groups.filter((g) => g.id !== id),
      primitives: value.primitives.map((p) => (p.group_id === id ? { ...p, group_id: null } : p)),
    });
  };

  const patchGroup = (id: string, label: string): void => {
    onChange({
      ...value,
      groups: value.groups.map((g) => (g.id === id ? { ...g, label } : g)),
    });
  };

  const groupOptions = sortedGroups.map((g) => ({ id: g.id, label: g.label }));

  return (
    <div className="collab-editor">
      <h4 className="stage-tag">{stage}</h4>

      <div className="format-block">
        <h5>{t.formatFields}</h5>
        {formatEntries.map(([k, v], idx) => (
          <div key={`${stage}-fmt-${idx}`} className="format-row">
            <input
              placeholder="key"
              value={k}
              onChange={(e) => {
                const next = [...formatEntries];
                next[idx] = [e.target.value, v];
                setFormat(next);
              }}
            />
            <input
              placeholder="value"
              value={v}
              onChange={(e) => {
                const next = [...formatEntries];
                next[idx] = [k, e.target.value];
                setFormat(next);
              }}
            />
            <button
              type="button"
              className="btn btn-secondary btn-compact"
              onClick={() => setFormat(formatEntries.filter((_, j) => j !== idx))}
            >
              ×
            </button>
          </div>
        ))}
        <button type="button" className="btn btn-secondary btn-compact" onClick={() => setFormat([...formatEntries, ["", ""]])}>
          {t.addFormatField}
        </button>
      </div>

      <div className="groups-block">
        <div className="groups-head">
          <h5>{t.collabGroups}</h5>
          <button type="button" className="btn btn-secondary btn-compact" onClick={addGroup}>
            {t.addGroup}
          </button>
        </div>
        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={onDragEndGroups}>
          <SortableContext items={sortedGroups.map((g) => g.id)} strategy={verticalListSortingStrategy}>
            <div className="group-list">
              {sortedGroups.map((g, i) => (
                <SortableGroupRow
                  key={g.id}
                  group={g}
                  index={i}
                  total={sortedGroups.length}
                  lang={lang}
                  onPatchLabel={patchGroup}
                  onMove={moveGroup}
                  onRemove={removeGroup}
                />
              ))}
            </div>
          </SortableContext>
        </DndContext>
      </div>

      <div className="primitives-block">
        <div className="primitives-head">
          <h5>{t.collabPrimitives}</h5>
          <button type="button" className="btn btn-secondary btn-compact" onClick={addPrimitive}>
            {t.addPrimitive}
          </button>
        </div>
        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={onDragEndPrimitives}>
          <SortableContext items={value.primitives.map((p) => p.id)} strategy={verticalListSortingStrategy}>
            <div className="primitive-list">
              {value.primitives.map((p) => (
                <SortablePrimitiveRow
                  key={p.id}
                  primitive={p}
                  lang={lang}
                  groupOptions={groupOptions}
                  onPatch={patchPrimitive}
                  onRemove={removePrimitive}
                />
              ))}
            </div>
          </SortableContext>
        </DndContext>
      </div>
    </div>
  );
}
