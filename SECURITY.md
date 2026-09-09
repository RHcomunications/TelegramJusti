# TelegramJusti Security Policy

## Overview

This document outlines the security practices and guidelines followed by the TelegramJusti NVDA add-on to prevent code injection and other security vulnerabilities.

## Security Principles

### Code Injection Prevention (CWE-943)

- **No `eval()`, `exec()`, or `compile()`**: The add-on never evaluates or executes Python code from user-controlled data, object names, or UI elements.
- **No dynamic imports**: All imports are static and declared at the top of each module.
- **No `pickle.loads()` or `marshal.loads()`**: The add-on does not deserialize untrusted data.
- **No `os.system()` or `subprocess` calls**: The add-on does not execute system commands.

### Input Validation (CWE-20)

- **String length limits**: Object names are capped at `MAX_NAME_LENGTH` (2000 characters) to prevent buffer overflow-style attacks through excessively long UI names.
- **Safe string operations**: All string manipulations use Python's built-in safe string methods. No string concatenation with executable code.
- **Config validation**: Configuration values are validated through `ConfigObj` schema, preventing arbitrary code execution through config files.

### Secure Configuration (CWE-359)

- **ConfigObj validation**: Configuration is read through `ConfigObj` with a strict schema specification (`spec`), which does not execute Python expressions.
- **No `os.remove()` on user-controlled paths**: File deletion only occurs on known-safe configuration paths after explicit error handling.
- **Exception handling**: All `except` clauses use `except Exception:` to avoid catching `KeyboardInterrupt` or `SystemExit`.

### UI Automation Safety (CWE-1167)

- **Safe object name processing**: Object names from UI Automation are treated as data, not code. They are only read and displayed, never evaluated.
- **`TextWindow` uses `SetValue()`**: Text is set via `wx.TextCtrl.SetValue()`, not through HTML or RTF rendering that could execute scripts.
- **No `browseableMessage` with untrusted content**: The add-on does not use `browseableMessage` for user-controlled content.

### API Stability and Security (NVDA Guidelines)

- **No private symbols**: The add-on uses only public NVDA API symbols (no underscore-prefixed names).
- **Bundled dependencies**: `configobj` is bundled as a pip dependency within the add-on package.
- **Manifest compliance**: All manifest fields are declared with proper values.

## Known CVE References

- **CVE-2026-28211** (CWE-943): NVDA Dev & Test Toolbox Log Reader - Python expressions in log entries were evaluated, leading to arbitrary code execution. This add-on follows the same pattern of not evaluating any user-controlled data.
- **CVE-2025-26326** (CWE-287): NVDA Remote weak password vulnerability. This add-on does not implement network authentication or remote access features.
- **GHSA-xg6w-23rw-39r8**: Reflected XSS through `browseableMessage`. This add-on does not use `browseableMessage` for user content.

## Security Review Checklist

Before publishing or updating:

- [ ] No `eval()`, `exec()`, `compile()` in codebase
- [ ] No `pickle.loads()`, `marshal.loads()` on external data
- [ ] No `os.system()`, `subprocess` calls
- [ ] No `__import__()` with dynamic module names
- [ ] All `except` clauses use `except Exception:` (not bare `except:`)
- [ ] Configuration validation schema is strict
- [ ] Object name processing has length limits
- [ ] Manifest declares all required fields
- [ ] No use of private NVDA API symbols
- [ ] Dependencies are bundled or properly declared

## Reporting Security Issues

Security issues should be reported through NVDA's official security policy:
- GitHub Security Advisory: https://github.com/nvaccess/nvda/security/advisories
- Email: info@nvaccess.org

## License

This security policy is part of the TelegramJusti add-on and is distributed under the GPL v2 license.
