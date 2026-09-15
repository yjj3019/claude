#!/usr/bin/env bash
# ============================================================
#  OpenShift Virtualization 정기점검 자동 수집 스크립트
#  대상 : RHOCP + OpenShift Virtualization(CNV)
#  범위 : 1.Cluster구성 / 2.ClusterOperator / 3.API연동 / 4.Network / 5.Virtualization
#         (Scaling/Deployment replica, Self-Healing 항목은 제외)
#  실행 : ./OCP-HCK-Score.sh
#         (완전 자동 — 입력 프롬프트 없이 클러스터에서 점검 대상을
#          자동으로 찾아 끝까지 실행합니다)
#  결과 : ocp-healthcheck-report-<날짜>.txt (체크리스트 xlsx의 "점검결과"란에
#         그대로 옮겨 적을 수 있도록 항목번호 순서로 출력됩니다)
#  의존성 : oc, bash  (선택: jq — 있으면 CO 판정이 더 정확해집니다)
#
#  안전장치 : VM 상태를 바꾸는 5-1(기동/재기동/종료), 5-2(Live Migration)는
#             기본적으로 자동 실행되지 않고 건너뜁니다(운영 영향 방지).
#             실행하려면 (1) 테스트용 VM에 라벨을 붙이고 (2) 아래처럼 실행하세요.
#             대상은 무작위 전체 VM이 아니라 이 라벨이 붙은 VM 중에서만 선정됩니다:
#               oc label vm <vm-name> -n <ns> healthcheck.ocp.score/disruptive-test=allowed
#               RUN_VM_DISRUPTIVE=yes ./OCP-HCK-Score.sh
#
#  점검 범위 원칙(2026-09-15 확정, 백인균/이주석 지적 반영): 이 스크립트는 "월 정기점검"
#             (매달 반복 실행해도 안전하고 의미 있는 읽기전용 상태 확인)과 "구조/구성진단"
#             (설계·오버커밋·리소스 배치 같은 구성상의 문제를 들춰내는 심층 점검)을 함께
#             다룬다 — 두 성격을 억지로 분리하지 않고 한 리포트에 담되, 클러스터 상태를
#             바꾸는 항목(5-1/5-2)만 "구축/변경검증용"으로 별도 표기하고 기본 제외한다.
#  참고 : 4-2(Pod간 통신) 테스트는 무작위 Pod에 ping이 없을 수 있어,
#         score-debug 네임스페이스에 아래처럼 전용 디버그 Pod를 미리 띄워두면
#         자동으로 그 Pod를 사용합니다(없으면 기존처럼 자동 탐지 Pod 사용):
#           oc new-project score-debug
#           oc create deployment score-debug \
#             --image=<내부미러레지스트리>/tools/score-debug:latest -n score-debug -- sleep infinity
# ============================================================
set -uo pipefail
umask 077

RUN_VM_DISRUPTIVE="${RUN_VM_DISRUPTIVE:-no}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log()  { echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} $1"; }
ok()   { echo -e "${GREEN}  ✔${NC} $1"; }
warn() { echo -e "${YELLOW}  ⚠${NC} $1"; }
err()  { echo -e "${RED}  ✘${NC} $1"; }

REPORT="ocp-healthcheck-report-$(date +%Y%m%d-%H%M%S)-$$.txt"
HTML_REPORT="${REPORT%.txt}.html"
FAIL_COUNT=0
FAILED_ITEMS=()

write() { echo -e "$1" | tee -a "$REPORT" >/dev/null; }
raw()   { echo -e "$1" >> "$REPORT"; }

# 방어적 경계 검증(team agent 리뷰 Suggestion, 2026-09-14): 이 스크립트는 클러스터에서
# 자동탐지한 네임스페이스/Pod/노드 등 이름을 bash -c "... '$VAR' ..." 형태로 nested
# 삽입한다. K8s apiserver가 오브젝트 이름을 RFC1123으로 검증하므로 값에 작은따옴표가
# 물리적으로 존재할 수 없어 오늘 시점엔 안전하지만(보안 리뷰로 확인됨), 그 전제가 실제로
# 지켜지는지 매 실행마다 스스로 재확인한다 — 위반되면 nested quoting이 깨지기 전에
# 해당 값을 무조건 비워서 안전하게 만든다(고쳐 쓰지 않고 버림).
assert_safe_name() {
  # 사용법: assert_safe_name <변수명> <값> — 안전하면 0, 아니면 경고 후 1
  local name="$1" val="$2"
  [ -z "$val" ] && return 0
  case "$val" in
    *[!a-zA-Z0-9._:/-]*)
      warn "자동탐지 값 ${name}='${val}' 이 예상 문자 범위(영숫자/-._:/)를 벗어나 안전을 위해 비웁니다 — 클러스터 리소스 이름을 직접 확인하세요."
      return 1
      ;;
  esac
  return 0
}

section() {
  write ""
  write "════════════════════════════════════════════════════════"
  write "■ $1"
  write "════════════════════════════════════════════════════════"
}

item_header() {
  # item_header "<번호>" "<점검항목>" "<Command>"
  raw ""
  raw "--------------------------------------------------------"
  raw "[$1] $2"
  raw "Command : $3"
  raw "--------------------------------------------------------"
}

# 명령 실행 후 결과를 리포트에 기록 (판정은 사람이 직접 xlsx에 기입)
# "[결과] rc=N" 한 줄을 출력 앞에 남겨 HTML 파서가 문자열 휴리스틱 대신
# 실제 종료코드로 성공/실패를 판정할 수 있게 한다. 실패는 FAIL_COUNT에 누적되어
# 스크립트 종료코드에 반영된다(cron/모니터링이 실패를 감지할 수 있도록).
run_cmd() {
  # run_cmd "<번호>" "<점검항목>" "<Command로 표시할 문자열>" -- 실제실행커맨드...
  local num="$1" desc="$2" show_cmd="$3"; shift 3
  if [[ "$1" == "--" ]]; then shift; fi
  item_header "$num" "$desc" "$show_cmd"
  local out rc
  out="$("$@" 2>&1)"
  rc=$?
  raw "[결과] rc=${rc}"
  printf '%s\n' "$out" >> "$REPORT"
  if [ "$rc" -eq 0 ]; then
    ok "$num $desc"
  else
    FAIL_COUNT=$((FAIL_COUNT+1))
    FAILED_ITEMS+=("$num")
    warn "$num $desc (명령 실행 실패 또는 오류 — 리포트 확인)"
  fi
}

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  OpenShift Virtualization 정기점검 자동 수집           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# ── 사전 점검 ──────────────────────────────────────────────
if ! command -v oc &>/dev/null; then
  err "oc CLI가 필요합니다."; exit 1
fi
if ! oc whoami &>/dev/null; then
  err "'oc login' 먼저 실행하세요."; exit 1
fi
: > "$REPORT"
HAS_JQ=0
command -v jq &>/dev/null && HAS_JQ=1
HAS_PY=0
command -v python3 &>/dev/null && HAS_PY=1

USER_=$(oc whoami)
SERVER=$(oc whoami --show-server 2>/dev/null || echo unknown)
write "점검 대상 클러스터 : ${SERVER}"
write "점검 수행 계정     : ${USER_}"
write "점검 시작 시각     : $(date)"

# ════════════════════════════════════════════════════════════
section "1. Cluster 구성 확인"
run_cmd "1-1" "Node Join 상태 확인" "oc get nodes" -- oc get nodes
run_cmd "1-2" "전체 Node Role 확인 (master/worker/infra/router 등)" "oc get nodes" -- oc get nodes
run_cmd "1-3" "Node 버전 일치 확인" "oc get nodes -o wide" -- oc get nodes -o wide
run_cmd "1-4" "VM 스케줄링 가능 Node 라벨 확인 (kubevirt.io/schedulable)" "oc get nodes -l kubevirt.io/schedulable=true" -- oc get nodes -l kubevirt.io/schedulable=true

# 노드별 스펙 + 현재 리소스 사용량 — 고객 요구사항(2026-09-15, 백인균): 1절이 노드
# 존재/역할/버전만 확인해 정보가 부족했음. Capacity(스펙)와 oc adm top(현재 사용량)을 함께.
run_cmd "1-5" "노드별 스펙(CPU/Memory Capacity) 및 현재 리소스 사용량 확인" "oc describe node | grep -A2 Capacity / oc adm top node" -- bash -c "
  rc=0
  oc get nodes -o custom-columns=NAME:.metadata.name,CPU_CAPACITY:.status.capacity.cpu,MEM_CAPACITY:.status.capacity.memory,ARCH:.status.nodeInfo.architecture,OS:.status.nodeInfo.osImage || rc=\$?
  echo ''
  echo '--- 현재 리소스 사용량(oc adm top node) ---'
  oc adm top node || rc=\$?
  echo '===== 아래는 상세 원본(참고용) ====='
  oc describe node || rc=\$?
  exit \$rc"

