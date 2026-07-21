#!/usr/bin/env bash
set -Eeuo pipefail

release_url="${AMS_RELEASE_URL:-https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/adaptive-master-subagent-orchestration-3.08.zip}"
expected_sha256="${AMS_EXPECTED_SHA256:-e45eed1762ed24d1a0f671d9fb7424558694f0bef557aaca97f0cc0828d07be6}"
skill_name="adaptive-master-subagent-orchestration"
skill_home="${AMS_SKILL_HOME:-${HOME:?HOME is not set}/.agents/skills}"
destination="${skill_home}/${skill_name}"

required_files=(
  "SKILL.md"
  "VERSION"
  "agents/openai.yaml"
  "references/intensity-control.md"
  "references/package-maintenance.md"
  "references/profile-management.md"
  "references/project-control.md"
  "references/runtime-core.md"
  "references/zergling-rush.md"
)

fail() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

for command_name in curl unzip zipinfo; do
  command -v "$command_name" >/dev/null 2>&1 || fail "Required command not found: ${command_name}"
done

[[ "$expected_sha256" =~ ^[0-9A-Fa-f]{64}$ ]] || fail "AMS_EXPECTED_SHA256 must contain exactly 64 hexadecimal characters."
expected_sha256="$(printf '%s' "$expected_sha256" | tr '[:upper:]' '[:lower:]')"

mkdir -p "$skill_home"
stage_root="$(mktemp -d "${skill_home}/.ams-install.XXXXXXXX")"
archive_path="${stage_root}/package.zip"
extract_root="${stage_root}/extract"
backup_path="${skill_home}/.${skill_name}.backup-$(date +%Y%m%d%H%M%S)-$$"
existing_moved=0

cleanup() {
  rm -rf -- "$stage_root"
}
trap cleanup EXIT INT TERM HUP

mkdir -p "$extract_root"

curl_args=(
  --fail --location --silent --show-error
  --retry 3 --retry-delay 1
  --connect-timeout 15 --max-time 300
  -H "Accept: application/octet-stream"
  -H "User-Agent: AMS-3.08-Installer"
)
if [[ -n "${GITHUB_TOKEN:-}" ]]; then
  curl_args+=( -H "Authorization: Bearer ${GITHUB_TOKEN}" )
fi

printf 'Downloading Adaptive Master-Subagent Orchestration 3.08...\n'
if ! curl "${curl_args[@]}" "$release_url" -o "$archive_path"; then
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    fail "Release download failed. Verify the URL and that GITHUB_TOKEN can read the repository."
  fi
  fail "Release download failed. If the repository or release is private, set GITHUB_TOKEN to a token with repository read access."
fi
[[ -s "$archive_path" ]] || fail "The release download was empty."

if command -v sha256sum >/dev/null 2>&1; then
  actual_sha256="$(sha256sum "$archive_path" | awk '{print tolower($1)}')"
elif command -v shasum >/dev/null 2>&1; then
  actual_sha256="$(shasum -a 256 "$archive_path" | awk '{print tolower($1)}')"
else
  fail "A SHA-256 tool is required (sha256sum or shasum)."
fi
[[ "$actual_sha256" == "$expected_sha256" ]] || fail "Release checksum mismatch. Expected ${expected_sha256}; received ${actual_sha256}."

archive_list="${stage_root}/entries.txt"
zipinfo -1 "$archive_path" > "$archive_list"
entry_name_count="$(wc -l < "$archive_list" | tr -d '[:space:]')"
(( entry_name_count > 0 && entry_name_count <= 500 )) || fail "The release archive has an invalid entry count: ${entry_name_count}"

if LC_ALL=C sort "$archive_list" | uniq -d | grep -q .; then
  fail "The release archive contains duplicate paths."
fi

while IFS= read -r name; do
  [[ -n "$name" ]] || fail "The release archive contains an empty path."
  [[ "$name" != *\\* ]] || fail "The release archive contains a backslash path: $name"
  [[ "$name" != /* && ! "$name" =~ ^[A-Za-z]: ]] || fail "The release archive contains an absolute path: $name"
  [[ "$name" == "${skill_name}/"* ]] || fail "The release archive contains an unexpected top-level path: $name"

  IFS='/' read -r -a components <<< "$name"
  for component in "${components[@]}"; do
    [[ "$component" != ".." ]] || fail "The release archive contains path traversal: $name"
  done
done < "$archive_list"

if zipinfo -l "$archive_path" | awk '$1 ~ /^l/ { found=1 } END { exit(found ? 0 : 1) }'; then
  fail "The release archive contains an unsupported symbolic link."
fi

read -r entry_count expanded_bytes < <(
  unzip -l "$archive_path" | awk '
    $1 ~ /^[0-9]+$/ && $2 ~ /-/ && $3 ~ /:/ { count += 1; total += $1 }
    END { print count + 0, total + 0 }
  '
)
(( entry_count <= 500 )) || fail "The release archive contains too many expanded entries: ${entry_count}"
(( expanded_bytes <= 104857600 )) || fail "The expanded release exceeds the 100 MiB safety limit."

for required in "${required_files[@]}"; do
  grep -Fqx "${skill_name}/${required}" "$archive_list" || fail "The release archive is missing required file: ${skill_name}/${required}"
done

unzip -q "$archive_path" -d "$extract_root"
candidate="${extract_root}/${skill_name}"
[[ -d "$candidate" && ! -L "$candidate" ]] || fail "The extracted package root is missing or redirected."

if find "$candidate" -type l -print -quit | grep -q .; then
  fail "The extracted package contains an unsupported symbolic link."
fi
for required in "${required_files[@]}"; do
  [[ -f "${candidate}/${required}" && ! -L "${candidate}/${required}" ]] || fail "The extracted package is missing required file: ${required}"
done

if [[ -e "$destination" ]]; then
  [[ ! -e "$backup_path" ]] || fail "Unexpected backup collision: ${backup_path}"
  mv -- "$destination" "$backup_path"
  existing_moved=1
fi

if ! mv -- "$candidate" "$destination"; then
  if (( existing_moved == 1 )) && [[ ! -e "$destination" && -e "$backup_path" ]]; then
    mv -- "$backup_path" "$destination"
    existing_moved=0
  fi
  fail "Installation failed while replacing the skill directory."
fi

if (( existing_moved == 1 )); then
  rm -rf -- "$backup_path"
fi

printf 'Installed Adaptive Master-Subagent Orchestration 3.08 to:\n  %s\n' "$destination"
printf 'Restart or reload Codex before using the updated skill.\n'
