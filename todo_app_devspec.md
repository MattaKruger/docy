Okay, here is a comprehensive specification document based on our iterative discussion. This incorporates all the requirements, design choices, and details we covered, intended for a developer to begin implementation.

---

**Specification: Automatic Descriptive TODO Generator**

**Version:** 1.0
**Date:** 2023-10-27

**1. Introduction & Overview**

This document specifies a command-line interface (CLI) tool written in Python. The tool scans a Python codebase for custom markers (`# TODO-{name}...# TODO-end`), extracts the code block defined by these markers along with metadata, and utilizes a Large Language Model (LLM) via the user's configured `pydantic_ai` layer to generate descriptive TODO items. These generated TODOs, along with source code context and error reports, are appended to a structured Markdown file.

**2. Functional Requirements**

**2.1. TODO Marker Syntax & Validation**
*   **Start Marker:** Identifies the beginning of a TODO span. Must conform to one of the following formats:
    *   `# TODO-{name}`
    *   `# TODO-{name}[{prompt_text}]`
*   **End Marker:** Identifies the end of a TODO span. Must be exactly:
    *   `# TODO-end`
*   **Validation:** The parsing logic must strictly enforce the marker format:
    *   Must start exactly with `# TODO-`.
    *   `{name}` must be present, non-empty, and contain only alphanumeric characters, hyphens, and underscores (`[a-zA-Z0-9_-]+`).
    *   If `[` is present immediately after `{name}`, a corresponding `]` must be the last character on the line.
    *   `{prompt_text}` between brackets must be non-empty if brackets are used.
    *   No extraneous characters allowed after `{name}` (if no brackets) or after `]` (if brackets).
    *   Markers are identified after stripping leading/trailing whitespace from the line.
*   **Error Handling:** Lines starting with `# TODO-` but failing validation must be reported as errors (See Section 2.7).

**2.2. File Discovery & Parsing**
*   **Target Files:** Scan for `.py` files.
*   **Scope:** Scan starts from a specified input path or the Current Working Directory (CWD). The scan is recursive.
*   **Exclusions:**
    *   Respect rules defined in a `.gitignore` file located in the CWD where the tool is executed.
    *   Use the `pathspec` library to parse `.gitignore` rules.
    *   Ignored files and directories (and their contents) are skipped during the scan.
*   **Parsing Strategy:**
    *   Process each non-ignored `.py` file line-by-line.
    *   Use regular expressions to identify potential start and end markers on each line.
    *   Maintain state using a stack data structure to handle nested TODO spans correctly.
    *   Extract `name`, `prompt_text` (if provided), `code_block` (lines between start and end markers), `start_line` number, and nesting relationships.

**2.3. LLM Integration**
*   **Interface:** Integration with the LLM will be handled via a user-provided `pydantic_ai` layer/instance. This spec focuses on preparing the input for that layer.
*   **Input Construction:** For each valid TODO span, construct a single text prompt string to be passed to the `pydantic_ai` layer. The prompt must include:
    *   The extracted `{name}`.
    *   The relevant prompt instruction (either custom `prompt_text` or the default).
    *   The extracted `{code_block}`.
    *   Clear context labels (See example below).
*   **Default Prompt Instruction:** When no custom `[{prompt_text}]` is provided in the marker, use the following instruction:
    ```
    "Analyze the provided code block and the TODO name. Generate a descriptive TODO item outlining the necessary task. If the task seems to involve multiple distinct steps or actions, format the description as a bulleted list with Markdown checkboxes (`- [ ] Action`). Otherwise, provide a concise summary sentence or paragraph."
    ```
*   **LLM Output Expectation:** The LLM (via `pydantic_ai`) is expected to return a string containing the description (either a single sentence/paragraph or a Markdown list with checkboxes). The LLM decides the format based on its analysis and the prompt.
*   **Prompt Structure Example:**
    ```text
    Context for the TODO item:
    Name: {name}

    Instructions for generation:
    {prompt_instruction}

    Code block to analyze:
    ```python
    {code_block}
    ```

    Generate the TODO description based on the instructions, name, and code block provided.
    ```

