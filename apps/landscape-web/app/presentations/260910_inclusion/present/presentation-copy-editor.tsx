"use client";

import {
  CheckIcon,
  EyeIcon,
  PencilIcon,
  RotateCcwIcon,
  SaveIcon,
  Undo2Icon,
} from "lucide-react";
import {
  createContext,
  type ClipboardEvent,
  type FormEvent,
  type KeyboardEvent,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import type {
  PresentationCopy,
  PresentationCopyKey,
} from "@/lib/inclusion-presentation-copy";

import styles from "./presentation.module.css";

type EditorContextValue = {
  activeKey: PresentationCopyKey | null;
  copy: PresentationCopy;
  editing: boolean;
  revision: number;
  setActiveKey: (key: PresentationCopyKey | null) => void;
  updateDraft: (
    key: PresentationCopyKey,
    value: string,
    commit: boolean,
  ) => void;
};

const EditorContext = createContext<EditorContextValue | null>(null);

function copiesMatch(left: PresentationCopy, right: PresentationCopy) {
  return Object.keys(left).every(
    (key) =>
      left[key as PresentationCopyKey] === right[key as PresentationCopyKey],
  );
}

export function PresentationCopyEditor({
  children,
  endpoint = "/api/inclusion-presentation-copy",
  initialCopy,
}: {
  children: ReactNode;
  endpoint?: string;
  initialCopy: PresentationCopy;
}) {
  const [copy, setCopy] = useState(initialCopy);
  const [savedCopy, setSavedCopy] = useState(initialCopy);
  const [editing, setEditing] = useState(false);
  const [canEdit, setCanEdit] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const [activeKey, setActiveKey] = useState<PresentationCopyKey | null>(null);
  const [revision, setRevision] = useState(0);
  const [status, setStatus] = useState("本地文案");
  const draftRef = useRef(initialCopy);

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      setCanEdit(
        window.location.hostname === "127.0.0.1" ||
          window.location.hostname === "localhost" ||
          window.location.hostname === "::1",
      );
    });
    return () => window.cancelAnimationFrame(frame);
  }, []);

  const updateDraft = useCallback(
    (key: PresentationCopyKey, value: string, commit: boolean) => {
      const nextCopy = { ...draftRef.current, [key]: value };
      draftRef.current = nextCopy;
      setDirty(!copiesMatch(nextCopy, savedCopy));
      setStatus("有未保存修改");
      if (commit) setCopy(nextCopy);
    },
    [savedCopy],
  );

  function resetSession() {
    draftRef.current = savedCopy;
    setCopy(savedCopy);
    setDirty(false);
    setActiveKey(null);
    setStatus("已撤销本次修改");
    setRevision((current) => current + 1);
  }

  function resetActiveField() {
    if (!activeKey) return;
    const nextCopy = {
      ...draftRef.current,
      [activeKey]: savedCopy[activeKey],
    };
    draftRef.current = nextCopy;
    setCopy(nextCopy);
    setDirty(!copiesMatch(nextCopy, savedCopy));
    setStatus("已恢复这段文字");
    setRevision((current) => current + 1);
  }

  async function saveDraft() {
    setSaving(true);
    setStatus("正在保存…");

    try {
      const response = await fetch(endpoint, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ copy: draftRef.current }),
      });
      const result: unknown = await response.json();
      if (!response.ok) {
        const message =
          result && typeof result === "object" && "error" in result
            ? String((result as { error: unknown }).error)
            : "保存失败";
        throw new Error(message);
      }

      const nextSaved = draftRef.current;
      setSavedCopy(nextSaved);
      setCopy(nextSaved);
      setDirty(false);
      setStatus("已保存到演讲文案");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "保存失败");
    } finally {
      setSaving(false);
    }
  }

  const contextValue = useMemo<EditorContextValue>(
    () => ({
      activeKey,
      copy,
      editing,
      revision,
      setActiveKey,
      updateDraft,
    }),
    [activeKey, copy, editing, revision, updateDraft],
  );

  return (
    <EditorContext.Provider value={contextValue}>
      {children}
      {canEdit ? (
        <aside
          className={styles.presentationCopyEditor}
          data-editing={editing}
          aria-label="本地演讲文案编辑器"
        >
          <button
            className={styles.presentationEditorPrimary}
            type="button"
            aria-label={editing ? "预览" : "编辑文案"}
            onClick={() => {
              setEditing((current) => !current);
              setActiveKey(null);
              setStatus(editing ? "预览模式" : "点击虚线框直接改文字");
            }}
          >
            {editing ? (
              <EyeIcon aria-hidden="true" />
            ) : (
              <PencilIcon aria-hidden="true" />
            )}
            <span className={styles.presentationEditorLabel}>
              {editing ? "预览" : "编辑文案"}
            </span>
          </button>

          {editing ? (
            <div className={styles.presentationEditorActions}>
              <button
                type="button"
                disabled={!activeKey}
                onClick={resetActiveField}
              >
                <RotateCcwIcon aria-hidden="true" />
                恢复这段
              </button>
              <button type="button" disabled={!dirty} onClick={resetSession}>
                <Undo2Icon aria-hidden="true" />
                撤销本次
              </button>
              <button
                type="button"
                disabled={!dirty || saving}
                onClick={saveDraft}
              >
                {saving ? (
                  <span
                    className={styles.presentationEditorSpinner}
                    aria-hidden="true"
                  />
                ) : dirty ? (
                  <SaveIcon aria-hidden="true" />
                ) : (
                  <CheckIcon aria-hidden="true" />
                )}
                {saving ? "保存中" : "保存"}
              </button>
            </div>
          ) : null}

          <span
            className={styles.presentationEditorStatus}
            aria-live="polite"
          >
            {status}
          </span>
        </aside>
      ) : null}
    </EditorContext.Provider>
  );
}

