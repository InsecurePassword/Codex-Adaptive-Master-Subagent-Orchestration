#!/usr/bin/env bash
set -Eeuo pipefail

repo_owner="InsecurePassword"
repo_name="Codex-Adaptive-Master-Subagent-Orchestration"
repo_ref="main"
raw_base_url="https://github.com/${repo_owner}/${repo_name}/raw/refs/heads/main"
manifest_url="${raw_base_url}/install-manifest.txt"
package_version="4.0"
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
max_runtime_bytes=67108864
max_runtime_record_bytes=65536
max_runtime_files=2048

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
  "references/configuration-maintenance.md"
  "references/convergence-control.md"
  "references/evidence-handling.md"
  "references/feature-control.md"
  "references/handoff-control.md"
  "references/hierarchy-control.md"
  "references/intensity-control.md"
  "references/package-maintenance.md"
  "references/profile-management.md"
  "references/project-control.md"
  "references/project-governance.md"
  "references/request-accounting.md"
  "references/review-control.md"
  "references/root-execution-fallback.md"
  "references/runtime-core.md"
  "references/runtime-observation.md"
  "references/shared-worktree-control.md"
  "references/surface-identity.md"
  "references/task-graph-safeguards.md"
  "references/work-order-refinement.md"
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

for command_name in curl awk sort cmp mktemp wc tr grep head tail od find dirname iconv; do
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


validate_runtime_text() {
  local path=$1 maximum=$2 size bom last_byte linked
  [[ -f "$path" && ! -L "$path" ]] || fail "AMS runtime record is not a safe regular file: ${path}"
  size="$(wc -c < "$path" | tr -d '[:space:]')"
  (( size > 0 && size <= maximum )) || fail "AMS runtime record size is invalid: ${path} (${size} bytes)"
  bom="$(head -c 3 "$path" | od -An -tx1 | tr -d ' \n')"
  [[ "$bom" != "efbbbf" ]] || fail "AMS runtime record has a UTF-8 BOM: ${path}"
  if LC_ALL=C grep -q $'\r' "$path"; then fail "AMS runtime record contains CR characters: ${path}"; fi
  if od -An -tx1 "$path" | grep -qE '(^| )00( |$)'; then fail "AMS runtime record contains NUL bytes: ${path}"; fi
  last_byte="$(tail -c 1 "$path" | od -An -tu1 | tr -d ' \n')"
  [[ "$last_byte" == "10" ]] || fail "AMS runtime record is missing final LF: ${path}"
  iconv -f UTF-8 -t UTF-8 "$path" >/dev/null 2>&1 || fail "AMS runtime record is not valid UTF-8: ${path}"
  linked="$(find -P "$path" -type f -links +1 -print 2>/dev/null || true)"
  [[ -z "$linked" ]] || fail "AMS runtime record has multiple hard links: ${path}"
}

runtime_field() {
  local path=$1 key=$2
  awk -F '\t' -v wanted="$key" '$1 == wanted { print substr($0, length($1) + 2); exit }' "$path"
}

