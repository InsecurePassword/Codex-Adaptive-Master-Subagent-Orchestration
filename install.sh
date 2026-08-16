#!/usr/bin/env bash
set -Eeuo pipefail

repo_owner="InsecurePassword"
repo_name="Codex-Adaptive-Master-Subagent-Orchestration"
repo_ref="main"
raw_base_url="https://github.com/${repo_owner}/${repo_name}/raw/refs/heads/main"
manifest_url="${raw_base_url}/install-manifest.txt"
package_version="3.10"
skill_name="adaptive-master-subagent-orchestration"
managed_marker="# managed-by: adaptive-master-subagent-orchestration"
user_agent="AMS-${package_version}-Tree-Installer"
skill_home="${AMS_SKILL_HOME:-${HOME:?HOME is not set}/.agents/skills}"
codex_home="${CODEX_HOME:-${HOME}/.codex}"
destination="${skill_home}/${skill_name}"
agent_home="${codex_home}/agents"
max_manifest_bytes=262144
max_file_bytes=1048576
max_total_bytes=104857600

profile_files=(
  "ams_sol_low.toml"
  "ams_sol_medium.toml"
  "ams_sol_high.toml"
  "ams_sol_xhigh.toml"
  "ams_sol_max.toml"
  "ams_daybreak_blue_max.toml"
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
  "references/configuration-maintenance.md"
  "references/daybreak-blue.md"
  "references/hierarchy-control.md"
  "references/intensity-control.md"
  "references/package-maintenance.md"
  "references/profile-management.md"
  "references/project-control.md"
  "references/project-governance.md"
  "references/root-execution-fallback.md"
  "references/runtime-core.md"
  "references/zergling-rush.md"
)
for profile_file in "${profile_files[@]}"; do
  required_files+=("assets/agent-profiles/${profile_file}")
done

is_authorized_prior_profile() {
  case "$1:$2" in
    "ams_spark_low.toml:b082a31f60627f4364b870c663deed670eff3c5c2adce03cb37b98452d9f0a1b"|\
    "ams_spark_medium.toml:c387ffa3c419d66e404ebcc9a7b82a21995690a43a12350a690e9aa13dd5f45a"|\
    "ams_spark_high.toml:bd0122c1f87b08ddb08b24df74979cf89c80c6be47627e9e0270ac2799c5320e")
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

fail() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

for command_name in curl awk sort cmp mktemp wc tr grep head tail od find dirname; do
  command -v "$command_name" >/dev/null 2>&1 || fail "Required command not found: ${command_name}"
done

sha256_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print tolower($1)}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print tolower($1)}'
  else
    fail "A SHA-256 tool is required (sha256sum or shasum)."
  fi
}

download_file() {
  local uri=$1
  local output=$2
  local description=$3
  if ! curl --fail --location --silent --show-error \
      --retry 3 --retry-delay 1 \
      --connect-timeout 15 --max-time 300 \
      -H "Accept: application/octet-stream" \
      -H "User-Agent: ${user_agent}" \
      "$uri" -o "$output"; then
    fail "${description} failed: ${uri}"
  fi
}

