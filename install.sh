#!/usr/bin/env bash
set -Eeuo pipefail

repo_owner="InsecurePassword"
repo_name="Codex-Adaptive-Master-Subagent-Orchestration"
package_version="3.09"
repo_branch="main"
asset_name="adaptive-master-subagent-orchestration-${package_version}.zip"
default_package_url="https://github.com/${repo_owner}/${repo_name}/raw/refs/heads/${repo_branch}/${asset_name}"
package_url="${AMS_PACKAGE_URL:-${AMS_RELEASE_URL:-$default_package_url}}"
expected_sha256="${AMS_EXPECTED_SHA256:-f2bfacac26d39bf21ce492f181bb4c51e9bc3a6b5d7cc3d7b18276d2c1a4d018}"
user_agent="AMS-${package_version}-Installer"
skill_name="adaptive-master-subagent-orchestration"
skill_home="${AMS_SKILL_HOME:-${HOME:?HOME is not set}/.agents/skills}"
codex_home="${CODEX_HOME:-${HOME}/.codex}"
destination="${skill_home}/${skill_name}"
agent_home="${codex_home}/agents"
managed_marker="# managed-by: adaptive-master-subagent-orchestration"
max_archive_bytes=10485760
max_expanded_bytes=104857600

profile_files=(
  "ams_sol_low.toml"
  "ams_sol_medium.toml"
  "ams_sol_high.toml"
  "ams_sol_xhigh.toml"
  "ams_sol_max.toml"
  "ams_terra_low.toml"
  "ams_terra_medium.toml"
  "ams_terra_high.toml"
  "ams_terra_xhigh.toml"
  "ams_terra_max.toml"
  "ams_luna_low.toml"
  "ams_luna_medium.toml"
  "ams_luna_high.toml"
  "ams_luna_xhigh.toml"
  "ams_luna_max.toml"
  "ams_spark_low.toml"
  "ams_spark_medium.toml"
  "ams_spark_high.toml"
)

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
for profile_file in "${profile_files[@]}"; do
  required_files+=("assets/agent-profiles/${profile_file}")
done

fail() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

for command_name in curl unzip zipinfo awk sort cmp mktemp; do
  command -v "$command_name" >/dev/null 2>&1 || fail "Required command not found: ${command_name}"
done

[[ "$expected_sha256" =~ ^[0-9A-Fa-f]{64}$ ]] || fail "AMS_EXPECTED_SHA256 must contain exactly 64 hexadecimal characters."
expected_sha256="$(printf '%s' "$expected_sha256" | tr '[:upper:]' '[:lower:]')"

[[ ! -L "$skill_home" ]] || fail "Skill parent is redirected: ${skill_home}"
[[ ! -e "$skill_home" || -d "$skill_home" ]] || fail "Skill parent is not a directory: ${skill_home}"
mkdir -p "$skill_home"

[[ ! -L "$codex_home" ]] || fail "CODEX_HOME is redirected: ${codex_home}"
[[ ! -e "$codex_home" || -d "$codex_home" ]] || fail "CODEX_HOME is not a directory: ${codex_home}"
mkdir -p "$codex_home"

[[ ! -L "$agent_home" ]] || fail "Agent registry is redirected: ${agent_home}"
[[ ! -e "$agent_home" || -d "$agent_home" ]] || fail "Agent registry is not a directory: ${agent_home}"
mkdir -p "$agent_home"

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
profile_backup_root=""
existing_moved=0
candidate_installed=0
committed=0
profile_created=()
profile_backup_targets=()
profile_backup_paths=()
profile_temps=()