validate_runtime_record() {
  local path=$1 kind=$2 relative=$3 header expected campaign_id state generation created updated fingerprints base
  local correction_count correction_limit redesign_count redesign_limit terminal receipt closed lease
  validate_runtime_text "$path" "$max_runtime_record_bytes"
  if [[ "$kind" == tracking ]]; then
    header='ams-convergence-tracking-v1'
    expected='campaign_id,root_objective_id,project_root,state,owner_id,owner_lease_expires_at,record_generation,created_at,updated_at,design_epoch_id,redesign_count,redesign_limit,epoch_correction_count,correction_limit,candidate_receipt,acceptance_boundary,finding_fingerprints,last_resolution_action'
  else
    header='ams-convergence-history-v1'
    expected='campaign_id,root_objective_id,project_root,state,owner_id,owner_lease_expires_at,record_generation,created_at,updated_at,design_epoch_id,redesign_count,redesign_limit,epoch_correction_count,correction_limit,candidate_receipt,acceptance_boundary,finding_fingerprints,last_resolution_action,terminal_disposition,terminal_receipt,closed_at'
  fi
  awk -F '\t' -v header="$header" -v expected="$expected" '
    NR == 1 { if ($0 != header) exit 10; next }
    NF != 2 || $1 !~ /^[a-z_]+$/ || seen[$1]++ || length($0) > 4096 { exit 11 }
    { value=substr($0, length($1) + 2); if (value ~ /[[:cntrl:]]/) exit 14 }
    END {
      n=split(expected, keys, ",")
      for (i=1; i<=n; i++) if (!seen[keys[i]]) exit 12
      if (NR != n + 1) exit 13
    }
  ' "$path" || fail "AMS convergence record structure is invalid: ${relative}"

  campaign_id="$(runtime_field "$path" campaign_id)"
  [[ "$campaign_id" =~ ^[A-Za-z0-9._-]{1,96}$ ]] || fail "AMS convergence campaign ID is invalid: ${relative}"
  [[ -n "$(runtime_field "$path" root_objective_id)" && -n "$(runtime_field "$path" project_root)" ]] || fail "AMS convergence identity is incomplete: ${relative}"
  state="$(runtime_field "$path" state)"
  generation="$(runtime_field "$path" record_generation)"
  correction_count="$(runtime_field "$path" epoch_correction_count)"
  correction_limit="$(runtime_field "$path" correction_limit)"
  redesign_count="$(runtime_field "$path" redesign_count)"
  redesign_limit="$(runtime_field "$path" redesign_limit)"
  [[ "$generation" =~ ^[0-9]+$ && "$correction_count" =~ ^[0-9]+$ && "$correction_limit" =~ ^[0-9]+$ && "$redesign_count" =~ ^[0-9]+$ && "$redesign_limit" =~ ^[0-9]+$ ]] || fail "AMS convergence counters are invalid: ${relative}"
  (( correction_limit >= 2 && correction_limit <= 12 && redesign_limit >= 1 && redesign_limit <= 12 )) || fail "AMS convergence limits are invalid: ${relative}"
  created="$(runtime_field "$path" created_at)"; updated="$(runtime_field "$path" updated_at)"; lease="$(runtime_field "$path" owner_lease_expires_at)"
  [[ "$created" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ && "$updated" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]] || fail "AMS convergence timestamps are invalid: ${relative}"
  [[ "$lease" == none || "$lease" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]] || fail "AMS convergence lease timestamp is invalid: ${relative}"
  fingerprints="$(runtime_field "$path" finding_fingerprints)"
  [[ "$fingerprints" == none || "$fingerprints" =~ ^[0-9a-f]{64}(,[0-9a-f]{64}){0,7}$ ]] || fail "AMS convergence fingerprints are invalid: ${relative}"
  base="$(basename "$path")"
  if [[ "$kind" == tracking ]]; then
    [[ "$state" =~ ^(monitoring|convergence|intervention-required|terminal-pending-history)$ ]] || fail "AMS convergence tracking state is invalid: ${relative}"
    [[ "$base" == "${campaign_id}.tracking.log" ]] || fail "AMS convergence tracking filename does not match its campaign: ${relative}"
  else
    terminal="$(runtime_field "$path" terminal_disposition)"; receipt="$(runtime_field "$path" terminal_receipt)"; closed="$(runtime_field "$path" closed_at)"
    [[ "$state" == terminal ]] || fail "AMS convergence history state is invalid: ${relative}"
    [[ "$terminal" =~ ^(accept|accept-with-follow-up|blocked|failed|intervention-required|cancelled|user-disabled|user-override|superseded|stale)$ ]] || fail "AMS convergence terminal disposition is invalid: ${relative}"
    [[ "$receipt" =~ ^[0-9a-f]{64}$ ]] || fail "AMS convergence terminal receipt is invalid: ${relative}"
    [[ "$closed" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]] || fail "AMS convergence closed timestamp is invalid: ${relative}"
    [[ "$base" == "${campaign_id}.${receipt}.record.log" ]] || fail "AMS convergence history filename does not match its record: ${relative}"
  fi
}