**2.4. Output Generation (Markdown File)**
*   **File Handling:**
    *   Output is written to a Markdown file (e.g., `TODO.md`).
    *   The tool appends to the file if it already exists.
    *   If appending, a delimiter line is added before the new entries:
        *   Format with custom name: `## Scan: {delimiter_name} (Executed on: YYYY-MM-DD HH:MM:SS)`
        *   Format without custom name: `## Scan executed on: YYYY-MM-DD HH:MM:SS`
        *   The timestamp reflects when the scan execution started.
    *   If the file doesn't exist, it's created without an initial delimiter.
*   **TODO Entry Format:**
    ```markdown
    ### TODO: {name}

    **Source:** `{file_path}:{line_number}`

    **Description:**
    {LLM_generated_description}

    **Code Block:**
    ```python
    {original_code_block}
    ```
    ---
    ```
*   **Error Entry Format:** See Section 2.7.
*   **Nested TODO Output:** Nested TODOs are represented hierarchically within their parent's entry using Markdown block quotes and potentially lower heading levels. (See Section 2.8).

**2.5. Command-Line Interface (CLI)**
*   **Command:** `generate-todos`
*   **Arguments:**
    *   `-i <path>` / `--input <path>` (Optional): Path to the specific file or directory to scan. If omitted, defaults to the Current Working Directory (CWD).
    *   `-o <file>` / `--output <file>` (Optional): Path to the output Markdown file. If omitted, defaults to `TODO.md` in the CWD.
    *   `-n <name>` / `--name <name>` (Optional): Custom name to include in the append delimiter. If omitted, the delimiter contains only the timestamp.

**2.6. Configuration File**
*   **Location:** The tool looks for a file named `gt_config.json` in the CWD.
*   **Format:** JSON object containing key-value pairs.
*   **Supported Settings:**
    *   `input_path` (string): Default input path if `-i` is not provided.
    *   `output_file` (string): Default output file path if `-o` is not provided.
    *   `delimiter_name` (string): Default delimiter name if `-n` is not provided.
    *   `max_code_block_chars` (integer): Maximum character count for a code block before skipping LLM processing (See Section 2.10). Provide a sensible default (e.g., 10000) if not set.
*   **Precedence:**
    1.  CLI arguments override all other settings.
    2.  Settings in `gt_config.json` override built-in defaults.
    3.  Built-in defaults are used if no CLI argument or config setting is found.

**2.7. Error Handling & Reporting**
*   Errors encountered during parsing are reported within the output Markdown file.
*   **Invalid Marker Syntax:** If a line matches `# TODO-` but fails validation.
    ```markdown
    ### ERROR: Invalid TODO Marker

    **Source:** `{file_path}:{line_number}`

    **Problematic Line:**
    ```
    {invalid_marker_line}
    ```

    **Reason:**
    {explanation_of_validation_failure}

    ---
    ```
*   **Unterminated Span:** If a valid start marker is found but no corresponding `# TODO-end` is found before the end of the file. Any spans still on the stack at EOF are reported.
    ```markdown
    ### ERROR: Unterminated TODO Span

    **Source:** `{file_path}:{line_number}`

    **Starting Marker:**
    ```
    {valid_start_marker_line}
    ```

    **Reason:**
    Found a valid TODO start marker, but no corresponding `# TODO-end` was found before the end of the file.

    ---
    ```
*   **Skipped Span (Size Limit):** If a code block exceeds `max_code_block_chars`.
    ```markdown
    ### WARNING: TODO Skipped (Size Limit Exceeded)

    **Source:** `{file_path}:{line_number}`

    **Starting Marker:**
    ```
    {valid_start_marker_line}
    ```

    **Reason:**
    The code block contains {actual_char_count} characters, exceeding the configured limit of {limit_char_count}. LLM processing was skipped for this TODO. Consider reducing the code scope between the markers or increasing the limit in `gt_config.json`.

    ---
    ```
*   **Console Warnings:** Warnings for skipped spans should also be logged to the console.

**2.8. Nesting Handling**
*   The parsing logic (using a stack) must correctly identify nested `# TODO-...` spans.
*   Each span (outer and inner) is processed independently by the LLM, receiving only its respective code block.
*   The Markdown output must reflect the nesting structure. Example using block quotes:
    ```markdown
    ### TODO: outer-task
    {... outer details ...}
    > #### TODO: inner-task
    > {... inner details ...}
    > --- *(End of inner-task)*
    --- *(End of outer-task)*
    ```