validate_manifest() {
  local manifest=$1
  local entries_output=$2
  local paths_output=$3
  local manifest_bytes bom last_byte line line_number hash length repo_path extra total_bytes

  [[ -f "$manifest" && ! -L "$manifest" ]] || fail "Install manifest is missing or redirected."
  manifest_bytes="$(wc -c < "$manifest" | tr -d '[:space:]')"
  (( manifest_bytes > 0 && manifest_bytes <= max_manifest_bytes )) || fail "Install manifest size is invalid: ${manifest_bytes} bytes"
  bom="$(head -c 3 "$manifest" | od -An -tx1 | tr -d ' \n')"
  [[ "$bom" != "efbbbf" ]] || fail "Install manifest must be UTF-8 without BOM."
  if LC_ALL=C grep -q $'\r' "$manifest"; then fail "Install manifest contains CR characters."; fi
  if od -An -tx1 "$manifest" | grep -qE '(^| )00( |$)'; then fail "Install manifest contains NUL bytes."; fi
  last_byte="$(tail -c 1 "$manifest" | od -An -tu1 | tr -d ' \n')"
  [[ "$last_byte" == "10" ]] || fail "Install manifest is missing final LF."

  : > "$entries_output"
  : > "$paths_output"
  line_number=0
  total_bytes=0
  while IFS= read -r line || [[ -n "$line" ]]; do
    line_number=$((line_number + 1))
    if (( line_number == 1 )); then
      [[ "$line" == "ams-install-manifest-v1" ]] || fail "Unsupported install manifest format."
      continue
    fi
    if (( line_number == 2 )); then
      [[ "$line" == $'version\t'"${package_version}" ]] || fail "Install manifest version does not match ${package_version}."
      continue
    fi
    [[ -n "$line" ]] || fail "Install manifest contains an unexpected blank line."
    IFS=$'\t' read -r hash length repo_path extra <<< "$line"
    [[ -z "${extra:-}" ]] || fail "Malformed install manifest line ${line_number}."
    [[ "$hash" =~ ^[0-9a-fA-F]{64}$ ]] || fail "Invalid SHA-256 on manifest line ${line_number}."
    [[ "$length" =~ ^[0-9]+$ ]] || fail "Invalid byte length on manifest line ${line_number}."
    (( length > 0 && length <= max_file_bytes )) || fail "Unsafe byte length on manifest line ${line_number}."
    case "$repo_path" in
      "${skill_name}/"*) ;;
      *) fail "Install manifest path escapes the skill tree: ${repo_path}" ;;
    esac
    total_bytes=$((total_bytes + length))
    (( total_bytes <= max_total_bytes )) || fail "Install manifest exceeds the total-size limit."
    printf '%s\t%s\t%s\n' "$(printf '%s' "$hash" | tr '[:upper:]' '[:lower:]')" "$length" "$repo_path" >> "$entries_output"
    printf '%s\n' "$repo_path" >> "$paths_output"
  done < "$manifest"

  (( line_number == ${#required_files[@]} + 2 )) || fail "Install manifest entry count is invalid."
}

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
candidate="${stage_root}/${skill_name}"
manifest_before="${stage_root}/install-manifest.before.txt"
manifest_after="${stage_root}/install-manifest.after.txt"
manifest_entries="${stage_root}/manifest-entries.tsv"
manifest_paths="${stage_root}/manifest-paths.txt"
expected_paths="${stage_root}/expected-paths.txt"
backup_path="${skill_home}/.${skill_name}.backup-$(date +%Y%m%d%H%M%S)-$$"
profile_backup_root="$(mktemp -d "${agent_home}/.ams-profile-backup.XXXXXXXX")"
mkdir -p "$candidate"

printf 'Reading the AMS %s install manifest from repository ref %s...\n' "$package_version" "$repo_ref"
download_file "$manifest_url" "$manifest_before" "Install manifest download"
validate_manifest "$manifest_before" "$manifest_entries" "$manifest_paths"

for required in "${required_files[@]}"; do
  printf '%s/%s\n' "$skill_name" "$required"
done | LC_ALL=C sort > "$expected_paths"
LC_ALL=C sort "$manifest_paths" -o "$manifest_paths"
cmp -s "$expected_paths" "$manifest_paths" || fail "Install manifest does not contain the exact required file set."

while IFS=$'\t' read -r expected_hash expected_length repo_path; do
  relative_path=${repo_path#"${skill_name}/"}
  target_path="${candidate}/${relative_path}"
  mkdir -p "$(dirname "$target_path")"
  temp_path="${target_path}.download"
  download_file "${raw_base_url}/${repo_path}" "$temp_path" "Download of ${repo_path}"
  [[ -f "$temp_path" && ! -L "$temp_path" ]] || fail "Downloaded path is not a safe regular file: ${repo_path}"
  actual_length="$(wc -c < "$temp_path" | tr -d '[:space:]')"
  [[ "$actual_length" == "$expected_length" ]] || fail "Downloaded length mismatch for ${repo_path}. Expected ${expected_length}; received ${actual_length}."
  actual_hash="$(sha256_file "$temp_path")"
  [[ "$actual_hash" == "$expected_hash" ]] || fail "Downloaded hash mismatch for ${repo_path}."
  mv -- "$temp_path" "$target_path"
done < "$manifest_entries"

download_file "$manifest_url" "$manifest_after" "Final install manifest download"
cmp -s "$manifest_before" "$manifest_after" || fail "The repository install manifest changed during download. Rerun the installer."

observed_version="$(tr -d '\r\n' < "${candidate}/VERSION")"
[[ "$observed_version" == "$package_version" ]] || fail "Unexpected source version. Expected ${package_version}; received '${observed_version}'."
for profile_file in "${profile_files[@]}"; do
  source_profile="${candidate}/assets/agent-profiles/${profile_file}"
  [[ -f "$source_profile" && ! -L "$source_profile" ]] || fail "Bundled profile is missing or redirected: ${profile_file}"
  first_line=""
  IFS= read -r first_line < "$source_profile" || true
  [[ "$first_line" == "$managed_marker" ]] || fail "Bundled profile lacks the required managed marker: ${profile_file}"
done

if [[ -L "$destination" ]]; then fail "Refusing to replace a redirected existing skill path: ${destination}"; fi
if [[ -e "$destination" && ! -d "$destination" ]]; then fail "Refusing to replace a non-directory existing skill path: ${destination}"; fi
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
  if [[ -e "$target_profile" && ! -f "$target_profile" ]]; then fail "Agent profile target is not a regular file: ${target_profile}"; fi

  if [[ -f "$target_profile" ]]; then
    source_hash="$(sha256_file "$source_profile")"
    target_hash="$(sha256_file "$target_profile")"
    if [[ "$source_hash" == "$target_hash" ]]; then
      profiles_unchanged=$((profiles_unchanged + 1))
      continue
    fi
    if ! is_authorized_prior_profile "$profile_file" "$target_hash"; then
      fail "Refusing to replace a differing profile without exact official provenance: ${target_profile}. Review, rename, remove, or manually reconcile it before retrying."
    fi
    saved_profile="${profile_backup_root}/${profile_file}"
    mv -- "$target_profile" "$saved_profile"
    profile_backup_targets+=("$target_profile")
    profile_backup_paths+=("$saved_profile")
  else
    profile_created+=("$target_profile")
  fi

  temp_profile="${agent_home}/.${profile_file}.ams-install.$$"
  profile_temps+=("$temp_profile")
  cp -- "$source_profile" "$temp_profile"
  source_hash="$(sha256_file "$source_profile")"
  [[ "$(sha256_file "$temp_profile")" == "$source_hash" ]] || fail "Agent profile staging verification failed: ${profile_file}"
  mv -- "$temp_profile" "$target_profile"
  [[ "$(sha256_file "$target_profile")" == "$source_hash" ]] || fail "Agent profile installation verification failed: ${profile_file}"
  profiles_changed=$((profiles_changed + 1))
done

committed=1
if (( existing_moved == 1 )); then
  rm -rf -- "$backup_path"
  existing_moved=0
fi
rm -rf -- "$profile_backup_root"
profile_backup_root=""

printf 'Installed Adaptive Master-Subagent Orchestration %s directly from the repository tree.\n' "$package_version"
printf 'Repository ref: %s\n' "$repo_ref"
printf 'Skill: %s\n' "$destination"
printf 'Profiles: %s (%s changed, %s unchanged)\n' "$agent_home" "$profiles_changed" "$profiles_unchanged"
printf 'Installation complete.\n'