validate_runtime_state() {
  local runtime_root=$1 total=0 count=0 path size relative
  [[ ! -L "$runtime_root" && -d "$runtime_root" ]] || fail "AMS runtime state is redirected or not a directory: ${runtime_root}"
  while IFS= read -r -d '' path; do
    [[ "$path" != "$runtime_root" ]] || continue
    [[ ! -L "$path" ]] || fail "AMS runtime state contains a redirected path: ${path}"
    relative=${path#"${runtime_root}/"}
    if [[ -d "$path" ]]; then
      case "$relative" in convergence|convergence/history) ;; *) fail "AMS runtime state contains an unexpected directory: ${relative}" ;; esac
    elif [[ -f "$path" ]]; then
      case "$relative" in
        convergence/*.tracking.log) validate_runtime_record "$path" tracking "$relative" ;;
        convergence/history/*.record.log) validate_runtime_record "$path" history "$relative" ;;
        *) fail "AMS runtime state contains an unexpected file: ${relative}" ;;
      esac
      size="$(wc -c < "$path" | tr -d '[:space:]')"; total=$((total + size)); count=$((count + 1))
      (( total <= max_runtime_bytes && count <= max_runtime_files )) || fail "AMS runtime state exceeds the preservation bound."
    else
      fail "AMS runtime state contains an unsupported path type: ${path}"
    fi
  done < <(find -P "$runtime_root" -print0)
}

runtime_state_snapshot() {
  local runtime_root=$1 output=$2 path relative size digest
  : > "$output"
  while IFS= read -r path; do
    relative=${path#"${runtime_root}/"}; size="$(wc -c < "$path" | tr -d '[:space:]')"; digest="$(sha256_file "$path")"
    printf '%s\t%s\t%s\n' "$relative" "$size" "$digest" >> "$output"
  done < <(find -P "$runtime_root" -type f -print | LC_ALL=C sort)
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

lock_dir="${skill_home}/.${skill_name}.runtime.lock"
[[ ! -L "$lock_dir" ]] || fail "Package/runtime lock path is redirected: ${lock_dir}"
if ! mkdir "$lock_dir" 2>/dev/null; then
  fail "Another AMS package/runtime writer is active or a stale lock exists: ${lock_dir}"
fi
lock_owner="installer-$$-$(date -u +%Y%m%dT%H%M%SZ)"
lock_now="$(date +%s)"
if ! printf '%s\n' \
  'ams-runtime-lock-v1' \
  $'owner_id\t'"${lock_owner}" \
  $'purpose\tinstaller' \
  $'campaign_id\tnone' \
  $'pid\t'"$$" \
  $'acquired_epoch\t'"${lock_now}" \
  $'lease_expires_epoch\t'"$((lock_now + 3600))" > "${lock_dir}/owner.log"; then
  rm -rf -- "$lock_dir" 2>/dev/null || true
  fail "Could not publish the package/runtime lock owner record."
fi

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
runtime_state_present=0
runtime_snapshot_before=""
runtime_snapshot_after=""

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
  if [[ -f "${lock_dir}/owner.log" ]] && grep -Fqx $'owner_id\t'"${lock_owner}" "${lock_dir}/owner.log" 2>/dev/null; then
    rm -rf -- "$lock_dir" 2>/dev/null || true
  fi
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
runtime_snapshot_before="${stage_root}/runtime-before.tsv"
runtime_snapshot_after="${stage_root}/runtime-after.tsv"
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
if [[ -e "$destination/.runtime" || -L "$destination/.runtime" ]]; then
  validate_runtime_state "$destination/.runtime"
  runtime_state_snapshot "$destination/.runtime" "$runtime_snapshot_before"
  runtime_state_present=1
fi
if [[ -e "$destination" ]]; then
  [[ ! -e "$backup_path" && ! -L "$backup_path" ]] || fail "Unexpected backup collision: ${backup_path}"
  mv -- "$destination" "$backup_path"
  existing_moved=1
fi
mv -- "$candidate" "$destination" || fail "Installation failed while replacing the skill directory."
candidate_installed=1

if (( runtime_state_present == 1 )); then
  [[ -d "$backup_path/.runtime" && ! -L "$backup_path/.runtime" ]] || fail "Preserved AMS runtime state disappeared during replacement."
  [[ ! -e "$destination/.runtime" && ! -L "$destination/.runtime" ]] || fail "Candidate unexpectedly contains package-local runtime state."
  cp -a -- "$backup_path/.runtime" "$destination/.runtime"
  validate_runtime_state "$destination/.runtime"
  runtime_state_snapshot "$destination/.runtime" "$runtime_snapshot_after"
  cmp -s "$runtime_snapshot_before" "$runtime_snapshot_after" || fail "AMS runtime state changed during preservation; retry from a stable record boundary."
fi

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