type EditableTag =
  | "blockquote"
  | "h2"
  | "h3"
  | "p"
  | "small"
  | "span"
  | "strong"
  | "time";

export function EditablePresentationText({
  as: Tag = "span",
  className,
  copyKey,
}: {
  as?: EditableTag;
  className?: string;
  copyKey: PresentationCopyKey;
}) {
  const editorContext = useContext(EditorContext);
  if (!editorContext) {
    throw new Error(
      "EditablePresentationText must be rendered inside PresentationCopyEditor",
    );
  }
  const editor = editorContext;
  const value = editor.copy[copyKey] ?? "";

  function readText(element: HTMLElement) {
    return element.innerText.replaceAll("\u00a0", " ").trim();
  }

  function handleInput(event: FormEvent<HTMLElement>) {
    editor.updateDraft(copyKey, readText(event.currentTarget), false);
  }

  function handlePaste(event: ClipboardEvent<HTMLElement>) {
    event.preventDefault();
    document.execCommand(
      "insertText",
      false,
      event.clipboardData.getData("text/plain"),
    );
  }

  function handleKeyDown(event: KeyboardEvent<HTMLElement>) {
    if (event.key !== "Enter") return;
    event.preventDefault();
    event.currentTarget.blur();
  }

  return (
    <Tag
      className={`${styles.presentationEditableText}${className ? ` ${className}` : ""}`}
      contentEditable={editor.editing ? "plaintext-only" : false}
      data-copy-empty={value.length === 0}
      data-presentation-copy-key={copyKey}
      key={`${copyKey}-${editor.revision}`}
      onBlur={(event) => {
        editor.updateDraft(copyKey, readText(event.currentTarget), true);
      }}
      onFocus={() => editor.setActiveKey(copyKey)}
      onInput={handleInput}
      onKeyDown={handleKeyDown}
      onPaste={handlePaste}
      spellCheck={editor.editing}
      suppressContentEditableWarning
    >
      {value}
    </Tag>
  );
}