# Machine Config(MCP) 현황 확인 — 고객 요구사항(2026-09-15, 장성빈). MCP가 Updated 상태이고
# 각 노드의 current/desired 렌더드 MachineConfig가 일치하는지(업그레이드/설정 반영이 밀린
# 노드가 없는지) 자동 판정한다.
run_cmd "1-6" "Machine Config(MCP) 현황 확인" "oc get mcp / oc get nodes (currentConfig vs desiredConfig)" -- bash -c "
  rc=0
  echo '[MCP 상태 — UPDATED=True, UPDATING=False, DEGRADED=False, PAUSED=<none>/false, READY=TOTAL이 정상]'
  oc get mcp -o custom-columns='NAME:.metadata.name,CONFIG:.status.configuration.name,UPDATED:.status.conditions[?(@.type==\"Updated\")].status,UPDATING:.status.conditions[?(@.type==\"Updating\")].status,DEGRADED:.status.conditions[?(@.type==\"Degraded\")].status,PAUSED:.spec.paused,READY:.status.readyMachineCount,TOTAL:.status.machineCount' || rc=\$?
  echo ''
  echo '[노드별 current/desired 렌더드 MachineConfig 일치 여부 — CURRENT==DESIRED, STATE=Done, REASON 비어있음이 정상]'
  NODE_MC=\$(oc get nodes -o custom-columns='NAME:.metadata.name,CURRENT:.metadata.annotations.machineconfiguration\.openshift\.io/currentConfig,DESIRED:.metadata.annotations.machineconfiguration\.openshift\.io/desiredConfig,STATE:.metadata.annotations.machineconfiguration\.openshift\.io/state,REASON:.metadata.annotations.machineconfiguration\.openshift\.io/reason' --no-headers 2>&1) || rc=\$?
  echo \"\$NODE_MC\"
  MISMATCH=\$(echo \"\$NODE_MC\" | awk '\$2!=\$3')
  if [ -n \"\$MISMATCH\" ]; then
    echo ''
    echo \"[확인 필요] current/desired MachineConfig가 다른 노드: \$MISMATCH\"
    rc=1
  fi
  exit \$rc"

# ════════════════════════════════════════════════════════════
section "2. Cluster Operator 상태 확인"
OPERATORS=(
  authentication baremetal cloud-controller-manager cloud-credential
  cluster-autoscaler config-operator console csi-snapshot-controller
  dns etcd image-registry ingress insights kube-apiserver
  kube-controller-manager kube-scheduler kube-storage-version-migrator
  machine-api machine-approver machine-config marketplace monitoring
  network node-tuning openshift-apiserver openshift-controller-manager
  openshift-samples operator-lifecycle-manager operator-lifecycle-manager-catalog
  operator-lifecycle-manager-packageserver service-ca storage
  control-plane-machine-set olm
)
# 고정폭 정렬 테이블로 개선(2026-09-15, 김수용 제안) — 파이프(|) 구분자는 HTML 파서
# (embedded python)와 fill_checklist.py의 CO_LINE_RE가 그대로 의존하므로 유지하되,
# 각 필드를 고정폭으로 패딩해 이전처럼 들쭉날쭉하지 않고 줄이 맞도록 함.
CO_FMT='%-6s | %-38s | %-9s | %-10s | %-12s | %-10s | %-8s | %s\n'
raw ""
raw "$(printf "$CO_FMT" 'NO' 'OPERATOR' 'VERSION' 'AVAILABLE' 'PROGRESSING' 'DEGRADED' 'SINCE' 'VERDICT')"
raw "$(printf '%.0s-' {1..115})"
idx=1
for op in "${OPERATORS[@]}"; do
  # native `oc get co` 한 줄로 VERSION/SINCE까지 항상 확보하고(jq 유무와 무관),
  # jq가 있으면 AVAILABLE/PROGRESSING/DEGRADED만 JSON conditions로 더 정확히 덮어쓴다.
  LINE=$(oc get co "$op" --no-headers 2>/dev/null)
  if [ -z "$LINE" ]; then
    write "$(printf "$CO_FMT" "2-${idx}" "$op" '-' '-' '-' '-' '-' '[조회 실패/미존재]')"
  else
    read -r _ VERSION AVAIL PROG DEG SINCE _ <<<"$LINE"
    if [ "$HAS_JQ" -eq 1 ]; then
      JSON=$(oc get co "$op" -o json 2>/dev/null)
      AVAIL=$(echo "$JSON" | jq -r '.status.conditions[]|select(.type=="Available")|.status')
      PROG=$(echo "$JSON"  | jq -r '.status.conditions[]|select(.type=="Progressing")|.status')
      DEG=$(echo "$JSON"   | jq -r '.status.conditions[]|select(.type=="Degraded")|.status')
    fi
    # 이모지 없는 순수 텍스트 판정(2026-09-14, 사용자 요청으로 어휘 통일) — 1/3/4/5절의
    # "정상/확인필요/건너뜀/수동확인"과 같은 표기 체계를 쓰되, CO는 심각도 구분이 유의미해서
    # "이상(사유)"/"주의(사유)"로 세분화해 유지한다(폐쇄망 구형 Excel의 이모지 깨짐 문제도 해소).
    VERDICT="정상"
    if [ "$DEG" == "True" ]; then
      VERDICT="이상(Degraded)"
    elif [ "$AVAIL" != "True" ]; then
      VERDICT="이상(Available)"
    elif [ "$PROG" == "True" ]; then
      VERDICT="주의(Progressing)"
    fi
    write "$(printf "$CO_FMT" "2-${idx}" "$op" "$VERSION" "$AVAIL" "$PROG" "$DEG" "$SINCE" "$VERDICT")"
  fi
  idx=$((idx+1))
done
ok "Cluster Operator ${#OPERATORS[@]}개 상태 수집 완료"

# 위 고정 목록에 없는 Operator가 클러스터에 실재하면(버전 차이/클라우드 특화 등)
# 그 상태를 놓칠 수 있으므로 실제 CO 목록과 대조해 목록 밖 항목만 별도로 남긴다.
ALL_CO=$(oc get co -o jsonpath='{.items[*].metadata.name}' 2>/dev/null)
EXTRA_CO=""
for co in $ALL_CO; do
  printf '%s\n' "${OPERATORS[@]}" | grep -qx "$co" || EXTRA_CO="${EXTRA_CO}${co} "
done
if [ -n "$EXTRA_CO" ]; then
  raw "[목록 외 Operator 발견] ${EXTRA_CO}(고정 ${#OPERATORS[@]}개 목록에 없음 — 'oc get co ${EXTRA_CO}'로 별도 확인 필요)"
  warn "목록 외 Operator ${EXTRA_CO}발견 — 리포트 확인"
fi

# ════════════════════════════════════════════════════════════
# 점검 대상 자동 탐지 (입력 프롬프트 없이 클러스터에서 자동으로 선정)
# 매 실행마다 "무작위"로 골라 여러 네임스페이스/노드/VM이 골고루
# 점검되도록 한다 (항상 첫 번째 항목만 뽑던 문제 수정).
# ════════════════════════════════════════════════════════════
log "점검 대상 자동 탐지 중... (실행마다 무작위로 선정됩니다)"

# 목록을 한 줄씩 받아 무작위로 한 줄 뽑는 헬퍼 (shuf 없으면 awk로 대체)
rand_line() {
  if command -v shuf &>/dev/null; then
    shuf -n1
  else
    awk 'BEGIN{srand()} {print rand()"\t"$0}' | sort -n | cut -f2- | head -n1
  fi
}

# Running 상태인 Pod 중 무작위 1개와 그 namespace를 함께 확보
read -r Q_NS Q_POD <<<"$(oc get pods -A --field-selector=status.phase=Running \
  -o jsonpath='{range .items[*]}{.metadata.namespace}{" "}{.metadata.name}{"\n"}{end}' 2>/dev/null \
  | rand_line)"

# 노드 목록 중 서로 다른 2개를 무작위로 확보 (대표 노드 / ping 대상 노드)
mapfile -t _NODES < <(oc get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null \
  | (command -v shuf &>/dev/null && shuf || awk 'BEGIN{srand()} {print rand()"\t"$0}' | sort -n | cut -f2-))
Q_NODE="${_NODES[0]:-}"
Q_NODE2="${_NODES[1]:-${_NODES[0]:-}}"
_NODES_LIST="${_NODES[*]}"

Q_SVC=""
Q_PVC=""
[ -n "$Q_NS" ] && Q_SVC=$(oc get svc -n "$Q_NS" -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null | rand_line)
[ -n "$Q_NS" ] && Q_PVC=$(oc get pvc -n "$Q_NS" -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null | rand_line)
Q_PV=$(oc get pv -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null | rand_line)
Q_ROUTE=""
[ -n "$Q_NS" ] && Q_ROUTE=$(oc get route -n "$Q_NS" -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null | rand_line)

# Pod간 통신(ping, 4-2) 테스트 대상 — 인프라 네임스페이스(openshift-*/kube-*/default 등)는
# NetworkPolicy로 ICMP를 막아두는 경우가 흔해(예: HCO의 kubevirt-apiserver-proxy-np가 ingress를
# TCP 8080만 허용) 정상 상태에서도 ping이 실패하는 오탐을 유발한다. 사용자 워크로드 네임스페이스의
# Running Pod 중에서만 무작위로 고른다(다른 항목의 대표 네임스페이스 Q_NS는 그대로 유지).
INFRA_NS_RE='^(openshift(-.*)?|kube-.*|default)$'
Q_PEER_NS=""
Q_PEER_IP=""
read -r Q_PEER_NS Q_PEER_IP <<<"$(oc get pods -A --field-selector=status.phase=Running \
  -o jsonpath='{range .items[*]}{.metadata.namespace}{" "}{.status.podIP}{"\n"}{end}' 2>/dev/null \
  | awk -v re="$INFRA_NS_RE" '$1 !~ re && $2!="" {print}' | rand_line)"
# 사용자 네임스페이스에 Running Pod가 전혀 없으면 안전한 대체 대상(DNS 서비스)으로 폴백
if [ -z "$Q_PEER_IP" ]; then
  Q_PEER_NS="openshift-dns"
  Q_PEER_IP=$(oc get svc -n openshift-dns dns-default -o jsonpath='{.spec.clusterIP}' 2>/dev/null)
fi

# 노드 인터페이스 ping 대상: 두 번째로 뽑힌 노드의 INTERNAL-IP
Q_NODE_TARGET_IP=""
if [ -n "$Q_NODE2" ]; then
  Q_NODE_TARGET_IP=$(oc get node "$Q_NODE2" -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}' 2>/dev/null)
fi

# VM/VMI 자동 탐지 (클러스터 전체 VM 중 무작위 1개 — 5-4/5-5/5-6 읽기전용 점검용)
read -r V_NS V_VM <<<"$(oc get vm -A -o jsonpath='{range .items[*]}{.metadata.namespace}{" "}{.metadata.name}{"\n"}{end}' 2>/dev/null \
  | rand_line)"

# 5-1/5-2(상태를 바꾸는 파괴적 테스트) 전용 대상 — 클러스터 전체 무작위가 아니라
# "healthcheck.ocp.score/disruptive-test=allowed" 라벨이 붙은 VM 중에서만 선정한다.
# RUN_VM_DISRUPTIVE=yes일 때만 조회(기본 읽기전용 실행에서는 불필요한 API 호출 생략).
V_NS_SAFE=""
V_VM_SAFE=""
if [ "$RUN_VM_DISRUPTIVE" = "yes" ]; then
  read -r V_NS_SAFE V_VM_SAFE <<<"$(oc get vm -A -l healthcheck.ocp.score/disruptive-test=allowed \
    -o jsonpath='{range .items[*]}{.metadata.namespace}{" "}{.metadata.name}{"\n"}{end}' 2>/dev/null \
    | rand_line)"
fi

raw ""
raw "[자동 탐지된 점검 대상] (매 실행마다 무작위 선정)"
raw "  Namespace(대표) : ${Q_NS:-없음}"
raw "  Pod(대표)       : ${Q_POD:-없음}"
raw "  Node(대표)      : ${Q_NODE:-없음}"
raw "  Node(2번째)     : ${Q_NODE2:-없음} (${Q_NODE_TARGET_IP:-IP없음})$([ -n "$Q_NODE2" ] && [ "$Q_NODE2" = "$Q_NODE" ] && echo ' — 단일 노드 클러스터: 4-1 ping은 자기 자신 대상')"
raw "  Service         : ${Q_SVC:-없음}"
raw "  PV              : ${Q_PV:-없음}"
raw "  PVC             : ${Q_PVC:-없음}"
raw "  Route           : ${Q_ROUTE:-없음}"
raw "  Pod간 통신 대상 IP : ${Q_PEER_IP:-없음} (ns: ${Q_PEER_NS:-없음}, 인프라 네임스페이스 제외하고 선정)"
raw "  VM(대표)        : ${V_NS:-없음}/${V_VM:-없음}"
raw "  ※ 위 대상은 매 실행마다 클러스터 전체에서 무작위로 재선정됩니다(같은 대상만 반복 점검하는 것을 방지)."
raw "     Namespace/Pod(대표)는 '현재 Running 중인 임의의 Pod 1개'의 네임스페이스이므로, 그 네임스페이스가"
raw "     인프라 성격(예: openshift-ovn-kubernetes 등)이면 PVC/최근 이벤트가 원래 없어 'No resources found'가"
raw "     정상적으로 나올 수 있습니다 — 이는 결함이 아니라 해당 네임스페이스의 실제 상태입니다."
raw "     VM(대표)는 '실행 중 여부와 무관하게 클러스터 전체 VM 중 무작위 1개'이므로, 하필 꺼져있는 VM이"
raw "     뽑히면 5-4(CPU/Memory) 등에서 virt-launcher Pod가 없어 'No resources found'가 나올 수 있습니다."
raw "     4-2(Pod간 통신 대상 IP)는 인프라 네임스페이스를 제외하고 뽑지만, 그래도 사용자 정의 NetworkPolicy가"
raw "     ICMP를 막아둔 Pod가 뽑히면 rc=1로 실패합니다 — 이 경우도 스크립트 결함이 아니라 그 Pod의 실제"
raw "     보안 정책이 원인이니, 리포트 하단의 대상 Pod/Namespace로 'oc get networkpolicy -n <ns>'를 직접 확인하세요."
raw "     특정 네임스페이스/VM을 반드시 점검해야 한다면 위 무작위 결과 대신 수동 명령으로 재확인하세요."

# 아래 각 값은 이후 bash -c "... '$VAR' ..." 형태로 여러 항목에 nested 삽입되므로,
# 여기서 한 번에 안전성을 재확인한다(위반 시 값을 비워 해당 항목은 "대상 없음"으로 처리됨).
for _n in Q_NS Q_POD Q_NODE Q_NODE2 Q_SVC Q_PVC Q_PV Q_ROUTE Q_PEER_IP Q_PEER_NS \
          Q_NODE_TARGET_IP V_NS V_VM V_NS_SAFE V_VM_SAFE; do
  _v="${!_n}"
  assert_safe_name "$_n" "$_v" || eval "$_n=''"
done
unset _n _v

ok "자동 탐지 완료 — 아래 항목은 위 대상을 기준으로 자동 실행됩니다"

# ════════════════════════════════════════════════════════════
# 섹션명 리프레이밍(2026-09-15, 백인균 제안) — "API 연동 확인"보다 "워크로드/리소스
# 현황 확인"의 의미가 크다는 지적 반영. 항목번호(3-1 등)는 그대로 유지.
section "3. 워크로드/리소스 현황 및 API 연동 확인"

# 3-1~3-4: 상세조회(describe)는 접어두고, 목록/개수 같은 핵심만 항상 노출(2026-09-15,
# 이주석/백인균 — "상세 조회 전체는 불필요한 정보" 지적 반영). describe는 여전히 하되
# FOLD_MARKER 뒤로 이동시켜 원본은 보존하되 드랍다운에만 담는다.
run_cmd "3-1" "Namespace 리스트/상세 조회" "oc get ns / oc describe ns" -- bash -c "
  rc=0
  oc get ns || rc=\$?
  echo '===== 아래는 상세 원본(참고용) ====='
  if [ -n '$Q_NS' ]; then oc describe ns '$Q_NS' || rc=\$?; else echo '(네임스페이스 없음 - 건너뜀)'; fi
  exit \$rc"
run_cmd "3-2" "Pod 리스트/상세 조회" "oc get po -n <ns> / oc describe po" -- bash -c "
  rc=0
  if [ -n '$Q_NS' ]; then
    oc get po -n '$Q_NS' || rc=\$?
    echo ''
    NS_POD_COUNT=\$(oc get po -n '$Q_NS' --no-headers 2>/dev/null | wc -l)
    NS_RUNNING_COUNT=\$(oc get po -n '$Q_NS' --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
    echo \"[요약] ${Q_NS} 네임스페이스: 전체 \$NS_POD_COUNT개 / Running \$NS_RUNNING_COUNT개\"
  else
    echo '(네임스페이스 없음 - 건너뜀)'
  fi
  echo '===== 아래는 상세 원본(참고용) ====='
  if [ -n '$Q_NS' ] && [ -n '$Q_POD' ]; then oc describe po '$Q_POD' -n '$Q_NS' || rc=\$?; else echo '(Pod 없음 - 건너뜀)'; fi
  exit \$rc"
run_cmd "3-3" "Node 리스트/상세 조회" "oc get node / oc describe node" -- bash -c "
  rc=0
  oc get node || rc=\$?
  echo '===== 아래는 상세 원본(참고용) ====='
  if [ -n '$Q_NODE' ]; then oc describe node '$Q_NODE' || rc=\$?; else echo '(Node 없음 - 건너뜀)'; fi
  exit \$rc"
run_cmd "3-4" "Service 리스트/상세 조회" "oc get svc -n <ns> / oc describe svc" -- bash -c "
  rc=0
  if [ -n '$Q_NS' ]; then oc get svc -n '$Q_NS' || rc=\$?; else echo '(네임스페이스 없음 - 건너뜀)'; fi
  echo '===== 아래는 상세 원본(참고용) ====='
  if [ -n '$Q_NS' ] && [ -n '$Q_SVC' ]; then oc describe svc '$Q_SVC' -n '$Q_NS' || rc=\$?; else echo '(Service 없음 - 건너뜀)'; fi
  exit \$rc"
# PV/PVC 개수+총 용량 요약(2026-09-15, 이주석 제안) — VM 1000대 규모 클러스터에서 PVC
# 전체 리스트가 1000행 넘게 그대로 나오는 문제 대응. 상세 리스트는 FOLD_MARKER로 접고
# 개수/총 용량만 항상 노출.
_size_to_gi() {
  awk '
    function tonum(v,   num,suf,mult){
      if (!match(v, /^[0-9.]+/)) return 0
      num=substr(v,RSTART,RLENGTH); suf=substr(v,RLENGTH+1)
      if (suf=="Ki") mult=1/1024/1024
      else if (suf=="Mi") mult=1/1024
      else if (suf=="Gi") mult=1
      else if (suf=="Ti") mult=1024
      else if (suf=="Pi") mult=1024*1024
      else mult=1/1024/1024/1024
      return num*mult
    }
    {sum+=tonum($1)} END{printf "%.1f", sum+0}'
}
PV_COUNT=$(oc get pv --no-headers 2>/dev/null | wc -l | tr -d ' ')
PV_TOTAL_GI=$(oc get pv -o custom-columns=CAP:.spec.capacity.storage --no-headers 2>/dev/null | _size_to_gi)
PVC_COUNT=$(oc get pvc -A --no-headers 2>/dev/null | wc -l | tr -d ' ')
PVC_TOTAL_GI=$(oc get pvc -A -o custom-columns=CAP:.status.capacity.storage --no-headers 2>/dev/null | _size_to_gi)

run_cmd "3-5" "PV 리스트/상세 조회" "oc get pv / oc describe pv" -- bash -c "
  rc=0
  echo '[요약] 전체 PV 개수: $PV_COUNT개, 총 용량: 약 ${PV_TOTAL_GI}Gi'
  echo '===== 아래는 상세 원본(참고용) ====='
  oc get pv || rc=\$?
  if [ -n '$Q_PV' ]; then oc describe pv '$Q_PV' || rc=\$?; else echo '(PV 없음 - 건너뜀)'; fi
  exit \$rc"
# Pod/VM 어디에도 바인딩되지 않고 남아있는 PVC 전체 목록(클러스터 전체) — 고객 요구사항(2026-09-14).
# VM 디스크는 virt-launcher Pod의 volume으로 잡히므로 Pod의 spec.volumes만 대조하면 VM PVC도 포함된다.
# jq가 필요(3절의 jq 소프트 의존성과 동일한 선택적 저하 패턴).
if [ "$HAS_JQ" -eq 1 ]; then
  ALL_PVC_LIST=$(oc get pvc -A -o json 2>/dev/null | jq -r '.items[] | "\(.metadata.namespace)/\(.metadata.name)"' | LC_ALL=C sort -u)
  USED_PVC_LIST=$(oc get pods -A -o json 2>/dev/null | jq -r '.items[] | .metadata.namespace as $ns | (.spec.volumes // [])[] | select(.persistentVolumeClaim) | $ns + "/" + .persistentVolumeClaim.claimName' | LC_ALL=C sort -u)
  if [ -n "$ALL_PVC_LIST" ]; then
    ORPHAN_PVC_LIST=$(LC_ALL=C comm -23 <(printf '%s\n' "$ALL_PVC_LIST") <(printf '%s\n' "$USED_PVC_LIST"))
    PVC_ORPHAN_REPORT="${ORPHAN_PVC_LIST:-(모두 Pod/VM에 바인딩되어 있음)}"
  else
    PVC_ORPHAN_REPORT="(클러스터 전체에 PVC 없음)"
  fi
else
  PVC_ORPHAN_REPORT="(jq 미설치 — 이 점검은 jq가 필요합니다)"
fi
run_cmd "3-6" "PVC 리스트/상세 조회" "oc get pvc -n <ns> / oc describe pvc" -- bash -c "
  rc=0
  echo '[요약] 전체 PVC 개수(클러스터 전체): $PVC_COUNT개, 총 용량: 약 ${PVC_TOTAL_GI}Gi'
  echo ''
  echo '[Pod/VM에 바인딩되지 않은 PVC — 클러스터 전체]'
  echo '$PVC_ORPHAN_REPORT'
  echo '===== 아래는 상세 원본(참고용) ====='
  if [ -n '$Q_NS' ]; then oc get pvc -n '$Q_NS' || rc=\$?; else echo '(네임스페이스 없음 - 건너뜀)'; fi
  if [ -n '$Q_NS' ] && [ -n '$Q_PVC' ]; then oc describe pvc '$Q_PVC' -n '$Q_NS' || rc=\$?; else echo '(PVC 없음 - 건너뜀)'; fi
  exit \$rc"
run_cmd "3-7" "알람 이벤트 조회" "oc get event -n <ns> --sort-by='.lastTimestamp'" -- bash -c "
  set -o pipefail
  if [ -n '$Q_NS' ]; then oc get event -n '$Q_NS' --sort-by='.lastTimestamp' | tail -50; else echo '(네임스페이스 없음 - 건너뜀)'; fi"

run_cmd "3-8" "Node CPU/Memory 사용량 조회" "oc adm top node" -- oc adm top node
run_cmd "3-9" "Pod CPU/Memory 사용량 조회" "oc adm top pod -n <ns>" -- bash -c "
  if [ -n '$Q_NS' ]; then oc adm top pod -n '$Q_NS'; else echo '(네임스페이스 없음 - 건너뜀)'; fi"

# 넘버링 교체(2026-09-15, 이주석 제안) — 정지된 Pod 확인을 먼저(3-10), Pod 로그 조회를
# 뒤로(3-11) 배치. 정지된(non-Running) Pod 전체 목록: Job/DaemonSet 소유의 Succeeded는
# 정상 종료로 분류하고, 그 외(Failed/Pending/Unknown 또는 소유자 불명의 Succeeded)만
# "확인 필요"로 구분해 보여준다(둘 다 rc에는 영향 없음 — 사람이 리포트를 보고 판단).
run_cmd "3-10" "정지된(non-Running) Pod 리스트 확인 — 정상 종료(Job/DaemonSet)와 비정상 종료 구분" "oc get pods -A --field-selector=status.phase!=Running" -- bash -c "
  rc=0
  RAW=\$(oc get pods -A --field-selector=status.phase!=Running -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,STATUS:.status.phase,REASON:.status.reason,OWNER:.metadata.ownerReferences[0].kind,NODE:.spec.nodeName --no-headers 2>/dev/null) || rc=\$?
  if [ -z \"\$RAW\" ]; then
    echo '(정지된 Pod 없음 — 모든 Pod가 Running 상태)'
  else
    echo '[정상 종료로 추정 — Job/DaemonSet 소유의 Succeeded]'
    echo \"\$RAW\" | awk '(\$3==\"Succeeded\" && (\$5==\"Job\" || \$5==\"DaemonSet\")){print; f=1} END{if(!f) print \"(해당 없음)\"}'
    echo ''
    echo '[확인 필요 — 그 외 비정상 종료/대기 상태]'
    echo \"\$RAW\" | awk '!(\$3==\"Succeeded\" && (\$5==\"Job\" || \$5==\"DaemonSet\")){print; f=1} END{if(!f) print \"(해당 없음)\"}'
  fi
  exit \$rc"

# 보안 리뷰 지적(2026-09-14): 무작위로 뽑힌 Pod의 애플리케이션 로그에 토큰/암호/PII가
# 찍혀 있으면 그대로 리포트에 남는다 — 흔한 시크릿 패턴을 최선노력으로 마스킹한다
# (완전한 시크릿 탐지는 불가능하므로 이건 심층방어이지 보장이 아님).
# 대상 확대(2026-09-15, 이주석 제안) — 무작위 Running Pod 1개가 아니라, 바로 위 3-10에서
# 찾은 non-Running(Terminating/Init 등) Pod들의 로그를 우선 조회한다(리포트 크기 관리를
# 위해 최대 5개·각 --tail=20으로 제한). non-Running Pod가 없으면 기존처럼 대표 Pod 로그.
run_cmd "3-11" "Pod 로그 조회 — non-Running Pod 우선(시크릿 패턴 마스킹 적용)" "oc logs <non-Running pod> -n <ns> --tail=20 (최대 5개) / 없으면 대표 Pod --tail=100" -- bash -c "
  rc=0
  mask_secrets() { sed -E 's/(password|passwd|token|secret|apikey|api_key|access_key|authorization)([[:space:]]*[:=][[:space:]]*).+/\1\2***MASKED***/gI; s/Bearer [A-Za-z0-9._-]+/Bearer ***MASKED***/g; s/AKIA[0-9A-Z]{16}/***MASKED_AWS_KEY***/g'; }
  NONRUNNING=\$(oc get pods -A --field-selector=status.phase!=Running -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name --no-headers 2>/dev/null | head -5)
  if [ -n \"\$NONRUNNING\" ]; then
    TOTAL=\$(oc get pods -A --field-selector=status.phase!=Running --no-headers 2>/dev/null | wc -l | tr -d ' ')
    echo \"[non-Running Pod \$TOTAL개 중 최대 5개 로그 표시]\"
    while read -r pns pname; do
      echo \"--- \${pns}/\${pname} ---\"
      oc logs \"\$pname\" -n \"\$pns\" --tail=20 2>&1 | mask_secrets || rc=1
      echo ''
    done <<< \"\$NONRUNNING\"
  elif [ -n '$Q_NS' ] && [ -n '$Q_POD' ]; then
    echo '[non-Running Pod 없음 — 대표 Pod 로그로 대체]'
    oc logs '$Q_POD' -n '$Q_NS' --tail=100 2>&1 | mask_secrets || rc=\$?
  else
    echo '(Pod 없음 - 건너뜀)'
  fi
  exit \$rc"

# kube-apiserver 헬스 + kubelet 상태 — 고객 요구사항(2026-09-15, 백인균). "API 연동 확인"의
# 원래 목적(API 서비스 자체가 정상인지)에 가장 직접적인 지표. `oc get --raw /healthz`는
# 현재 kubeconfig가 가리키는 apiserver에 직접 헬스체크를 보낸다(임의 IP:port curl과 동일 효과).
run_cmd "3-12" "kube-apiserver Health / kubelet 상태 확인" "oc get --raw /healthz / oc get nodes (kubelet Ready 조건)" -- bash -c "
  rc=0
  echo '[kube-apiserver /healthz]'
  oc get --raw /healthz || rc=\$?
  echo ''
  echo ''
  echo '[kubelet 상태 — Node Ready 조건]'
  oc get nodes -o custom-columns=NAME:.metadata.name,KUBELET_READY:.status.conditions[-1].status,MSG:.status.conditions[-1].message || rc=\$?
  exit \$rc"

# ════════════════════════════════════════════════════════════
section "4. Network 상태 확인"
# 3번 앞에서 자동 탐지한 대상을 기본값으로 재사용
N_NODE="$Q_NODE"
N_TARGET_IP="$Q_NODE_TARGET_IP"
N_NS="$Q_NS"
N_POD="$Q_POD"
N_PEER_IP="$Q_PEER_IP"
N_ROUTE="$Q_ROUTE"

# score-debug 전용 디버그 Pod(ping/traceroute/tcpdump 등 포함)가 떠 있으면
# 4-2(Pod간 통신) 테스트'만' 이걸 우선 사용 (ping 바이너리 보장).
# ※ N_NS/N_ROUTE는 그대로 두어 4-3/4-4는 원래 자동 탐지된 대상(aap 등)을
#   그대로 점검한다 — 예전 버전은 여기서 N_NS 전체를 score-debug로 바꿔버려
#   4-3(route 조회)이 엉뚱한 네임스페이스를 보는 버그가 있었음(수정됨).
# 만들기: oc create deployment score-debug --image=<내부미러레지스트리>/tools/score-debug:latest -n score-debug -- sleep infinity
PING_NS="$N_NS"
PING_POD="$N_POD"
NETDEBUG_NS="score-debug"
NETDEBUG_POD=$(oc get pods -n "$NETDEBUG_NS" -l app=score-debug --field-selector=status.phase=Running \
  -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
assert_safe_name "NETDEBUG_POD" "$NETDEBUG_POD" || NETDEBUG_POD=""
if [ -n "$NETDEBUG_POD" ]; then
  PING_NS="$NETDEBUG_NS"
  PING_POD="$NETDEBUG_POD"
  raw "[4-2용 대상 Pod 교체] score-debug Pod 사용: ${PING_NS}/${PING_POD} (4-3/4-4는 원래 자동 탐지 대상 ${N_NS}/${N_POD} 유지)"
fi

# 전체 노드로 확대 + 실사용 인터페이스만 표시(2026-09-15, 백인균 제안) — 기존엔 노드 1대만
# 확인했고 lo까지 다 나와 가독성이 떨어졌음. `ip -o addr`(주소 할당된 인터페이스만, 한 줄당
# 1개)에서 lo와 IPv6 link-local(fe80, 노이즈성) 행만 제외한다. 노드 간 ping은 기존처럼
# 대표 노드쌍 1회.
# [코드리뷰 수정: 최초 구현은 `grep 'state UP'`을 썼으나 `ip -o addr` 출력에는 그 텍스트가
#  존재하지 않아(그건 `ip link` 전용 필드) 항상 매치 실패로 무의미했음 — addr 출력 자체가
#  "주소가 할당된" 인터페이스만 보여주므로 상태 필터 없이 lo/link-local만 제외하는 것으로 교체]
# 실운영 중 발견(2026-09-15): 전체 노드로 확대하면서 노드 1대가 API 연결 지연 등으로
# oc debug가 멈추면 나머지 노드는 물론 스크립트 전체가 무한정 걸린다 — 노드별로 timeout을
# 걸어 한 노드가 막혀도 나머지는 계속 진행되게 한다(실제로 실클러스터 검증 중 master03에서
# TLS handshake 지연으로 oc debug가 11분 넘게 걸린 것을 발견하고 추가).
run_cmd "4-1" "Node Network Interface 연동 확인(전체 노드, 실사용 인터페이스만)" "oc debug node/<각 노드> -- chroot /host ip -o a (lo/link-local 제외, 노드당 60초 timeout)" -- bash -c "
  rc=0
  for n in $_NODES_LIST; do
    echo \"=== \$n ===\"
    OUT=\$(timeout 60 oc debug node/\"\$n\" -- chroot /host ip -o a 2>&1)
    trc=\$?
    if [ \"\$trc\" -eq 124 ]; then
      echo \"[경고] \$n : oc debug 60초 타임아웃 — 노드 응답 지연 또는 API 연결 문제 가능성, 직접 확인 필요\"
      rc=1
      continue
    fi
    [ \"\$trc\" -ne 0 ] && rc=\$trc
    echo \"\$OUT\" | grep -v '^[0-9]*: lo' | grep -v 'inet6 fe80' || echo '(표시할 인터페이스 없음)'
  done
  if [ -n '$N_NODE' ] && [ -n '$N_TARGET_IP' ]; then
    echo ''
    echo \"--- 노드간 ping: \$N_NODE -> \$N_TARGET_IP ---\"
    timeout 30 oc debug node/'$N_NODE' -- chroot /host ping -c 3 '$N_TARGET_IP' || rc=\$?
  else
    echo '(대상 노드 IP 없음 - ping 건너뜀)'
  fi
  exit \$rc"

run_cmd "4-2" "Pod간 Networking 확인" "oc get pod -o wide / oc rsh -> ping" -- bash -c "
  rc=0
  if [ -n '$PING_NS' ]; then oc get pod -o wide -n '$PING_NS' || rc=\$?; else echo '(네임스페이스 없음 - 건너뜀)'; fi
  if [ -n '$PING_NS' ] && [ -n '$PING_POD' ] && [ -n '$N_PEER_IP' ]; then
    oc rsh -n '$PING_NS' '$PING_POD' ping -c 3 '$N_PEER_IP' || rc=\$?
  else
    echo '(Pod 또는 통신 대상 IP 없음 - ping 건너뜀)'
  fi
  exit \$rc"

# 축소(2026-09-15, 백인균 제안) — svc -o wide 상세 대신 서비스 목록만 + curl 실검증에 집중.
run_cmd "4-3" "Cluster 외부-내부 Networking 확인" "oc get svc -n <ns> / curl" -- bash -c "
  rc=0
  if [ -n '$N_NS' ]; then
    oc get svc -n '$N_NS' || rc=\$?
    if [ -n '$N_ROUTE' ]; then
      URL=\$(oc get route '$N_ROUTE' -n '$N_NS' -o jsonpath='{.spec.host}') || rc=\$?
      [ -n \"\$URL\" ] && { curl -sk -o /dev/null -w 'HTTP %{http_code}\\n' \"https://\$URL\" || rc=\$?; }
    else
      echo '(Route 없음 - curl 건너뜀)'
    fi
  else
    echo '(네임스페이스 없음 - 건너뜀)'
  fi
  exit \$rc"

# 축소(2026-09-15, 이주석/백인균 제안) — describe pod 전체 덤프는 불필요, network-status
# annotation만으로 Multus 추가 IP 할당 여부 확인 가능.
run_cmd "4-4" "Pod 추가 네트워크(Multus) IP 할당 확인" "network-status annotation" -- bash -c "
  rc=0
  if [ -n '$N_NS' ] && [ -n '$N_POD' ]; then
    echo '--- network-status annotation ---'
    oc get pod '$N_POD' -n '$N_NS' -o jsonpath='{.metadata.annotations.k8s\.v1\.cni\.cncf\.io/network-status}' || rc=\$?
    echo ''
  else
    echo '(대상 Pod 없음 - 건너뜀)'
  fi
  exit \$rc"

run_cmd "4-5" "Multus/OVN-Kubernetes 네트워크 플러그인 Pod 상태 확인" "oc get pods -n openshift-multus / oc get pods -n openshift-ovn-kubernetes" -- bash -c "
  rc=0
  oc get pods -n openshift-multus || rc=\$?
  echo '--- openshift-ovn-kubernetes ---'
  oc get pods -n openshift-ovn-kubernetes || rc=\$?
  exit \$rc"

# ════════════════════════════════════════════════════════════
section "5. Virtualization 점검"
command -v virtctl &>/dev/null || warn "virtctl CLI가 없습니다 — 5-1~5-3(VM 기동/마이그레이션/콘솔)은 건너뜁니다."
raw "[자동 탐지된 VM] ${V_NS:-없음}/${V_VM:-없음}"

# 5-1, 5-2 는 VM 상태를 바꾸는 테스트라 기본적으로 자동 실행하지 않음.
# RUN_VM_DISRUPTIVE=yes ./OCP-HCK-Score.sh 로 실행한 경우에만, 그것도 클러스터
# 전체 무작위 VM이 아니라 "healthcheck.ocp.score/disruptive-test=allowed" 라벨이
# 붙은 VM(V_NS_SAFE/V_VM_SAFE)에 대해서만 수행한다 — 운영 VM 오선정 방지.
CAN_VMTEST=0
SKIP_REASON=""
if ! command -v virtctl &>/dev/null; then
  SKIP_REASON="virtctl CLI 없음"
elif [ "$RUN_VM_DISRUPTIVE" != "yes" ]; then
  SKIP_REASON="정책상 건너뜀(기본값, 운영 영향 방지) — RUN_VM_DISRUPTIVE=yes 로 재실행하면 수행"
elif [ -z "$V_NS_SAFE" ] || [ -z "$V_VM_SAFE" ]; then
  SKIP_REASON="파괴적 테스트 허용 라벨(healthcheck.ocp.score/disruptive-test=allowed)이 붙은 VM이 없어 건너뜀 — 'oc label vm <name> -n <ns> healthcheck.ocp.score/disruptive-test=allowed' 로 테스트용 VM에 라벨을 붙이세요"
else
  CAN_VMTEST=1
  raw "[파괴적 테스트 대상] ${V_NS_SAFE}/${V_VM_SAFE} (라벨 healthcheck.ocp.score/disruptive-test=allowed 로 선정)"
fi

# 정기점검 범위 명확화(2026-09-15, 백인균 제안) — 5-1/5-2는 VM 상태를 바꾸는
# 구축/변경검증 성격의 테스트라 월간 정기점검에서는 기본 제외(RUN_VM_DISRUPTIVE=yes일
# 때만 수행되는 기존 게이트가 이미 이 결정을 구현하고 있음 — 라벨 문구로 명확화).
item_header "5-1" "VM 기동/재기동/종료 정상 동작 확인 [구축/변경검증용 — 정기점검 기본 제외]" "virtctl start/stop <vm> -n <ns> / oc get vm,vmi -n <ns>"
if [ "$CAN_VMTEST" -eq 1 ]; then
  raw "[테스트 전 상태]"; oc get vm,vmi -n "$V_NS_SAFE" >>"$REPORT" 2>&1
  rc51=0
  # stop~start 사이 중단(Ctrl-C/세션 끊김 등) 시 VM을 다시 start해 방치하지 않는다.
  trap 'virtctl start "$V_VM_SAFE" -n "$V_NS_SAFE" >>"$REPORT" 2>&1 || true' EXIT
  virtctl stop "$V_VM_SAFE" -n "$V_NS_SAFE" >>"$REPORT" 2>&1 || rc51=1
  stopped=0
  for _ in $(seq 1 12); do
    sleep 5
    st=$(oc get vmi "$V_VM_SAFE" -n "$V_NS_SAFE" -o jsonpath='{.status.phase}' 2>/dev/null)
    # stop이 완료되면 VMI 자체가 삭제되어 조회 결과가 빈 값이 되는 것도 정상 종료다.
    if [ -z "$st" ]; then stopped=1; break; fi
  done
  raw "[stop 후 상태 — 최대 60초 폴링]"; oc get vm,vmi -n "$V_NS_SAFE" >>"$REPORT" 2>&1
  if [ "$stopped" -eq 0 ]; then
    raw "[경고] 60초 내 Stopped 상태 도달 실패"
    rc51=1
  fi
  virtctl start "$V_VM_SAFE" -n "$V_NS_SAFE" >>"$REPORT" 2>&1 || rc51=1
  running=0
  for _ in $(seq 1 12); do
    sleep 5
    st=$(oc get vmi "$V_VM_SAFE" -n "$V_NS_SAFE" -o jsonpath='{.status.phase}' 2>/dev/null)
    if [ "$st" = "Running" ]; then running=1; break; fi
  done
  raw "[start 후 상태 — 최대 60초 폴링]"; oc get vm,vmi -n "$V_NS_SAFE" >>"$REPORT" 2>&1
  if [ "$running" -eq 0 ]; then
    raw "[경고] 60초 내 Running 상태 도달 실패"
    rc51=1
  fi
  trap - EXIT
  raw "[결과] rc=${rc51}"
  if [ "$rc51" -eq 0 ]; then
    ok "5-1 VM 기동/재기동/종료 확인 — Stopped/Running 상태 도달 확인됨"
  else
    FAIL_COUNT=$((FAIL_COUNT+1))
    FAILED_ITEMS+=("5-1")
    warn "5-1 VM 기동/재기동/종료 확인 실패(상태 미도달 또는 명령 실패) — 리포트 확인"
  fi
else
  raw "[건너뜀: ${SKIP_REASON}]"
  raw "[결과] skip"
  warn "5-1 건너뜀 (${SKIP_REASON})"
fi

item_header "5-2" "Live Migration 동작 확인 [구축/변경검증용 — 정기점검 기본 제외]" "virtctl migrate <vm> -n <ns> / oc get vmim -n <ns>"
if [ "$CAN_VMTEST" -eq 1 ]; then
  rc52=0
  virtctl migrate "$V_VM_SAFE" -n "$V_NS_SAFE" >>"$REPORT" 2>&1 || rc52=1
  log "Migration 진행 대기 중 (최대 90초 폴링)..."
  migstate=""
  for _ in $(seq 1 18); do
    sleep 5
    migstate=$(oc get vmim -n "$V_NS_SAFE" --sort-by=.metadata.creationTimestamp \
      -o jsonpath='{range .items[*]}{.status.phase}{"\n"}{end}' 2>/dev/null | tail -1)
    if [ "$migstate" = "Succeeded" ] || [ "$migstate" = "Failed" ]; then break; fi
  done
  raw "[Migration 폴링 종료 후 상태 — 최대 90초]"; oc get vmim -n "$V_NS_SAFE" >>"$REPORT" 2>&1
  if [ "$migstate" != "Succeeded" ]; then
    raw "[경고] 90초 내 Succeeded 도달 실패 (최종 상태: ${migstate:-확인불가})"
    rc52=1
  fi
  raw "[결과] rc=${rc52}"
  if [ "$rc52" -eq 0 ]; then
    ok "5-2 Live Migration 확인 — Succeeded 도달 확인됨"
  else
    FAIL_COUNT=$((FAIL_COUNT+1))
    FAILED_ITEMS+=("5-2")
    warn "5-2 Live Migration 확인 실패(Succeeded 미도달 또는 명령 실패) — 리포트 확인"
  fi
else
  raw "[건너뜀: ${SKIP_REASON}]"
  raw "[참고] 실제 마이그레이션을 트리거하지 않는 읽기전용 조회 — 현재 클러스터의 VirtualMachineInstanceMigration 목록:"
  oc get vmim -A >>"$REPORT" 2>&1
  raw "[결과] skip"
  warn "5-2 건너뜀 (${SKIP_REASON}) — 기존 vmim 목록은 리포트에 기록됨"
fi

item_header "5-3" "VM Console 접속 확인" "virtctl console <vm> -n <ns>"
raw "[수동 확인 필요] 아래 명령을 별도 터미널에서 직접 실행하여 콘솔 접속을 확인하세요:"
if [ -n "$V_NS" ] && [ -n "$V_VM" ]; then
  raw "  virtctl console ${V_VM} -n ${V_NS}"
else
  raw "  virtctl console <vm-name> -n <ns-name>"
fi
raw "[결과] manual"
warn "5-3 VM Console 접속은 대화형 세션이라 자동 실행할 수 없습니다 — 수동으로 확인하세요."

run_cmd "5-4" "VM CPU/Memory 리소스 사용률 확인" "oc adm top pod -n <ns> -l kubevirt.io=virt-launcher" -- bash -c "
  if [ -n '$V_NS' ]; then oc adm top pod -n '$V_NS' -l kubevirt.io=virt-launcher; else echo '(VM 없음 - 건너뜀)'; fi"
# 관점 전환(2026-09-15, 백인균 제안) — 단순 Bound 확인보다, reclaimPolicy로 남아있는
# Released PV와 Succeeded가 아닌 상태로 오래 머무는 DataVolume이 실무적으로 더 유의미.
run_cmd "5-5" "VM 디스크(DataVolume/PVC) 바인딩 상태 확인 — Released PV / 비정상 DV 점검 포함" "oc get dv,pvc -n <ns> / oc get pv (Released 필터) / oc get dv -A (non-Succeeded 필터)" -- bash -c "
  rc=0
  if [ -n '$V_NS' ]; then oc get dv,pvc -n '$V_NS' || rc=\$?; else echo '(VM 없음 - 건너뜀)'; fi
  echo ''
  echo '[확인 필요 — Released 상태로 남아있는 PV (reclaimPolicy로 재사용 안 된 채 방치)]'
  RELEASED=\$(oc get pv --field-selector=status.phase=Released --no-headers 2>/dev/null)
  if [ -n \"\$RELEASED\" ]; then echo \"\$RELEASED\"; rc=1; else echo '(해당 없음)'; fi
  echo ''
  echo '[확인 필요 — Succeeded가 아닌 상태의 DataVolume(클러스터 전체)]'
  # [코드리뷰 수정] --no-headers 출력의 고정 컬럼 위치(\$5)에 의존했으나 CDI 버전마다
  # printer-column 구성이 달라질 수 있어 실제로는 PHASE가 \$3인 경우가 많고 전체 DV가
  # 항상 오탐되는 결함이었음 — status.phase를 jsonpath로 명시 지정해 버전에 안전하게 함.
  DV_BAD=\$(oc get dv -A -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,PHASE:.status.phase --no-headers 2>/dev/null | awk '\$3!=\"Succeeded\"')
  if [ -n \"\$DV_BAD\" ]; then echo \"\$DV_BAD\"; rc=1; else echo '(해당 없음 — 전부 Succeeded)'; fi
  exit \$rc"
# 단순화(2026-09-15, 천민솔 제안) vs 상세유지(이주석 제안) 절충 — 존재/생성 개수는
# 항상 노출하는 요약으로 두고("생성 조건 충족 여부"만 한눈에), yaml 상세는 접어서 필요할
# 때만 펼쳐보게 한다. 둘 다 만족.
run_cmd "5-6" "NodeHealthCheck / Fence Agent 동작 확인" "oc get nhc / oc get far -A (개수 요약) / 상세는 접힘" -- bash -c "
  rc=0
  NHC_COUNT=\$(oc get nhc --no-headers 2>/dev/null | wc -l | tr -d ' ')
  FAR_COUNT=\$(oc get far -A --no-headers 2>/dev/null | wc -l | tr -d ' ')
  echo \"[요약] NHC \${NHC_COUNT}개, FAR(FenceAgentsRemediation) \${FAR_COUNT}개 — FAR은 노드 장애/리붓 시 생성되는 게 정상 동작이며, 0개면 최근 격리 이벤트 없음\"
  echo '===== 아래는 상세 원본(참고용) ====='
  oc get nhc || rc=\$?
  oc get far -A || rc=\$?
  if [ \"\$FAR_COUNT\" -gt 0 ]; then
    echo ''
    echo '[FenceAgentsRemediation 상세 — 리붓 등 발생 원인 확인용, BMC/IPMI 자격증명 마스킹 적용]'
    oc get far -A -o yaml \
      | sed -E 's/((password|passwd|secret|token)[[:space:]]*:[[:space:]]*).+/\1\"***MASKED***\"/gI; s/(--?(password|passwd|secret|token)[= ]+)[^ ]+/\1***MASKED***/gI' || rc=\$?
  fi
  exit \$rc"

run_cmd "5-7" "KubeVirt/CDI 플랫폼 컴포넌트 상태 확인" "oc get hco -n openshift-cnv / oc get pods -n openshift-cnv -l kubevirt.io -o wide" -- bash -c "
  rc=0
  oc get hco -n openshift-cnv || rc=\$?
  echo '--- virt-*/cdi-* Pod 상태 ---'
  oc get pods -n openshift-cnv -l 'kubevirt.io in (virt-operator,virt-controller,virt-handler,virt-api)' -o wide || rc=\$?
  oc get pods -n openshift-cnv -l 'cdi.kubevirt.io' || rc=\$?
  echo ''
  echo '[virt-handler DaemonSet 워커 노드 커버리지 확인]'
  WORKERS=\$(oc get nodes -l node-role.kubernetes.io/worker -o custom-columns=NAME:.metadata.name --no-headers 2>/dev/null | LC_ALL=C sort -u)
  VH_NODES=\$(oc get pods -n openshift-cnv -l kubevirt.io=virt-handler -o custom-columns=NODE:.spec.nodeName --no-headers 2>/dev/null | LC_ALL=C sort -u)
  MISSING=\$(LC_ALL=C comm -23 <(printf '%s\n' \"\$WORKERS\") <(printf '%s\n' \"\$VH_NODES\"))
  if [ -n \"\$MISSING\" ]; then
    echo \"[경고] virt-handler가 기동되지 않은 워커 노드: \$MISSING\"
    rc=1
  else
    echo '(모든 워커 노드에 virt-handler 기동 확인됨)'
  fi
  exit \$rc"

# request 메모리 기준 스케줄링 실패(실사용량이 아니라 Allocated request 소진율이 원인)를
# 진단하려면 노드별 Capacity/Allocatable/Allocated resources가 필요하다는 고객 요구사항
# 반영(2026-09-14). 대상은 위에서 이미 자동 탐지해둔 전체 노드 목록(_NODES)을 그대로 재사용.
_NODES_LIST="${_NODES[*]}"
# 워커 노드만 한눈에 비교할 수 있는 요약 표를 먼저 보여달라는 고객 추가 요구사항(2026-09-14) —
# 상세 블록(전체 노드)과는 별개로 워커 노드만 골라 메모리 Allocatable/Request/Limit 비율을 한 줄씩.
_WORKERS_LIST="$(oc get nodes -l node-role.kubernetes.io/worker \
  -o jsonpath='{range .items[*]}{.metadata.name}{" "}{end}' 2>/dev/null)"
run_cmd "5-8" "노드별 메모리 Capacity/Allocatable/Allocated(Request 소진율) 확인" "oc describe node <각 노드> | sed -n '/Capacity:/,/Allocatable:/p;/Allocatable:/,/System Info:/p' / grep -A10 'Allocated resources'" -- bash -c "
  rc=0
  printf '%-20s %-15s %-20s %-20s\n' 'WORKER NODE' 'ALLOCATABLE' 'MEM_REQUEST(%)' 'MEM_LIMIT(%)'
  printf '%-20s %-15s %-20s %-20s\n' '----' '-----------' '---------------' '---------------'
  for n in $_WORKERS_LIST; do
    WD=\$(oc describe node \"\$n\") || rc=\$?
    WALLOC=\$(echo \"\$WD\" | awk '/^Allocatable:/{f=1;next} f && /memory:/{print \$2; exit}')
    read -r _ WREQV WREQP WLIMV WLIMP <<<\"\$(echo \"\$WD\" | awk '/^Allocated resources:/{f=1} f && /^  memory /{print; exit}')\"
    # 단위 통일(2026-09-15, 백인균 제안) — WALLOC은 이미 Ki 단위인데 WREQV/WLIMV는 raw byte라
    # 단위가 안 맞았음. numfmt로 사람이 읽기 쉬운 단위(Ki/Mi/Gi)로 통일(numfmt 없으면 raw 유지).
    # [코드리뷰 수정] --from 미지정 시 기본이 'none'이라 입력에 Mi/Gi 접미사가 붙어 있으면
    # invalid number 에러로 매번 실패해(에러는 숨겨짐) 사실상 no-op였음 — --from=auto로 raw byte든
    # 이미 접미사가 붙은 값이든 둘 다 정확히 인식하도록 수정.
    WREQV_H=\$(numfmt --from=auto --to=iec \"\$WREQV\" 2>/dev/null || echo \"\$WREQV\")
    WLIMV_H=\$(numfmt --from=auto --to=iec \"\$WLIMV\" 2>/dev/null || echo \"\$WLIMV\")
    printf '%-20s %-15s %-20s %-20s\n' \"\$n\" \"\$WALLOC\" \"\$WREQV_H \$WREQP\" \"\$WLIMV_H \$WLIMP\"
  done
  echo '===== 아래는 상세 원본(참고용) ====='
  echo ''
  for n in $_NODES_LIST; do
    echo \"=== \$n ===\"
    D=\$(oc describe node \"\$n\") || rc=\$?
    # -A2 고정폭은 KubeVirt bridge/device 플러그인 항목 수가 노드마다 달라서 cpu/memory/pods
    # 같은 핵심 값을 놓칠 수 있었음(2026-09-14 첫 구현 버그, 실클러스터에서 발견) — Capacity:/
    # Allocatable: 블록을 다음 헤더 직전까지 정확히 잘라내는 방식으로 교체.
    echo \"\$D\" | sed -n '/^Capacity:/,/^Allocatable:/{/^Allocatable:/!p}'
    echo \"\$D\" | sed -n '/^Allocatable:/,/^System Info:/{/^System Info:/!p}'
    echo \"\$D\" | grep -A10 'Allocated resources'
    echo ''
  done
  exit \$rc"

# 관점 전환(2026-09-15, 백인균 제안) — 설정값 자체보다 "설정 대비 실사용"이 중요하다는
# 지적 반영. 워커 노드 중 메모리 request 소진율이 100%를 넘는(실질적으로 오버커밋이
# 실제로 벌어지고 있는) 노드를 자동으로 골라낸다.
run_cmd "5-9" "OpenShift Virtualization 메모리 Overcommit 설정 및 실사용 대비 확인" "oc get hyperconverged ... higherWorkloadDensity / 워커 노드별 memory request 소진율 100% 초과 여부" -- bash -c "
  rc=0
  OVERCOMMIT=\$(oc get hyperconverged kubevirt-hyperconverged -n openshift-cnv -o jsonpath='{.spec.higherWorkloadDensity}' 2>/dev/null) || rc=\$?
  echo \"[Overcommit 설정] higherWorkloadDensity: \${OVERCOMMIT:-미설정(기본 비활성)}\"
  echo ''
  echo '[설정 대비 실사용 — 메모리 request 소진율이 100%를 넘는 워커 노드]'
  FOUND=0
  for n in $_WORKERS_LIST; do
    WD=\$(oc describe node \"\$n\" 2>/dev/null)
    # [코드리뷰 수정] 이 memory 라인엔 Requests(%)/Limits(%) 두 퍼센트가 같이 있어서
    # grep -oE가 둘 다 매치해 WREQP가 2줄짜리 값이 되고 이후 -ge 비교가 조용히 항상 실패하던
    # 결함이었음 — head -1로 첫 번째(Requests) 값만 취하도록 수정.
    WREQP=\$(echo \"\$WD\" | awk '/^Allocated resources:/{f=1} f && /^  memory /{print; exit}' | grep -oE '\([0-9]+%\)' | head -1 | tr -d '()%')
    if [ -n \"\$WREQP\" ] && [ \"\$WREQP\" -ge 100 ] 2>/dev/null; then
      echo \"[확인 필요] \$n : memory request \${WREQP}% (오버커밋이 실제로 발생 중)\"
      FOUND=1
    fi
  done
  [ \"\$FOUND\" -eq 0 ] && echo '(request 100%를 넘는 워커 노드 없음)'
  exit \$rc"

# 고객 요구사항 추가분(2026-09-14): "노드별 Pod request 상세"는 실제로는 "전체 VM
# (virt-launcher) Pod의 memory request"를 뜻했음 — 특정 노드명이 필요 없어 클러스터
# 전체를 한 번에 자동 점검 가능(특정 VM의 request 확인도 이 표에 포함되므로 별도 항목 불필요).
run_cmd "5-10" "전체 VM(virt-launcher) Pod의 memory request 확인" "oc get pods -A -l kubevirt.io=virt-launcher -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,NODE:.spec.nodeName,REQ:.spec.containers[*].resources.requests.memory" -- oc get pods -A -l kubevirt.io=virt-launcher -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,NODE:.spec.nodeName,REQ:.spec.containers[*].resources.requests.memory

# FailedScheduling은 특정 Pod명을 미리 알아야 하는 진단 명령이었으나, 현재 클러스터에
# 실제로 발생 중인 이벤트를 직접 조회하면 대상을 몰라도 자동 점검 가능(없으면 "정상").
run_cmd "5-11" "VM 스케줄링 실패(FailedScheduling) 이벤트 확인" "oc get events -A --field-selector reason=FailedScheduling --sort-by=.lastTimestamp" -- oc get events -A --field-selector reason=FailedScheduling --sort-by=.lastTimestamp

# VM 실행 정책 감사 — 고객 요구사항(2026-09-14). spec.running은 deprecated 필드라 남아있으면
# 제거가 필요하고, runStrategy는 RerunOnFailure를 권장한다는 고객 가이드를 읽기전용으로 감사만
# 한다(클러스터 상태를 바꾸는 oc patch/for문은 이 점검의 범위 밖 — 사람이 직접 판단 후 적용).
run_cmd "5-12" "VM 실행 정책(spec.running/runStrategy) 설정 확인" "oc get vm -A -o custom-columns=NAME:.metadata.name,RUNNING:.spec.running,RUNSTRATEGY:.spec.runStrategy" -- bash -c "
  rc=0
  RAW=\$(oc get vm -A -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,RUNNING:.spec.running,RUNSTRATEGY:.spec.runStrategy --no-headers 2>/dev/null) || rc=\$?
  if [ -z \"\$RAW\" ]; then
    echo '(클러스터에 VM 없음)'
  else
    echo \"\$RAW\"
    echo ''
    echo '[확인 필요 — spec.running(deprecated) 잔존 또는 runStrategy가 RerunOnFailure가 아님]'
    FLAGGED=\$(echo \"\$RAW\" | awk '\$3!=\"<none>\" || \$4!=\"RerunOnFailure\"')
    if [ -n \"\$FLAGGED\" ]; then
      echo \"\$FLAGGED\"
      echo '[안내] spec.running은 더 이상 제공되지 않는 deprecated 필드입니다 — 마이그레이션/VM 생성 시'
      echo '       이 필드가 남아있다면 제거하고 runStrategy를 RerunOnFailure로 맞추는 것을 권장합니다.'
      echo '       이 점검은 읽기전용이라 자동 변경하지 않으니, oc patch vm 명령으로 직접 적용하세요.'
    else
      echo '(모든 VM이 RerunOnFailure로 설정되어 있고 spec.running 잔존 없음)'
    fi
  fi
  exit \$rc"

# ════════════════════════════════════════════════════════════
write ""
write "════════════════════════════════════════════════════════"
write "점검 종료 시각 : $(date)"
write "════════════════════════════════════════════════════════"

# ── HTML 대시보드 리포트 생성 (python3 있을 때만 — 텍스트 리포트는 항상 산출됨) ──
# 원본 .txt를 파싱해 노드 토폴로지/Operator 상태 도넛/항목별 수집현황을 갖춘
# 단일 HTML 파일로 재구성한다. 브라우저의 인쇄(Ctrl+P) → PDF로 저장 기능으로
# PDF 변환도 가능(별도 PDF 라이브러리 의존성 없이 브라우저 네이티브 기능 사용).
if [ "$HAS_PY" -eq 1 ]; then
  if python3 - "$REPORT" "$HTML_REPORT" <<'PYEOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parses OCP-HCK-Score.sh's raw .txt report into a structured HTML dashboard.
Usage: python3 THIS.py <report.txt> <out.html>"""
import re, html, sys

if len(sys.argv) != 3:
    print("usage: build_report.py <report.txt> <out.html>", file=sys.stderr)
    sys.exit(2)
SRC, OUT = sys.argv[1], sys.argv[2]

with open(SRC, encoding="utf-8", errors="replace") as f:
    text = f.read()
lines = text.split("\n")

SEP = "════════════════════════════════════════════════════════"
DASH = "--------------------------------------------------------"

# ---- header ----
header = {}
for ln in lines[:4]:
    if "점검 대상 클러스터" in ln: header["server"] = ln.split(":", 1)[1].strip()
    if "점검 수행 계정" in ln: header["user"] = ln.split(":", 1)[1].strip()
    if "점검 시작 시각" in ln: header["start"] = ln.split(":", 1)[1].strip()
end_match = re.search(r"점검 종료 시각\s*:\s*(.+)", text)
header["end"] = end_match.group(1).strip() if end_match else ""

# ---- split into top-level sections by "■ N. Title" ----
sec_re = re.compile(r"^■ (\d+)\. (.+)$")
sections = []  # list of (num, title, body_lines)
cur = None
for ln in lines:
    m = sec_re.match(ln)
    if m:
        cur = {"num": m.group(1), "title": m.group(2), "lines": []}
        sections.append(cur)
    elif cur is not None and ln != SEP:
        cur["lines"].append(ln)

def skip_or_attention(body):
    if "건너뜀" in body:
        return "skip"
    if re.search(r"\berror:|Error from server|unauthorized|command not found|no such", body, re.I):
        return "attention"
    return "ok"

ITEM_HDR = re.compile(r"^\[(\d+-\d+(?:-\d+)?)\]\s+(.+)$")
# run_cmd/5-1/5-2/5-3 남기는 "[결과] rc=N|skip|manual" 마커 — 있으면 문자열 휴리스틱보다
# 우선해서 상태를 판정한다(실제 종료코드 기반, C4에서 리포트에 심음).
RESULT_LINE = re.compile(r"^\[결과\]\s+(rc=(\d+)|skip|manual)\s*$")

def parse_items(body_lines):
    """Split a section's body into item blocks delimited by DASH/[num] desc/Command/DASH."""
    items = []
    i = 0
    n = len(body_lines)
    while i < n:
        if body_lines[i] == DASH and i + 3 < n and ITEM_HDR.match(body_lines[i+1]):
            m = ITEM_HDR.match(body_lines[i+1])
            num, desc = m.group(1), m.group(2)
            cmd = body_lines[i+2].split(":", 1)[1].strip() if body_lines[i+2].startswith("Command") else ""
            j = i + 4
            out = []
            result_tag = None
            while j < n and body_lines[j] != DASH:
                rm = RESULT_LINE.match(body_lines[j])
                if rm and result_tag is None:
                    result_tag = rm.group(1)
                else:
                    out.append(body_lines[j])
                j += 1
            body_text = "\n".join(out).strip("\n")
            if result_tag == "skip":
                status = "skip"
            elif result_tag == "manual":
                status = "manual"
            elif result_tag is not None:
                status = "ok" if result_tag.split("=", 1)[1] == "0" else "attention"
            else:
                status = skip_or_attention(body_text)  # 마커 없는 항목용 폴백
            items.append({"num": num, "desc": desc, "cmd": cmd, "body": body_text, "status": status})
            i = j
        else:
            i += 1
    return items

# ---- section 1: nodes ----
sec1 = next(s for s in sections if s["num"] == "1")
items1 = parse_items(sec1["lines"])
# use 1-3 (wide) as authoritative node table
node_rows = []
for it in items1:
    if it["num"] == "1-3":
        rows = [r for r in it["body"].split("\n") if r.strip()]
        hdr = re.split(r"\s{2,}", rows[0].strip())
        for r in rows[1:]:
            cols = re.split(r"\s{2,}", r.strip())
            node_rows.append(dict(zip([h.lower() for h in hdr], cols)))

# ---- section 2: cluster operators ----
sec2 = next(s for s in sections if s["num"] == "2")
co_rows = []
extra_co_line = ""
for ln in sec2["lines"]:
    if ln.startswith("2-") and "|" in ln:
        parts = [p.strip() for p in ln.split("|")]
        if len(parts) >= 8:
            # idx | name | version | avail | prog | deg | since | verdict
            co_rows.append({"idx": parts[0], "name": parts[1], "version": parts[2],
                             "avail": parts[3], "prog": parts[4], "deg": parts[5],
                             "since": parts[6], "verdict": parts[7]})
        else:
            # 예상 밖 필드 수 — 판정 불가로 기록(크래시 방지)
            co_rows.append({"idx": parts[0], "name": parts[1] if len(parts) > 1 else "?",
                             "version": "", "avail": "", "prog": "", "deg": "", "since": "",
                             "verdict": "[형식 확인 필요 - 원본 확인]"})
    if ln.startswith("[목록 외 Operator 발견]"):
        extra_co_line = ln

auto_targets = []
in_targets = False
for ln in sec2["lines"]:
    if ln.startswith("[자동 탐지된 점검 대상]"):
        in_targets = True
        continue
    if in_targets:
        m = re.match(r"^\s{2}(\S.*?)\s*:\s*(.*)$", ln)
        if m:
            auto_targets.append((m.group(1).strip(), m.group(2).strip()))
        elif ln.strip() == "":
            in_targets = False

co_ok = sum(1 for r in co_rows if "정상" in r["verdict"])
co_warn = sum(1 for r in co_rows if "주의" in r["verdict"])
co_crit = sum(1 for r in co_rows if "이상" in r["verdict"])
co_unjudged = sum(1 for r in co_rows if "형식 확인 필요" in r["verdict"])
# jq는 있지만 oc get co 자체가 빈 응답이었던 것 — "정상"으로 절대 세지 않는다.
co_lookup_failed = sum(1 for r in co_rows if "조회 실패" in r["verdict"])
extra_co_names = []
m_extra = re.search(r"\[목록 외 Operator 발견\]\s*(.+?)\s*\(고정", extra_co_line)
if m_extra:
    extra_co_names = m_extra.group(1).split()

# ---- sections 3,4,5 ----
def get_sec(n):
    return next(s for s in sections if s["num"] == str(n))

items3 = parse_items(get_sec(3)["lines"])
items4 = parse_items(get_sec(4)["lines"])
items5 = parse_items(get_sec(5)["lines"])

def counts(items):
    return {
        "total": len(items),
        "ok": sum(1 for i in items if i["status"] == "ok"),
        "skip": sum(1 for i in items if i["status"] == "skip"),
        "attn": sum(1 for i in items if i["status"] == "attention"),
    }

c3, c4, c5 = counts(items3), counts(items4), counts(items5)

esc = html.escape

# ---------------------------------------------------------------- node topology
ROLE_LANES = [
    ("control-plane", "Control Plane"),
    ("infra", "Infra / Router"),
    ("worker", "Worker"),
]
def lane_for(roles):
    if "control-plane" in roles or "master" in roles: return 0
    if "infra" in roles or "router" in roles: return 1
    return 2

lanes = [[], [], []]
for n in node_rows:
    lanes[lane_for(n.get("roles", ""))].append(n)

def node_card(n):
    return f'''<div class="node-chip">
      <div class="node-chip-name">{esc(n.get("name",""))}</div>
      <div class="node-chip-meta"><span>{esc(n.get("internal-ip",""))}</span><span>{esc(n.get("version",""))}</span></div>
      <div class="node-chip-roles">{esc(n.get("roles",""))}</div>
    </div>'''

topology_html = ""
for idx, (key, label) in enumerate(ROLE_LANES):
    members = lanes[idx]
    if not members:
        continue
    topology_html += f'''<div class="lane">
      <div class="lane-head"><span class="lane-label">{label}</span><span class="lane-count">{len(members)}</span></div>
      <div class="lane-body">{"".join(node_card(n) for n in members)}</div>
    </div>'''

# ---------------------------------------------------------------- CO donut
total_judged = co_ok + co_warn + co_crit
def arc(offset, frac, color):
    if frac <= 0: return "", offset
    circumf = 2 * 3.14159265 * 54
    dash = frac * circumf
    seg = f'<circle class="ring-seg" cx="64" cy="64" r="54" fill="none" stroke="{color}" stroke-width="14" stroke-dasharray="{dash:.2f} {circumf:.2f}" stroke-dashoffset="{-offset:.2f}" transform="rotate(-90 64 64)"/>'
    return seg, offset + dash

segs = []
off = 0
for cnt, color in [(co_ok, "var(--good)"), (co_warn, "var(--warn)"), (co_crit, "var(--crit)")]:
    s, off = arc(off, (cnt / total_judged) if total_judged else 0, color)
    segs.append(s)
donut_svg = f'''<svg viewBox="0 0 128 128" class="donut" role="img" aria-label="Cluster Operator 상태 비율">
  <circle cx="64" cy="64" r="54" fill="none" stroke="var(--border)" stroke-width="14"/>
  {"".join(segs)}
  <text x="64" y="60" text-anchor="middle" class="donut-num">{co_ok}/{total_judged}</text>
  <text x="64" y="78" text-anchor="middle" class="donut-sub">정상</text>
</svg>'''

# ---------------------------------------------------------------- section coverage bars
def coverage_bar(sec_num, title, c):
    total = c["total"] or 1
    ok_pct = c["ok"] / total * 100
    skip_pct = c["skip"] / total * 100
    attn_pct = c["attn"] / total * 100
    return f'''<div class="cov-row">
      <div class="cov-label"><span class="cov-num">{sec_num}</span>{title}</div>
      <div class="cov-track" role="img" aria-label="{title}: 수집 {c['ok']}건, 건너뜀 {c['skip']}건, 확인필요 {c['attn']}건">
        <span class="cov-seg cov-ok" style="width:{ok_pct:.1f}%"></span><span class="cov-seg cov-skip" style="width:{skip_pct:.1f}%"></span><span class="cov-seg cov-attn" style="width:{attn_pct:.1f}%"></span>
      </div>
      <div class="cov-count">{c['ok']}/{c['total']}<span class="cov-count-dim"> 건 수집</span></div>
    </div>'''

coverage_html = (
    coverage_bar("3.", "API 연동", c3) +
    coverage_bar("4.", "Network", c4) +
    coverage_bar("5.", "Virtualization", c5)
)

# ---------------------------------------------------------------- CO table
# 가로 나열 칩 → 세로 표로 개선(2026-09-15, 김수용 제안) — 한눈에 스캔하기 쉽도록.
def co_row_cls(verdict):
    if "형식 확인 필요" in verdict or "조회 실패" in verdict:
        return "co-unjudged"
    elif "정상" in verdict:
        return "co-ok"
    elif "주의" in verdict:
        return "co-warn"
    return "co-crit"

def co_table_row(r):
    cls = co_row_cls(r["verdict"])
    return f'''<tr class="{cls}">
      <td class="mono">{esc(r["idx"])}</td>
      <td>{esc(r["name"])}</td>
      <td class="mono">{esc(r["version"])}</td>
      <td class="mono">{esc(r["avail"])}</td>
      <td class="mono">{esc(r["prog"])}</td>
      <td class="mono">{esc(r["deg"])}</td>
      <td class="mono">{esc(r["since"])}</td>
      <td><span class="co-badge {cls}">{esc(r["verdict"])}</span></td>
    </tr>'''

co_grid_html = f'''<table class="co-table">
  <thead><tr><th>NO</th><th>OPERATOR</th><th>VERSION</th><th>AVAILABLE</th><th>PROGRESSING</th><th>DEGRADED</th><th>SINCE</th><th>VERDICT</th></tr></thead>
  <tbody>{"".join(co_table_row(r) for r in co_rows)}</tbody>
</table>'''
extra_co_html = ""
if extra_co_names:
    chips = "".join(f'<div class="co-chip co-unknown"><span class="co-dot"></span>{esc(n)}</div>' for n in extra_co_names)
    extra_co_html = f'''<div class="co-extra">
      <div class="co-extra-label">⚑ 고정 34개 목록 밖 Operator (신규 발견 — 별도 확인 필요)</div>
      <div class="co-grid">{chips}</div>
    </div>'''

# ---------------------------------------------------------------- auto targets
targets_html = "".join(
    f'<div class="tgt"><div class="tgt-k">{esc(k)}</div><div class="tgt-v">{esc(v) if v else "없음"}</div></div>'
    for k, v in auto_targets
)

# ---------------------------------------------------------------- item sections (3/4/5)
STATUS_LABEL = {
    "ok": ("수집 완료", "st-ok"),
    "skip": ("건너뜀 · 대상/정책", "st-skip"),
    "attention": ("확인 필요", "st-attn"),
    "manual": ("수동 확인 필요", "st-manual"),
}

# 항목 원문에 이 구분선이 있으면, 그 앞부분(핵심 요약 테이블 등)은 드랍다운 밖에 항상 노출하고
# 뒷부분(상세 원본)만 접어서 보여준다 — "드랍다운을 펼쳐야만 요약을 볼 수 있다"는 피드백 반영.
# 사용자 요청(2026-09-14)으로 5-8(워커 노드 요약 표)에 처음 적용. FOLD_MARKER_ITEMS에 없는
# 항목에는 적용하지 않는다 — 3-7/3-10처럼 자유 텍스트(이벤트 메시지/Pod 로그)를 그대로 담는
# 항목까지 전역으로 검사하면, 우연히 같은 문구가 로그에 찍혔을 때 의도치 않게 분할될 수
# 있어서다(코드 리뷰 지적, 2026-09-14). 다른 항목에 재사용하려면 이 set에 번호를 추가할 것.
FOLD_MARKER = "===== 아래는 상세 원본(참고용) ====="
FOLD_MARKER_ITEMS = {"1-5", "3-1", "3-2", "3-3", "3-4", "3-5", "3-6", "5-6", "5-8"}

def item_block(it, open_attn=True):
    label, cls = STATUS_LABEL[it["status"]]
    open_attr = " open" if (it["status"] == "attention" and open_attn) else ""
    raw_body = it["body"]
    summary_html = ""
    if it["num"] in FOLD_MARKER_ITEMS and FOLD_MARKER in raw_body:
        summary_part, raw_body = raw_body.split(FOLD_MARKER, 1)
        summary_part = summary_part.strip("\n")
        if summary_part.strip():
            summary_html = f'<pre class="item-summary">{esc(summary_part)}</pre>'
    body = esc(raw_body) if raw_body.strip() else "(출력 없음)"
    return f'''<div class="item">
      <div class="item-head">
        <span class="item-num">{esc(it["num"])}</span>
        <span class="item-desc">{esc(it["desc"])}</span>
        <span class="item-status {cls}">{label}</span>
      </div>
      {summary_html}
      <details class="item-toggle{open_attr}">
        <summary>원본 로그 보기</summary>
        <div class="item-body">
          <div class="item-cmd">$ {esc(it["cmd"])}</div>
          <pre>{body}</pre>
        </div>
      </details>
    </div>'''

items1_html = "".join(item_block(i, open_attn=False) for i in items1)
items3_html = "".join(item_block(i) for i in items3)
items4_html = "".join(item_block(i) for i in items4)
items5_html = "".join(item_block(i) for i in items5)

# 아래 중 하나라도 걸리면 "확인 필요" — 무엇 하나라도 사람이 판정 못 한 게 있으면
# 절대 "전체 정상"으로 단정하지 않는다(구체적 원인은 각 카드/범례에서 확인).
co_unknown_total = co_unjudged + co_lookup_failed
overall_ok = (
    co_crit == 0 and co_warn == 0 and co_unknown_total == 0
    and not extra_co_names
    and c3["attn"] == 0 and c4["attn"] == 0 and c5["attn"] == 0
)
overall_label = "전체 정상" if overall_ok else "확인 필요 항목 있음"
overall_cls = "st-ok" if overall_ok else "st-attn"

skipped_total = c3["skip"] + c4["skip"] + c5["skip"]

_m = re.search(r"https?://([^:/]+)", header.get("server", ""))
_host = _m.group(1) if _m else "OCP"
_parts = _host.split(".")
cluster_short = ".".join(_parts[1:]) if len(_parts) > 2 and _parts[0] in ("api", "console") else _host
page_title = f"{cluster_short} 헬스체크"

TEMPLATE = r"""<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__PAGE_TITLE__</title>
<style>
:root{
  --bg:#f6f4ee; --surface:#ffffff; --surface-2:#efeae0; --border:#ddd6c6;
  --ink:#211f19; --ink-dim:#635b49; --ink-faint:#978d76;
  --accent:#0d5c54; --accent-soft:#e2efec;
  --good:#2f7d3c; --good-bg:#e3f2e2;
  --warn:#9a6700; --warn-bg:#fbf0d3;
  --crit:#ac2b23; --crit-bg:#fae3e0;
  --mono-surface:#f1ede1;
  --seal-ring:rgba(33,31,25,0.08);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#15130f; --surface:#1d1b16; --surface-2:#26221a; --border:#37311f;
    --ink:#efeadd; --ink-dim:#b6ad97; --ink-faint:#847a63;
    --accent:#5fcfc0; --accent-soft:rgba(95,207,192,0.14);
    --good:#5abf67; --good-bg:rgba(90,191,103,0.16);
    --warn:#e0a63a; --warn-bg:rgba(224,166,58,0.16);
    --crit:#e58177; --crit-bg:rgba(229,129,119,0.16);
    --mono-surface:#19170f;
    --seal-ring:rgba(239,234,221,0.1);
  }
}
:root[data-theme="dark"]{
  --bg:#15130f; --surface:#1d1b16; --surface-2:#26221a; --border:#37311f;
  --ink:#efeadd; --ink-dim:#b6ad97; --ink-faint:#847a63;
  --accent:#5fcfc0; --accent-soft:rgba(95,207,192,0.14);
  --good:#5abf67; --good-bg:rgba(90,191,103,0.16);
  --warn:#e0a63a; --warn-bg:rgba(224,166,58,0.16);
  --crit:#e58177; --crit-bg:rgba(229,129,119,0.16);
  --mono-surface:#19170f;
  --seal-ring:rgba(239,234,221,0.1);
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:"IBM Plex Sans", ui-sans-serif, system-ui, sans-serif;
  padding:0 20px 64px; font-size:15px; line-height:1.6;
}
h1,h2{font-family:"IBM Plex Serif","Noto Serif KR",Georgia,"Batang",serif; text-wrap:balance; margin:0; font-weight:600}
.mono{font-family:"IBM Plex Mono", ui-monospace, "SFMono-Regular", monospace; font-variant-numeric:tabular-nums}
a{color:var(--accent)}

.cover{
  max-width:1080px; margin:0 auto; padding:36px 0 22px; border-bottom:1px solid var(--border);
}
.cover-top{display:flex; flex-wrap:wrap; align-items:flex-start; justify-content:space-between; gap:18px 28px}
.cover-eyebrow{font-size:11px; font-weight:600; letter-spacing:.14em; text-transform:uppercase; color:var(--accent); margin-bottom:10px}
.cover-title{font-size:32px; line-height:1.2}
.cover-meta{display:flex; flex-wrap:wrap; gap:6px 22px; font-size:12.5px; color:var(--ink-dim); margin-top:14px}
.cover-meta .mono{color:var(--ink)}
.seal{
  display:inline-flex; align-items:center; gap:9px; padding:9px 16px; border-radius:10px;
  font-size:13px; font-weight:700; letter-spacing:.02em; flex:none;
  box-shadow:0 0 0 5px var(--seal-ring);
}
.seal::before{content:""; width:9px; height:9px; border-radius:50%; background:currentColor; flex:none}
.st-ok{color:var(--good); background:var(--good-bg)}
.st-warn{color:var(--warn); background:var(--warn-bg)}
.st-attn{color:var(--warn); background:var(--warn-bg)}
.st-crit{color:var(--crit); background:var(--crit-bg)}
.st-skip{color:var(--ink-faint); background:var(--surface-2)}
.st-manual{color:var(--accent); background:var(--accent-soft)}
.pill{
  display:inline-flex; align-items:center; gap:6px; padding:5px 12px; border-radius:999px;
  font-size:12.5px; font-weight:600; letter-spacing:.02em;
}
.pill::before{content:""; width:7px; height:7px; border-radius:50%; background:currentColor}

.topbar{
  position:sticky; top:0; z-index:5; background:var(--surface); border-bottom:1px solid var(--border);
  margin:0 -20px 32px; padding:10px 20px; display:flex; flex-wrap:wrap; gap:8px 20px; align-items:center;
  backdrop-filter:blur(6px); font-size:12.5px; color:var(--ink-dim);
}
.topbar-title{font-weight:700; color:var(--ink)}
.topbar-spacer{flex:1}

main{max-width:1080px; margin:0 auto}
.eyebrow{font-size:11.5px; font-weight:600; letter-spacing:.09em; text-transform:uppercase; color:var(--ink-faint); margin-bottom:6px}
section.block{margin-bottom:44px}
.block-head{display:flex; align-items:baseline; gap:12px; margin-bottom:16px; padding-bottom:10px; border-bottom:1px solid var(--border); flex-wrap:wrap}
.sec-no{font-family:"IBM Plex Mono",monospace; font-size:12px; font-weight:600; color:var(--accent); letter-spacing:.04em}
.block-head h2{font-size:20px}
.block-head .count{font-size:12.5px; color:var(--ink-faint); margin-left:auto}

.grid-summary{display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:14px; margin-bottom:8px}
.card{background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:18px}
.stat-tile .stat-num{font-family:"IBM Plex Mono"; font-size:32px; font-weight:600; font-variant-numeric:tabular-nums; line-height:1}
.stat-tile .stat-label{font-size:12.5px; color:var(--ink-dim); margin-top:6px}

.donut-card{display:flex; align-items:center; gap:18px}
.donut{width:96px; height:96px; flex:none}
.donut-num{font-family:"IBM Plex Mono"; font-size:22px; font-weight:700; fill:var(--ink)}
.donut-sub{font-size:10px; fill:var(--ink-faint)}
.donut-legend{display:flex; flex-direction:column; gap:5px; font-size:12.5px}
.legend-row{display:flex; align-items:center; gap:7px; color:var(--ink-dim)}
.legend-dot{width:8px; height:8px; border-radius:50%; flex:none}

.cov-row{display:grid; grid-template-columns:96px 1fr 88px; align-items:center; gap:10px; padding:6px 0}
.cov-label{display:flex; align-items:center; gap:6px; font-size:12.5px; color:var(--ink-dim); white-space:nowrap}
.cov-num{font-family:"IBM Plex Mono"; color:var(--ink-faint)}
.cov-track{display:flex; height:8px; border-radius:5px; overflow:hidden; background:var(--surface-2)}
.cov-seg{height:100%}
.cov-ok{background:var(--good)}
.cov-skip{background:var(--ink-faint); opacity:.55}
.cov-attn{background:var(--warn)}
.cov-count{font-family:"IBM Plex Mono"; font-size:12px; text-align:right; color:var(--ink-dim)}
.cov-count-dim{color:var(--ink-faint)}

.topology{display:flex; flex-wrap:wrap; gap:14px}
.lane{flex:1 1 260px; background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:14px}
.lane-head{display:flex; justify-content:space-between; align-items:baseline; margin-bottom:10px}
.lane-label{font-weight:700; font-size:13.5px}
.lane-count{font-family:"IBM Plex Mono"; font-size:12px; color:var(--ink-faint)}
.lane-body{display:flex; flex-direction:column; gap:8px}
.node-chip{background:var(--surface-2); border:1px solid var(--border); border-radius:8px; padding:9px 11px}
.node-chip-name{font-family:"IBM Plex Mono"; font-size:12.5px; font-weight:600}
.node-chip-meta{display:flex; gap:10px; font-family:"IBM Plex Mono"; font-size:11px; color:var(--ink-dim); margin-top:3px; font-variant-numeric:tabular-nums}
.node-chip-roles{font-size:10.5px; color:var(--ink-faint); margin-top:3px}

.tgt-grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:1px; background:var(--border); border:1px solid var(--border); border-radius:12px; overflow:hidden}
.tgt{background:var(--surface); padding:11px 13px}
.tgt-k{font-size:11px; color:var(--ink-faint); letter-spacing:.02em}
.tgt-v{font-family:"IBM Plex Mono"; font-size:12.5px; margin-top:2px; word-break:break-all}

.co-table{width:100%; border-collapse:collapse; font-size:12.5px}
.co-table th{
  text-align:left; font-size:11px; text-transform:uppercase; letter-spacing:.04em; color:var(--ink-faint);
  padding:8px 10px; border-bottom:1px solid var(--border); position:sticky; top:0; background:var(--surface);
}
.co-table td{padding:6px 10px; border-bottom:1px solid var(--border); font-size:12.5px}
.co-table tbody tr:hover{background:var(--surface-2)}
.co-badge{font-size:11px; font-weight:600; padding:2px 8px; border-radius:999px; white-space:nowrap}
.co-badge.co-ok{color:var(--good); background:var(--good-bg)}
.co-badge.co-warn{color:var(--warn); background:var(--warn-bg)}
.co-badge.co-crit{color:var(--crit); background:var(--crit-bg)}
.co-badge.co-unjudged{color:var(--ink-faint); background:var(--surface-2)}
.co-grid{display:flex; flex-wrap:wrap; gap:6px; overflow-x:auto}
.co-chip{
  display:inline-flex; align-items:center; gap:6px; font-family:"IBM Plex Mono"; font-size:11.5px;
  padding:5px 9px; border-radius:7px; background:var(--surface-2); border:1px solid var(--border); color:var(--ink-dim);
}
.co-dot{width:6px; height:6px; border-radius:50%}
.co-ok .co-dot{background:var(--good)} .co-ok{color:var(--ink)}
.co-warn .co-dot{background:var(--warn)} .co-warn{color:var(--warn); border-color:var(--warn)}
.co-crit .co-dot{background:var(--crit)} .co-crit{color:var(--crit); border-color:var(--crit)}
.co-unknown .co-dot{background:var(--accent)} .co-unknown{color:var(--accent); border-color:var(--accent)}
.co-unjudged .co-dot{background:var(--ink-faint)} .co-unjudged{color:var(--ink-faint); font-style:italic}
.co-extra{margin-top:14px; padding-top:14px; border-top:1px dashed var(--border)}
.co-extra-label{font-size:12px; color:var(--warn); font-weight:600; margin-bottom:8px}

.item{background:var(--surface); border:1px solid var(--border); border-radius:10px; margin-bottom:8px; overflow:hidden}
.item summary{
  list-style:none; cursor:pointer; display:flex; align-items:center; gap:12px; padding:11px 14px;
  font-size:13.5px; user-select:none;
}
.item summary::-webkit-details-marker{display:none}
.item summary::before{content:"▸"; color:var(--ink-faint); font-size:11px; transition:transform .15s}
.item[open] summary::before{transform:rotate(90deg)}
.item-head{display:flex; align-items:center; gap:12px; padding:11px 14px; font-size:13.5px}
.item-num{font-family:"IBM Plex Mono"; color:var(--ink-faint); font-size:12px; flex:none; width:52px}
.item-desc{flex:1; min-width:0}
.item-status{font-size:11px; font-weight:600; padding:3px 9px; border-radius:999px; flex:none}
.item-summary{
  margin:0 14px 10px; padding:10px 12px; background:var(--accent-soft); border:1px solid var(--border);
  border-radius:8px; font-family:"IBM Plex Mono"; font-size:12px; line-height:1.6; white-space:pre;
  overflow-x:auto; color:var(--ink);
}
.item-toggle{border-top:1px solid var(--border)}
.item-toggle summary{
  list-style:none; cursor:pointer; padding:8px 14px; font-size:12px; color:var(--accent); user-select:none;
}
.item-toggle summary::-webkit-details-marker{display:none}
.item-toggle summary::before{content:"▸ "; font-size:10px}
.item-toggle[open] summary::before{content:"▾ "}
.item-body{padding:0 14px 14px}
.item-cmd{font-family:"IBM Plex Mono"; font-size:11.5px; color:var(--accent); background:var(--accent-soft); border-radius:6px; padding:7px 10px; margin-bottom:8px; overflow-x:auto; white-space:pre}
.item-body pre{
  font-family:"IBM Plex Mono"; font-size:11.5px; line-height:1.6; background:var(--mono-surface);
  border:1px solid var(--border); border-radius:8px; padding:12px; margin:0; overflow-x:auto; color:var(--ink-dim);
  max-height:480px; overflow-y:auto; white-space:pre; tab-size:2;
}

.co-table-hint{font-size:12px; color:var(--ink-faint); margin-top:10px}
footer{max-width:1080px; margin:48px auto 0; padding-top:18px; border-top:1px solid var(--border); font-size:12px; color:var(--ink-faint); display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px}

.btn-print{
  appearance:none; border:1px solid var(--border); background:var(--surface-2); color:var(--ink);
  font:inherit; font-size:12.5px; font-weight:600; padding:7px 14px; border-radius:8px; cursor:pointer;
  display:inline-flex; align-items:center; gap:6px;
}
.btn-print:hover{border-color:var(--accent); color:var(--accent)}

@media (max-width:640px){
  .cov-row{grid-template-columns:1fr; row-gap:6px}
  .cov-count{text-align:left}
  .donut-card{flex-direction:column; align-items:flex-start}
}

@page{ size:A4; margin:16mm 14mm }

@media print{
  /* 다크 모드 브라우저에서 인쇄해도 항상 밝은 팔레트로 고정 — 그대로 두면
     body 배경/글자색만 흰색/검정으로 바뀌고 --ink/--accent 등 CSS 변수는
     다크 테마 값(거의 흰색)에 머물러, 흰 배경에 밝은 글자가 겹쳐 안 보이게 된다. */
  :root, :root:not([data-theme="light"]), :root[data-theme="dark"]{
    --bg:#ffffff; --surface:#ffffff; --surface-2:#f2f0e8; --border:#c7c0a9;
    --ink:#1a1810; --ink-dim:#4a4433; --ink-faint:#726a55;
    --accent:#0d5c54; --accent-soft:#e2efec;
    --good:#256b30; --good-bg:#deefdc;
    --warn:#7d5400; --warn-bg:#f8edc8;
    --crit:#9c231b; --crit-bg:#f8ddda;
    --mono-surface:#f5f3ea;
    --seal-ring:rgba(0,0,0,.1);
  }
  body{padding:0}
  .cover{border-bottom:2px solid #000; break-after:avoid}
  .topbar{position:static; backdrop-filter:none; margin:0 0 18px; border-bottom:1px solid #999}
  .btn-print{display:none}
  h2,.block-head{break-after:avoid}
  .item{border:1px solid #999; break-inside:avoid}
  .item summary::before, .item-toggle summary::before{display:none}
  .item-toggle{border-top-color:#999}
  .item-body pre{max-height:none; overflow:visible; border-color:#999; white-space:pre-wrap; overflow-wrap:anywhere; word-break:normal; font-size:12px; line-height:1.7}
  .pill,.seal,.item-status,.co-chip{border:1px solid currentColor}
  .card,.lane{break-inside:avoid; border-color:#999}
  section.block{break-inside:avoid-page}
  *{-webkit-print-color-adjust:exact; print-color-adjust:exact}
}
</style>

<header class="cover">
  <div class="cover-top">
    <div>
      <div class="cover-eyebrow">OpenShift Virtualization 정기점검 리포트</div>
      <h1 class="cover-title">__PAGE_TITLE__</h1>
      <div class="cover-meta">
        <span>대상 <span class="mono">__SERVER__</span></span>
        <span>계정 <span class="mono">__USER__</span></span>
        <span>시작 <span class="mono">__START__</span></span>
        <span>종료 <span class="mono">__END__</span></span>
      </div>
    </div>
    <span class="seal __OVERALL_CLS__">__OVERALL_LABEL__</span>
  </div>
</header>

<div class="topbar">
  <span class="topbar-title">◆ __PAGE_TITLE__</span>
  <div class="topbar-spacer"></div>
  <button class="btn-print" onclick="window.print()">🖨 PDF로 저장</button>
  <span class="pill __OVERALL_CLS__">__OVERALL_LABEL__</span>
</div>

<main>
  <section class="block">
    <div class="eyebrow">정기점검 요약</div>
    <h2 style="margin-bottom:16px">1&ndash;5번 항목 자동 수집 결과</h2>
    <div class="grid-summary">
      <div class="card stat-tile">
        <div class="stat-num">__NODE_COUNT__</div>
        <div class="stat-label">Node (Control Plane __CP_COUNT__ · Infra __INFRA_COUNT__ · Worker __WORKER_COUNT__)</div>
      </div>
      <div class="card donut-card">
        __DONUT_SVG__
        <div class="donut-legend">
          <div class="legend-row"><span class="legend-dot" style="background:var(--good)"></span>정상 __CO_OK__</div>
          <div class="legend-row"><span class="legend-dot" style="background:var(--warn)"></span>주의 __CO_WARN__</div>
          <div class="legend-row"><span class="legend-dot" style="background:var(--crit)"></span>이상 __CO_CRIT__</div>
          <div class="legend-row"><span class="legend-dot" style="background:var(--ink-faint)"></span>판정불가 __CO_UNJUDGED__</div>
        </div>
      </div>
      <div class="card stat-tile">
        <div class="stat-num">__SKIPPED_TOTAL__</div>
        <div class="stat-label">대상 없음으로 건너뛴 항목 (3&ndash;5번 구간, 오류 아님)</div>
      </div>
    </div>
    <div class="card" style="margin-top:14px">
      <div class="eyebrow" style="margin-bottom:10px">3&ndash;5번 구간 수집 현황</div>
      __COVERAGE_HTML__
    </div>
  </section>

  <section class="block">
    <div class="block-head"><span class="sec-no">01</span><h2>Cluster 구성</h2><span class="count">Node __NODE_COUNT__대</span></div>
    <div class="topology">__TOPOLOGY_HTML__</div>
    <div class="co-table-hint">원본 명령 출력 ▾</div>
    __ITEMS1_HTML__
  </section>

  <section class="block">
    <div class="block-head"><span class="sec-no">02</span><h2>Cluster Operator 상태</h2><span class="count">고정 34개 + 목록 외 __EXTRA_COUNT__개</span></div>
    <div class="card">
      <div class="co-grid">__CO_GRID_HTML__</div>
      __EXTRA_CO_HTML__
    </div>
  </section>

  <section class="block">
    <div class="block-head"><span class="sec-no">03</span><h2>워크로드/리소스 현황 및 API 연동 확인</h2><span class="count">__C3_OK__/__C3_TOTAL__ 건 수집</span></div>
    __ITEMS3_HTML__
  </section>

  <section class="block">
    <div class="block-head"><span class="sec-no">04</span><h2>Network 상태 확인</h2><span class="count">__C4_OK__/__C4_TOTAL__ 건 수집</span></div>
    __ITEMS4_HTML__
  </section>

  <section class="block">
    <div class="block-head"><span class="sec-no">05</span><h2>Virtualization 점검</h2><span class="count">__C5_OK__/__C5_TOTAL__ 건 수집</span></div>
    __ITEMS5_HTML__
  </section>

  <section class="block">
    <div class="block-head"><span class="sec-no">부록</span><h2>이번 점검 자동 탐지 대상</h2><span class="count">실행마다 무작위 재선정</span></div>
    <div class="tgt-grid">__TARGETS_HTML__</div>
  </section>
</main>

<footer>
  <span>본 리포트는 OCP-HCK-Score.sh에 의해 자동 생성되었습니다 &middot; 항목 번호는 OCP_Virtualization_정기점검_체크리스트.xlsx 시트 구성과 동일합니다</span>
  <span>판정은 사람이 xlsx에 최종 기입 &middot; 종료 __END__</span>
</footer>

<script>
// PDF 페이지 수 축소(2026-09-15, 이주석 제안 — "70페이지+ 나온다") — 이전엔 인쇄 시
// 모든 항목의 원본 로그(.item-toggle)를 강제로 펼쳐서 항목당 수십 줄씩 그대로 PDF에
// 찍혔음. 화면에서 보이는 상태(확인 필요 항목만 열림) 그대로 인쇄하도록 강제 펼침을 제거.
// 항목 머리글 + 요약은 어차피 접힘과 무관하게 항상 보이므로 정보 손실은 없다.
</script>
"""

html_out = (TEMPLATE
    .replace("__PAGE_TITLE__", esc(page_title))
    .replace("__SERVER__", esc(header.get("server","")))
    .replace("__USER__", esc(header.get("user","")))
    .replace("__START__", esc(header.get("start","")))
    .replace("__END__", esc(header.get("end","")))
    .replace("__OVERALL_CLS__", overall_cls)
    .replace("__OVERALL_LABEL__", overall_label)
    .replace("__NODE_COUNT__", str(len(node_rows)))
    .replace("__CP_COUNT__", str(len(lanes[0])))
    .replace("__INFRA_COUNT__", str(len(lanes[1])))
    .replace("__WORKER_COUNT__", str(len(lanes[2])))
    .replace("__DONUT_SVG__", donut_svg)
    .replace("__CO_OK__", str(co_ok))
    .replace("__CO_WARN__", str(co_warn))
    .replace("__CO_CRIT__", str(co_crit))
    .replace("__CO_UNJUDGED__", str(co_unjudged + co_lookup_failed))
    .replace("__SKIPPED_TOTAL__", str(skipped_total))
    .replace("__COVERAGE_HTML__", coverage_html)
    .replace("__TOPOLOGY_HTML__", topology_html)
    .replace("__ITEMS1_HTML__", f'<details class="item"><summary><span class="item-num">1&ndash;x</span><span class="item-desc">Node 원본 조회 결과 (1-1/1-2/1-3)</span><span class="item-status st-ok">수집 완료</span></summary><div class="item-body">{items1_html}</div></details>')
    .replace("__EXTRA_COUNT__", str(len(extra_co_names)))
    .replace("__CO_GRID_HTML__", co_grid_html)
    .replace("__EXTRA_CO_HTML__", extra_co_html)
    .replace("__TARGETS_HTML__", targets_html)
    .replace("__C3_OK__", str(c3["ok"])).replace("__C3_TOTAL__", str(c3["total"])).replace("__ITEMS3_HTML__", items3_html)
    .replace("__C4_OK__", str(c4["ok"])).replace("__C4_TOTAL__", str(c4["total"])).replace("__ITEMS4_HTML__", items4_html)
    .replace("__C5_OK__", str(c5["ok"])).replace("__C5_TOTAL__", str(c5["total"])).replace("__ITEMS5_HTML__", items5_html)
)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html_out)
PYEOF
  then
    ok "HTML 리포트 생성 완료: ${HTML_REPORT} (브라우저에서 열어 우측 상단 'PDF로 저장' 버튼으로 PDF 변환 가능)"
  else
    warn "HTML 리포트 생성 실패 — 텍스트 리포트만 확인하세요 (${REPORT})"
  fi
else
  warn "python3이 없어 HTML 리포트를 건너뜁니다 — 텍스트 리포트만 생성됨 (${REPORT})"
fi

echo ""
echo -e "${GREEN}✔ 수집 완료: ${REPORT}${NC}"
[ "$HAS_PY" -eq 1 ] && [ -f "$HTML_REPORT" ] && echo -e "${GREEN}✔ HTML 대시보드: ${HTML_REPORT}${NC} (브라우저로 열기 → 우측 상단 'PDF로 저장')"
echo "  위 리포트의 값을 OCP_Virtualization_정기점검_체크리스트.xlsx 의 '점검결과' 컬럼에 옮겨 적으세요."
echo "  (항목번호는 xlsx 시트 구성과 동일합니다: 1.Cluster구성 / 2.ClusterOperator / 3.API연동 / 4.Network / 5.Virtualization)"
echo "  ※ 5-3(VM Console 접속)은 대화형 명령이라 자동 실행되지 않으니 리포트에 안내된 명령을 직접 실행해 확인하세요."
echo ""

# FAIL_COUNT는 run_cmd/5-1/5-2가 실제 명령 실패 시 누적한다 — cron/모니터링이
# 점검 실패를 exit code로 감지할 수 있도록 여기서 반영한다.
if [ "$FAIL_COUNT" -gt 0 ]; then
  echo -e "${YELLOW}⚠ 총 ${FAIL_COUNT}개 항목에서 명령 실행 실패가 감지되었습니다: ${FAILED_ITEMS[*]} — 리포트를 확인하세요.${NC}"
  exit 1
fi
exit 0