**2.9. LLM Scope**
*   The code block provided to the LLM must *only* contain the content strictly between the start and end markers. No surrounding code context is included.

**2.10. Constraints**
*   **Code Block Size Limit:**
    *   Before sending a code block to the LLM, check its character count against the `max_code_block_chars` limit (from config or default).
    *   If the limit is exceeded, do not call the LLM. Log a console warning and add the specific "WARNING: TODO Skipped (Size Limit Exceeded)" entry to the Markdown output file.

**3. Technical Architecture**

*   **Language:** Python 3.x
*   **Key Libraries:**
    *   `os`: For file system navigation (`os.walk`).
    *   `re`: For regular expression matching of markers.
    *   `json`: For parsing `gt_config.json`.
    *   `datetime`: For generating timestamps.
    *   `argparse`: For parsing CLI arguments.
    *   `pathspec`: For parsing `.gitignore` files.
    *   User's `pydantic_ai` library/module: For LLM interaction.
*   **Core Parsing Algorithm:** Stateful, line-by-line processing of files using a stack to manage active TODO spans and handle nesting.
*   **File Handling:** Standard Python file I/O (`open` with `utf-8` encoding recommended).
*   **Configuration Loading:** Check for `gt_config.json`, parse if exists, merge with CLI args and defaults based on precedence rules.

**4. Data Structures**

*   **Intermediate TODO Span Representation (during parsing, e.g., on the stack):**
    *   `name` (str)
    *   `prompt` (str or None)
    *   `start_line` (int)
    *   `code_lines` (list[str]): Lines collected so far.
    *   `children` (list[CompletedTodoSpan]): List of nested TODOs finalized within this span.
*   **Completed TODO Span Representation (after popping from stack or for final output):**
    *   `name` (str)
    *   `prompt` (str or None)
    *   `start_line` (int)
    *   `file_path` (str)
    *   `code_block` (str): Joined code lines.
    *   `children` (list[CompletedTodoSpan])
    *   `llm_description` (str): Populated after LLM call.
*   **Error Representation:**
    *   `error_type` (enum/str: 'InvalidMarker', 'UnterminatedSpan', 'SkippedSize')
    *   `file_path` (str)
    *   `line_number` (int)
    *   `details` (dict): Containing specific info like `problematic_line`, `reason`, `start_marker`, `actual_chars`, `limit_chars`.

**5. Detailed Logic Flows**

*   **Startup:**
    1.  Parse CLI arguments using `argparse`.
    2.  Determine project root (CWD).
    3.  Attempt to load and parse `gt_config.json` from CWD.
    4.  Determine effective settings (input path, output file, delimiter name, max chars) using defined precedence.
    5.  Attempt to load and parse `.gitignore` from CWD using `pathspec`.
*   **File Scanning:**
    1.  Initialize an empty list for all results (`all_results = []`).
    2.  Use `os.walk` on the effective input path.
    3.  For each directory/file, check against the loaded `pathspec` (`.gitignore` rules). Prune ignored directories from `os.walk`, skip ignored files.
    4.  If a non-ignored file ends with `.py`:
        *   Call the File Parsing function (see below).
        *   Append the results (parsed TODOs and errors from that file) to `all_results`.
