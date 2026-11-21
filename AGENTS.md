# Agent Instructions

This repository prepares an ESP-IDF HTTPS OTA code review and reproducible QEMU tests.

- Use simple everyday English and keep changes focused.
- Record commands, findings, failed attempts, and explanations under `docs/`.
- Keep personal documents, interview logistics, and unfiltered logs in ignored directories like `tmp/`.
- Run builds in `nix develop` and use `uv` for Python dependencies.
- The review SDK is pinned to `7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00`.
- Keep SDK sources clean. Generate experimental fixes in build directories.
- Do not open physical serial ports or flash boards without explicit authorization.
- Distinguish injected faults, emulated behavior, and physical hardware results.
- Document the single-core, HTTP, and disabled QEMU watchdog limitations.

## Writing Style

- Write in simple, plain English. Use short sentences and everyday words.
- Use Oxford commas in inline lists: "a, b, and c" not "a, b, c".
- Do not use em dashes. Restructure the sentence or use a semicolon instead. User emojis scarcely.
- Avoid colons in the middle of sentences. A colon that introduces a code block or a list is fine;
  existing text is reworded when it is touched anyway, not in a sweep.
- Avoid colorful adjectives and adverbs. Write "adjacency query" not "blazing adjacency query".
- Prefer noun phrases for checklist items over imperative verbs. Write "temp directory teardown" not "tear down the temp directory".
- Headings in Markdown files must be in title case: "Build from Source" not "Build from source". Minor words (a, an, the, and, but, or, for, in, on,
  at, to, by, of) stay lowercase unless they are the first word.
- Do not bold the lead-in of a list item. Write "Vector and set similarity: ..." not "**Vector and set similarity**: ...".
- Use sentence case for the lead-in of a list item. Write "Seed selection: ..." not "Seed Selection: ...". Proper nouns keep their capitals.
- Capitalize only the first part of a hyphenated compound: "Full-text Search" in a heading, "Breadth-first" at the start of a sentence, and
  "breadth-first search" elsewhere. Never write "Breadth-First".
- Start each sentence with a capital letter, capitalize proper nouns (Rust, PostgreSQL, SvelteKit, TypeScript), and leave common nouns lowercase
  in the middle of a sentence.
- Write correct and complete sentences.
- Avoid made-up words and abbreviations.
- Use participial phrases scarcely.
