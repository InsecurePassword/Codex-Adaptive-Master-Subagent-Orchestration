#!/usr/bin/env bash
set -Eeuo pipefail

repo_owner="InsecurePassword"
repo_name="Codex-Adaptive-Master-Subagent-Orchestration"
package_version="3.09"
release_tag="ReleaseZip"
asset_name="adaptive-master-subagent-orchestration-${package_version}.zip"
default_release_url="https://github.com/${repo_owner}/${repo_name}/releases/download/${release_tag}/${asset_name}"
release_url="${AMS_RELEASE_URL:-$default_release_url}"
expected_sha256="${AMS_EXPECTED_SHA256:-3e3e8dc3142d5bc2411a4703982150941816c3669d5f0bb01bab2099f7a88373}"
user_agent="AMS-${package_version}-Installer"
skill_name="adaptive-master-subagent-orchestration"
skill_home="${AMS_SKILL_HOME:-${HOME:?HOME is not set}/.agents/skills}"
destination="${skill_home}/${skill_name}"
max_archive_bytes=10485760
max_expanded_bytes=104857600

required_files=(
  "SKILL.md"
  "VERSION"
  "agents/openai.yaml"
  "references/hierarchy-control.md"
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

for command_name in curl unzip zipinfo awk sort cmp; do
  command -v "$command_name" >/dev/null 2>&1 || fail "Required command not found: ${command_name}"
done

[[ "$expected_sha256" =~ ^[0-9A-Fa-f]{64}$ ]] || fail "AMS_EXPECTED_SHA256 must contain exactly 64 hexadecimal characters."
expected_sha256="$(printf '%s' "$expected_sha256" | tr '[:upper:]' '[:lower:]')"

mkdir -p "$skill_home"
lock_dir="${skill_home}/.${skill_name}.install.lock"
[[ ! -L "$lock_dir" ]] || fail "Installer lock path is redirected: ${lock_dir}"
if ! mkdir "$lock_dir" 2>/dev/null; then
  fail "Another installation is active or a stale lock exists: ${lock_dir}"
fi
printf '%s\n' "pid=$$" "host=$(hostname 2>/dev/null || printf unknown)" > "${lock_dir}/owner"

stage_root=""
archive_path=""
extract_root=""
backup_path=""
existing_moved=0
candidate_installed=0
committed=0

cleanup() {
  status=$?
  trap - EXIT INT TERM HUP
  if (( committed == 0 )); then
    if (( candidate_installed == 1 )) && [[ -d "$destination" && ! -L "$destination" ]]; then
      rm -rf -- "$destination" || true
    fi
    if (( existing_moved == 1 )) && [[ ! -e "$destination" && ! -L "$destination" && -d "$backup_path" && ! -L "$backup_path" ]]; then
      /bin/mv -- "$backup_path" "$destination" || printf 'Error: rollback could not restore %s\n' "$destination" >&2
    fi
  fi
  if [[ -n "$stage_root" ]]; then
    rm -rf -- "$stage_root" 2>/dev/null || true
  fi
  rm -rf -- "$lock_dir" 2>/dev/null || true
  exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP

stage_root="$(mktemp -d "${skill_home}/.ams-install.XXXXXXXX")"
archive_path="${stage_root}/package.zip"
extract_root="${stage_root}/extract"
backup_path="${skill_home}/.${skill_name}.backup-$(date +%Y%m%d%H%M%S)-$$"
mkdir -p "$extract_root"

common_curl_args=(
  --fail --location --silent --show-error
  --retry 3 --retry-delay 1
  --connect-timeout 15 --max-time 300
  --max-filesize "$max_archive_bytes"
  -H "User-Agent: ${user_agent}"
)

download_url="$release_url"
download_accept="application/octet-stream"
if [[ -n "${GITHUB_TOKEN:-}" && -z "${AMS_RELEASE_URL:-}" ]]; then
  metadata_url="https://api.github.com/repos/${repo_owner}/${repo_name}/releases/tags/${release_tag}"
  metadata="$({ curl "${common_curl_args[@]}" \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${GITHUB_TOKEN}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "$metadata_url"; } 2>/dev/null)" || fail "Unable to resolve the private release metadata. Verify GITHUB_TOKEN repository read access."
  download_url="$(printf '%s' "$metadata" | awk -v target="$asset_name" '
    BEGIN { RS="\\{"; FS="," }
    index($0, "\"name\":\"" target "\"") {
      for (i=1; i<=NF; i++) {
        field=$i
        gsub(/[[:space:]]/, "", field)
        if (field ~ /^"url":"https:\/\/api\.github\.com\/repos\/[^\"]+\/releases\/assets\/[0-9]+"$/) {
          sub(/^"url":"/, "", field)
          sub(/"$/, "", field)
          print field
          exit
        }
      }
    }
  ')"
  [[ -n "$download_url" ]] || fail "Release asset '${asset_name}' was not found in tag '${release_tag}'."
fi

headers=( -H "Accept: ${download_accept}" )
if [[ -n "${GITHUB_TOKEN:-}" ]]; then
  headers+=( -H "Authorization: Bearer ${GITHUB_TOKEN}" -H "X-GitHub-Api-Version: 2022-11-28" )
fi

printf 'Downloading Adaptive Master-Subagent Orchestration %s...\n' "$package_version"
if ! curl "${common_curl_args[@]}" "${headers[@]}" "$download_url" -o "$archive_path"; then
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    fail "Release download failed. Verify the release and GITHUB_TOKEN repository read access."
  fi
  fail "Release download failed. If access is private, set GITHUB_TOKEN to a token with repository read access."
fi
[[ -s "$archive_path" ]] || fail "The release download was empty."
archive_bytes="$(wc -c < "$archive_path" | tr -d '[:space:]')"
(( archive_bytes <= max_archive_bytes )) || fail "The compressed release exceeds the 10 MiB safety limit."

if command -v sha256sum >/dev/null 2>&1; then
  actual_sha256="$(sha256sum "$archive_path" | awk '{print tolower($1)}')"
elif command -v shasum >/dev/null 2>&1; then
  actual_sha256="$(shasum -a 256 "$archive_path" | awk '{print tolower($1)}')"
else
  fail "A SHA-256 tool is required (sha256sum or shasum)."
fi
[[ "$actual_sha256" == "$expected_sha256" ]] || fail "Release checksum mismatch. Expected ${expected_sha256}; received ${actual_sha256}."

archive_list="${stage_root}/entries.txt"
archive_files="${stage_root}/archive-files.txt"
archive_dirs="${stage_root}/archive-directories.txt"
expected_list="${stage_root}/expected.txt"
if ! zipinfo -1 "$archive_path" > "$archive_list"; then
  fail "The release archive is not a readable ZIP file."
fi
awk -v files="$archive_files" -v dirs="$archive_dirs" '
  /\/$/ { print > dirs; next }
  { print > files }
' "$archive_list"
for required in "${required_files[@]}"; do
  printf '%s/%s\n' "$skill_name" "$required"
done | LC_ALL=C sort > "$expected_list"
LC_ALL=C sort "$archive_files" -o "$archive_files"
if ! cmp -s "$expected_list" "$archive_files"; then
  fail "The release archive file set does not exactly match the ${package_version} package contract."
fi
if ! awk -v root="${skill_name}/" -v agents="${skill_name}/agents/" -v refs="${skill_name}/references/" '
  $0 != root && $0 != agents && $0 != refs { exit 1 }
  seen[$0]++ { exit 1 }
' "$archive_dirs"; then
  fail "The release archive contains an unexpected or duplicate directory entry."
fi

if zipinfo -l "$archive_path" | awk '$1 ~ /^l/ { found=1 } END { exit(found ? 0 : 1) }'; then
  fail "The release archive contains an unsupported symbolic link."
fi
if ! unzip -tqq "$archive_path" </dev/null; then
  fail "The release archive failed integrity or encryption validation."
fi

read -r entry_count expanded_bytes < <(
  unzip -l "$archive_path" | awk '
    $1 ~ /^[0-9]+$/ && $2 ~ /-/ && $3 ~ /:/ && $4 !~ /\/$/ { count += 1; total += $1 }
    END { print count + 0, total + 0 }
  '
)
(( entry_count == ${#required_files[@]} )) || fail "The release archive has an invalid expanded entry count: ${entry_count}"
(( expanded_bytes <= max_expanded_bytes )) || fail "The expanded release exceeds the 100 MiB safety limit."

unzip -q -o "$archive_path" -d "$extract_root"
candidate="${extract_root}/${skill_name}"
[[ -d "$candidate" && ! -L "$candidate" ]] || fail "The extracted package root is missing or redirected."
if find "$candidate" -type l -print -quit | grep -q .; then
  fail "The extracted package contains an unsupported symbolic link."
fi

actual_extracted="${stage_root}/extracted.txt"
: > "$actual_extracted"
while IFS= read -r -d '' file; do
  relative="${file#"${candidate}/"}"
  printf '%s/%s\n' "$skill_name" "$relative" >> "$actual_extracted"
done < <(find "$candidate" -type f -print0)
LC_ALL=C sort "$actual_extracted" -o "$actual_extracted"
cmp -s "$expected_list" "$actual_extracted" || fail "The extracted package file set does not match the ${package_version} package contract."

observed_version="$(tr -d '\r\n' < "${candidate}/VERSION")"
[[ "$observed_version" == "$package_version" ]] || fail "Unexpected package version. Expected ${package_version}; received '${observed_version}'."

if [[ -L "$destination" ]]; then
  fail "Refusing to replace a redirected existing skill path: ${destination}"
fi
if [[ -e "$destination" && ! -d "$destination" ]]; then
  fail "Refusing to replace a non-directory existing skill path: ${destination}"
fi
if [[ -e "$destination" ]]; then
  [[ ! -e "$backup_path" && ! -L "$backup_path" ]] || fail "Unexpected backup collision: ${backup_path}"
  mv -- "$destination" "$backup_path"
  existing_moved=1
fi

if ! mv -- "$candidate" "$destination"; then
  fail "Installation failed while replacing the skill directory."
fi
candidate_installed=1

if (( existing_moved == 1 )); then
  rm -rf -- "$backup_path"
  existing_moved=0
fi
committed=1

printf 'Installed Adaptive Master-Subagent Orchestration %s to:\n  %s\n' "$package_version" "$destination"
printf 'Restart or reload Codex before using the updated skill.\n'