cleanup() {
  status=$?
  trap - EXIT INT TERM HUP

  if (( committed == 0 )); then
    for temp_path in "${profile_temps[@]}"; do
      [[ -n "$temp_path" ]] && rm -f -- "$temp_path" 2>/dev/null || true
    done

    for created_path in "${profile_created[@]}"; do
      [[ -n "$created_path" ]] && rm -f -- "$created_path" 2>/dev/null || true
    done

    if (( ${#profile_backup_targets[@]} > 0 )); then
      for (( i=${#profile_backup_targets[@]}-1; i>=0; i-- )); do
        target_path=${profile_backup_targets[$i]}
        saved_path=${profile_backup_paths[$i]}
        rm -f -- "$target_path" 2>/dev/null || true
        if [[ -f "$saved_path" && ! -L "$saved_path" ]]; then
          mv -- "$saved_path" "$target_path" 2>/dev/null || true
        fi
      done
    fi

    if (( candidate_installed == 1 )) && [[ -d "$destination" && ! -L "$destination" ]]; then
      rm -rf -- "$destination" 2>/dev/null || true
    fi
    if (( existing_moved == 1 )) && [[ ! -e "$destination" && ! -L "$destination" && -d "$backup_path" && ! -L "$backup_path" ]]; then
      mv -- "$backup_path" "$destination" 2>/dev/null || true
    fi
  fi

  [[ -z "$profile_backup_root" ]] || rm -rf -- "$profile_backup_root" 2>/dev/null || true
  [[ -z "$stage_root" ]] || rm -rf -- "$stage_root" 2>/dev/null || true
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
profile_backup_root="$(mktemp -d "${agent_home}/.ams-profile-backup.XXXXXXXX")"
mkdir -p "$extract_root"

common_curl_args=(
  --fail --location --silent --show-error
  --retry 3 --retry-delay 1
  --connect-timeout 15 --max-time 300
  --max-filesize "$max_archive_bytes"
  -H "User-Agent: ${user_agent}"
)

printf 'Downloading Adaptive Master-Subagent Orchestration %s...\n' "$package_version"
if ! curl "${common_curl_args[@]}" -H "Accept: application/octet-stream" "$package_url" -o "$archive_path"; then
  fail "Package download failed. Verify the repository raw-file URL or set AMS_PACKAGE_URL to the exact package location."
fi
[[ -s "$archive_path" ]] || fail "The package download was empty."
archive_bytes="$(wc -c < "$archive_path" | tr -d '[:space:]')"
(( archive_bytes <= max_archive_bytes )) || fail "The compressed package exceeds the 10 MiB safety limit."

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
zipinfo -1 "$archive_path" > "$archive_list" || fail "The release archive is not a readable ZIP file."
awk -v files="$archive_files" -v dirs="$archive_dirs" '
  /\/$/ { print > dirs; next }
  { print > files }
' "$archive_list"
for required in "${required_files[@]}"; do
  printf '%s/%s\n' "$skill_name" "$required"
done | LC_ALL=C sort > "$expected_list"
LC_ALL=C sort "$archive_files" -o "$archive_files"
cmp -s "$expected_list" "$archive_files" || fail "The release archive file set does not exactly match the ${package_version} package contract."

if ! awk -v root="${skill_name}/" -v agents="${skill_name}/agents/" -v assets="${skill_name}/assets/" -v profiles="${skill_name}/assets/agent-profiles/" -v refs="${skill_name}/references/" '
  $0 != root && $0 != agents && $0 != assets && $0 != profiles && $0 != refs { exit 1 }
  seen[$0]++ { exit 1 }
' "$archive_dirs"; then
  fail "The release archive contains an unexpected or duplicate directory entry."
fi

if zipinfo -l "$archive_path" | awk '$1 ~ /^l/ { found=1 } END { exit(found ? 0 : 1) }'; then
  fail "The release archive contains an unsupported symbolic link."
fi
unzip -tqq "$archive_path" </dev/null || fail "The release archive failed integrity or encryption validation."

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

for profile_file in "${profile_files[@]}"; do
  source_profile="${candidate}/assets/agent-profiles/${profile_file}"
  [[ -f "$source_profile" && ! -L "$source_profile" ]] || fail "Bundled profile is missing or redirected: ${profile_file}"
  first_line=""
  IFS= read -r first_line < "$source_profile" || true
  [[ "$first_line" == "$managed_marker" ]] || fail "Bundled profile lacks the required managed marker: ${profile_file}"
done

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

mv -- "$candidate" "$destination" || fail "Installation failed while replacing the skill directory."
candidate_installed=1

profiles_changed=0
profiles_unchanged=0
for profile_file in "${profile_files[@]}"; do
  source_profile="${destination}/assets/agent-profiles/${profile_file}"
  target_profile="${agent_home}/${profile_file}"

  [[ ! -L "$target_profile" ]] || fail "Refusing to replace a redirected agent profile: ${target_profile}"
  if [[ -e "$target_profile" && ! -f "$target_profile" ]]; then
    fail "Agent profile target is not a regular file: ${target_profile}"
  fi

  if [[ -f "$target_profile" ]] && cmp -s "$source_profile" "$target_profile"; then
    ((profiles_unchanged+=1))
    continue
  fi

  if [[ -f "$target_profile" ]]; then
    first_line=""
    IFS= read -r first_line < "$target_profile" || true
    [[ "$first_line" == "$managed_marker" ]] || fail "Refusing to overwrite an unrecognized or user-authored profile: ${target_profile}"
    saved_profile="${profile_backup_root}/${profile_file}"
    mv -- "$target_profile" "$saved_profile"
    profile_backup_targets+=("$target_profile")
    profile_backup_paths+=("$saved_profile")
  else
    profile_created+=("$target_profile")
  fi

  temp_profile="$(mktemp "${agent_home}/.${profile_file}.ams-install.XXXXXXXX")"
  profile_temps+=("$temp_profile")
  cp -- "$source_profile" "$temp_profile"
  cmp -s "$source_profile" "$temp_profile" || fail "Agent profile staging verification failed: ${profile_file}"
  mv -- "$temp_profile" "$target_profile"
  cmp -s "$source_profile" "$target_profile" || fail "Agent profile installation verification failed: ${profile_file}"
  ((profiles_changed+=1))
done

committed=1

if (( existing_moved == 1 )); then
  rm -rf -- "$backup_path" 2>/dev/null || true
  existing_moved=0
fi
rm -rf -- "$profile_backup_root" 2>/dev/null || true
profile_backup_root=""

printf 'Installed Adaptive Master-Subagent Orchestration %s to:\n  %s\n' "$package_version" "$destination"
printf 'Installed or updated %d AMS profiles; %d were already current.\n' "$profiles_changed" "$profiles_unchanged"
printf 'Agent profile registry:\n  %s\n' "$agent_home"
printf 'Restart or reload Codex before using the updated skill and profiles.\n'