*   **File Parsing (per file):**
    1.  Initialize `file_todos = []`, `file_errors = []`, `active_spans_stack = []`.
    2.  Compile regex patterns for start/end markers.
    3.  Iterate through file lines `enumerate(file, 1)`.
    4.  Apply logic described in Section 2.2 (check start marker, check end marker, handle regular lines, manage stack).
    5.  Append detected errors (invalid marker, unexpected end) to `file_errors`.
    6.  Append completed top-level spans to `file_todos` (nested children are attached).
    7.  After loop, check stack for unterminated spans and add errors to `file_errors`.
    8.  Return `file_todos` and `file_errors`.
*   **LLM Processing & Output Generation:**
    1.  Iterate through `all_results`.
    2.  For each `CompletedTodoSpan` object (traverse nested structure recursively):
        *   Check code block size against `max_code_block_chars`.
        *   If too large, convert it to a "SkippedSize" error object.
        *   If within limit:
            *   Construct the LLM prompt string.
            *   Call the `pydantic_ai` layer with the prompt.
            *   Store the returned description in the object (`llm_description`).
            *   Handle potential errors during LLM call (log appropriately, maybe create a specific error entry).
    3.  Open the effective output file in append mode (`'a'`).
    4.  If the file was not empty before opening (or if this is not the first run conceptually), write the timestamp/name delimiter.
    5.  Iterate through `all_results` again.
    6.  For each item (TODO or Error), format it according to the Markdown structures defined in Sections 2.4, 2.7, 2.8. Write the formatted string to the file. Ensure nested TODOs are formatted within their parent's block.

**6. Error Handling Strategy (Summary)**

*   **Invalid Markers:** Detected during line-by-line parsing. Do not process the potential span. Report in Markdown output.
*   **Unterminated Spans:** Detected at the end of file processing if the stack is not empty. Report in Markdown output.
*   **Unexpected End Markers:** Detected if `# TODO-end` is found when the stack is empty. Report in Markdown output.
*   **Oversized Code Blocks:** Detected before LLM call. Skip LLM, log warning, report in Markdown output.
*   **File I/O Errors:** Handle potential `FileNotFoundError` (for input path, config, gitignore) or permission errors gracefully (e.g., print error message and exit).
*   **LLM Errors:** Catch exceptions during the call to the `pydantic_ai` layer. Log the error. Consider adding a specific error entry to the Markdown file indicating LLM failure for that TODO.
*   **Configuration Errors:** Handle invalid JSON in `gt_config.json` (log error, proceed with defaults/CLI args).

**7. Testing Plan**

*   **Unit Tests:**
    *   Test marker regex patterns (valid/invalid cases).
    *   Test the core stateful parsing logic (stack operations, code line collection, nesting).
    *   Test individual validation rules for markers.
    *   Test `.gitignore` pattern matching logic (if implemented manually, otherwise test integration with `pathspec`).
    *   Test configuration loading and precedence logic.
    *   Test prompt string construction.
*   **Integration Tests:**
    *   Test CLI argument parsing.
    *   Test reading from and appending to the Markdown output file.
    *   Test interaction with `pathspec` for file filtering based on a sample `.gitignore`.
    *   Test handling of `gt_config.json`.
    *   *(Optional)* Mock the `pydantic_ai` layer to test the flow of data to/from it.
*   **End-to-End Tests:**
    *   Run the CLI tool on sample Python projects with various structures:
        *   No markers.
        *   Simple markers.
        *   Nested markers.
        *   Markers with custom prompts.
        *   Files containing invalid markers.
        *   Files containing unterminated spans.
        *   Spans with code blocks exceeding the size limit.
        *   Projects with a `.gitignore` file.
    *   Verify the content and structure of the generated Markdown file against expected output.

**8. Future Considerations (Optional)**

*   More sophisticated context awareness for LLM (e.g., including surrounding function/class definitions).
*   Support for TODO markers in other languages.
*   More advanced `.gitignore` feature support if not using a library or if library limitations are hit.
*   Interactive mode (e.g., confirming overwrites).
*   Configuration option for the default LLM prompt.
*   Allowing different output formats (e.g., JSON).

---
