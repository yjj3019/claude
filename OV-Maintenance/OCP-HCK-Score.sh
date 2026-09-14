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
: > "$REPORT"

write() { echo -e "$1" | tee -a "$REPORT" >/dev/null; }
raw()   { echo -e "$1" >> "$REPORT"; }

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
)
raw ""
raw "번호 | Operator | AVAILABLE | PROGRESSING | DEGRADED | 판정"
raw "--------------------------------------------------------------"
idx=1
for op in "${OPERATORS[@]}"; do
  if [ "$HAS_JQ" -eq 1 ]; then
    JSON=$(oc get co "$op" -o json 2>/dev/null)
    if [ -z "$JSON" ]; then
      raw "2-${idx} | ${op} | - | - | - | [조회 실패/미존재]"
    else
      AVAIL=$(echo "$JSON" | jq -r '.status.conditions[]|select(.type=="Available")|.status')
      PROG=$(echo "$JSON"  | jq -r '.status.conditions[]|select(.type=="Progressing")|.status')
      DEG=$(echo "$JSON"   | jq -r '.status.conditions[]|select(.type=="Degraded")|.status')
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
      raw "2-${idx} | ${op} | ${AVAIL} | ${PROG} | ${DEG} | ${VERDICT}"
    fi
  else
    LINE=$(oc get co "$op" --no-headers 2>/dev/null)
    if [ -z "$LINE" ]; then
      raw "2-${idx} | ${op} | [조회 실패/미존재]"
    else
      raw "2-${idx} | ${op} | ${LINE}"
    fi
  fi
  idx=$((idx+1))
done
ok "Cluster Operator 32개 상태 수집 완료 (jq 미설치 시 원본 라인만 기록 — 3번째 컬럼부터 AVAILABLE/PROGRESSING/DEGRADED/SINCE 순)"

# 위 고정 32개 목록에 없는 Operator가 클러스터에 실재하면(버전 차이/클라우드 특화 등)
# 그 상태를 놓칠 수 있으므로 실제 CO 목록과 대조해 목록 밖 항목만 별도로 남긴다.
ALL_CO=$(oc get co -o jsonpath='{.items[*].metadata.name}' 2>/dev/null)
EXTRA_CO=""
for co in $ALL_CO; do
  printf '%s\n' "${OPERATORS[@]}" | grep -qx "$co" || EXTRA_CO="${EXTRA_CO}${co} "
done
if [ -n "$EXTRA_CO" ]; then
  raw "[목록 외 Operator 발견] ${EXTRA_CO}(고정 32개 목록에 없음 — 'oc get co ${EXTRA_CO}'로 별도 확인 필요)"
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

Q_SVC=""
Q_PVC=""
[ -n "$Q_NS" ] && Q_SVC=$(oc get svc -n "$Q_NS" -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null | rand_line)
[ -n "$Q_NS" ] && Q_PVC=$(oc get pvc -n "$Q_NS" -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null | rand_line)
Q_PV=$(oc get pv -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null | rand_line)
Q_ROUTE=""
[ -n "$Q_NS" ] && Q_ROUTE=$(oc get route -n "$Q_NS" -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null | rand_line)

# 같은 namespace 안의 '다른' Pod 중 무작위 1개의 IP (Pod간 통신 테스트용 목적지)
Q_PEER_IP=""
if [ -n "$Q_NS" ]; then
  Q_PEER_IP=$(oc get pods -n "$Q_NS" --field-selector=status.phase=Running \
    -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.status.podIP}{"\n"}{end}' 2>/dev/null \
    | awk -v me="$Q_POD" '$1!=me && $2!="" {print $2}' | rand_line)
  # 같은 ns에 다른 Pod가 없으면, DNS 서비스 IP로 대체 (항상 존재하는 안전한 ping 대상)
  if [ -z "$Q_PEER_IP" ]; then
    Q_PEER_IP=$(oc get svc -n openshift-dns dns-default -o jsonpath='{.spec.clusterIP}' 2>/dev/null)
  fi
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
raw "  Pod간 통신 대상 IP : ${Q_PEER_IP:-없음}"
raw "  VM(대표)        : ${V_NS:-없음}/${V_VM:-없음}"
raw "  ※ 위 대상은 매 실행마다 클러스터 전체에서 무작위로 재선정됩니다(같은 대상만 반복 점검하는 것을 방지)."
raw "     Namespace/Pod(대표)는 '현재 Running 중인 임의의 Pod 1개'의 네임스페이스이므로, 그 네임스페이스가"
raw "     인프라 성격(예: openshift-ovn-kubernetes 등)이면 PVC/최근 이벤트가 원래 없어 'No resources found'가"
raw "     정상적으로 나올 수 있습니다 — 이는 결함이 아니라 해당 네임스페이스의 실제 상태입니다."
raw "     VM(대표)는 '실행 중 여부와 무관하게 클러스터 전체 VM 중 무작위 1개'이므로, 하필 꺼져있는 VM이"
raw "     뽑히면 5-4(CPU/Memory) 등에서 virt-launcher Pod가 없어 'No resources found'가 나올 수 있습니다."
raw "     특정 네임스페이스/VM을 반드시 점검해야 한다면 위 무작위 결과 대신 수동 명령으로 재확인하세요."
ok "자동 탐지 완료 — 아래 항목은 위 대상을 기준으로 자동 실행됩니다"

# ════════════════════════════════════════════════════════════
section "3. API 연동 확인"

run_cmd "3-1-1" "Namespace 리스트/상세 조회" "oc get ns / oc describe ns" -- bash -c "
  rc=0
  oc get ns || rc=\$?
  if [ -n '$Q_NS' ]; then oc describe ns '$Q_NS' || rc=\$?; else echo '(네임스페이스 없음 - 건너뜀)'; fi
  exit \$rc"
run_cmd "3-1-2" "Pod 리스트/상세 조회" "oc get po -n <ns> / oc describe po" -- bash -c "
  rc=0
  if [ -n '$Q_NS' ]; then oc get po -n '$Q_NS' || rc=\$?; else echo '(네임스페이스 없음 - 건너뜀)'; fi
  if [ -n '$Q_NS' ] && [ -n '$Q_POD' ]; then oc describe po '$Q_POD' -n '$Q_NS' || rc=\$?; else echo '(Pod 없음 - 건너뜀)'; fi
  exit \$rc"
run_cmd "3-1-3" "Node 리스트/상세 조회" "oc get node / oc describe node" -- bash -c "
  rc=0
  oc get node || rc=\$?
  if [ -n '$Q_NODE' ]; then oc describe node '$Q_NODE' || rc=\$?; else echo '(Node 없음 - 건너뜀)'; fi
  exit \$rc"
run_cmd "3-1-4" "Service 리스트/상세 조회" "oc get svc -n <ns> / oc describe svc" -- bash -c "
  rc=0
  if [ -n '$Q_NS' ]; then oc get svc -n '$Q_NS' || rc=\$?; else echo '(네임스페이스 없음 - 건너뜀)'; fi
  if [ -n '$Q_NS' ] && [ -n '$Q_SVC' ]; then oc describe svc '$Q_SVC' -n '$Q_NS' || rc=\$?; else echo '(Service 없음 - 건너뜀)'; fi
  exit \$rc"
run_cmd "3-1-5" "PV 리스트/상세 조회" "oc get pv / oc describe pv" -- bash -c "
  rc=0
  oc get pv || rc=\$?
  if [ -n '$Q_PV' ]; then oc describe pv '$Q_PV' || rc=\$?; else echo '(PV 없음 - 건너뜀)'; fi
  exit \$rc"
run_cmd "3-1-6" "PVC 리스트/상세 조회" "oc get pvc -n <ns> / oc describe pvc" -- bash -c "
  rc=0
  if [ -n '$Q_NS' ]; then oc get pvc -n '$Q_NS' || rc=\$?; else echo '(네임스페이스 없음 - 건너뜀)'; fi
  if [ -n '$Q_NS' ] && [ -n '$Q_PVC' ]; then oc describe pvc '$Q_PVC' -n '$Q_NS' || rc=\$?; else echo '(PVC 없음 - 건너뜀)'; fi
  exit \$rc"
run_cmd "3-1-7" "알람 이벤트 조회" "oc get event -n <ns> --sort-by='.lastTimestamp'" -- bash -c "
  set -o pipefail
  if [ -n '$Q_NS' ]; then oc get event -n '$Q_NS' --sort-by='.lastTimestamp' | tail -50; else echo '(네임스페이스 없음 - 건너뜀)'; fi"

run_cmd "3-2-1" "Node CPU/Memory 사용량 조회" "oc adm top node" -- oc adm top node
run_cmd "3-2-2" "Pod CPU/Memory 사용량 조회" "oc adm top pod -n <ns>" -- bash -c "
  if [ -n '$Q_NS' ]; then oc adm top pod -n '$Q_NS'; else echo '(네임스페이스 없음 - 건너뜀)'; fi"

run_cmd "3-3-1" "Pod 로그 조회" "oc logs <pod> -n <ns>" -- bash -c "
  if [ -n '$Q_NS' ] && [ -n '$Q_POD' ]; then oc logs '$Q_POD' -n '$Q_NS' --tail=100; else echo '(Pod 없음 - 건너뜀)'; fi"

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
if [ -n "$NETDEBUG_POD" ]; then
  PING_NS="$NETDEBUG_NS"
  PING_POD="$NETDEBUG_POD"
  raw "[4-2용 대상 Pod 교체] score-debug Pod 사용: ${PING_NS}/${PING_POD} (4-3/4-4는 원래 자동 탐지 대상 ${N_NS}/${N_POD} 유지)"
fi

run_cmd "4-1" "Node Network Interface 연동 확인" "oc debug node/<node> -- chroot /host ip a" -- bash -c "
  rc=0
  if [ -n '$N_NODE' ]; then
    oc debug node/'$N_NODE' -- chroot /host ip a || rc=\$?
    if [ -n '$N_TARGET_IP' ]; then
      oc debug node/'$N_NODE' -- chroot /host ping -c 3 '$N_TARGET_IP' || rc=\$?
    else
      echo '(대상 노드 IP 없음 - ping 건너뜀)'
    fi
  else
    echo '(대상 Node 없음 - 건너뜀)'
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

run_cmd "4-3" "Cluster 외부-내부 Networking 확인" "oc get svc -o wide / oc get route / curl" -- bash -c "
  rc=0
  if [ -n '$N_NS' ]; then
    oc get svc -o wide -n '$N_NS' || rc=\$?
    oc get route -n '$N_NS' || rc=\$?
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

run_cmd "4-4" "Pod 추가 네트워크(Multus) IP 할당 확인" "oc describe pod / network-status annotation" -- bash -c "
  rc=0
  if [ -n '$N_NS' ] && [ -n '$N_POD' ]; then
    oc describe pod '$N_POD' -n '$N_NS' || rc=\$?
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

item_header "5-1" "VM 기동/재기동/종료 정상 동작 확인" "virtctl start/stop <vm> -n <ns> / oc get vm,vmi -n <ns>"
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
    warn "5-1 VM 기동/재기동/종료 확인 실패(상태 미도달 또는 명령 실패) — 리포트 확인"
  fi
else
  raw "[건너뜀: ${SKIP_REASON}]"
  raw "[결과] skip"
  warn "5-1 건너뜀 (${SKIP_REASON})"
fi

item_header "5-2" "Live Migration 동작 확인" "virtctl migrate <vm> -n <ns> / oc get vmim -n <ns>"
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
    warn "5-2 Live Migration 확인 실패(Succeeded 미도달 또는 명령 실패) — 리포트 확인"
  fi
else
  raw "[건너뜀: ${SKIP_REASON}]"
  raw "[결과] skip"
  warn "5-2 건너뜀 (${SKIP_REASON})"
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
run_cmd "5-5" "VM 디스크(DataVolume/PVC) 바인딩 상태 확인" "oc get dv,pvc -n <ns>" -- bash -c "
  if [ -n '$V_NS' ]; then oc get dv,pvc -n '$V_NS'; else echo '(VM 없음 - 건너뜀)'; fi"
run_cmd "5-6" "NodeHealthCheck / Fence Agent 동작 확인" "oc get nhc / oc get far -A" -- bash -c "
  rc=0
  oc get nhc || rc=\$?
  oc get far -A || rc=\$?
  exit \$rc"

run_cmd "5-7" "KubeVirt/CDI 플랫폼 컴포넌트 상태 확인" "oc get hco -n openshift-cnv / oc get pods -n openshift-cnv -l kubevirt.io" -- bash -c "
  rc=0
  oc get hco -n openshift-cnv || rc=\$?
  echo '--- virt-*/cdi-* Pod 상태 ---'
  oc get pods -n openshift-cnv -l 'kubevirt.io in (virt-operator,virt-controller,virt-handler,virt-api)' || rc=\$?
  oc get pods -n openshift-cnv -l 'cdi.kubevirt.io' || rc=\$?
  exit \$rc"

# request 메모리 기준 스케줄링 실패(실사용량이 아니라 Allocated request 소진율이 원인)를
# 진단하려면 노드별 Capacity/Allocatable/Allocated resources가 필요하다는 고객 요구사항
# 반영(2026-09-14). 대상은 위에서 이미 자동 탐지해둔 전체 노드 목록(_NODES)을 그대로 재사용.
_NODES_LIST="${_NODES[*]}"
run_cmd "5-8" "노드별 메모리 Capacity/Allocatable/Allocated(Request 소진율) 확인" "oc describe node <각 노드> | sed -n '/Capacity:/,/Allocatable:/p;/Allocatable:/,/System Info:/p' / grep -A10 'Allocated resources'" -- bash -c "
  rc=0
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

run_cmd "5-9" "OpenShift Virtualization 메모리 Overcommit(higherWorkloadDensity) 설정 확인" "oc get hyperconverged kubevirt-hyperconverged -n openshift-cnv -o jsonpath={.spec.higherWorkloadDensity}" -- oc get hyperconverged kubevirt-hyperconverged -n openshift-cnv -o jsonpath='{.spec.higherWorkloadDensity}{"\n"}'

# 고객 요구사항 추가분(2026-09-14): "노드별 Pod request 상세"는 실제로는 "전체 VM
# (virt-launcher) Pod의 memory request"를 뜻했음 — 특정 노드명이 필요 없어 클러스터
# 전체를 한 번에 자동 점검 가능(특정 VM의 request 확인도 이 표에 포함되므로 별도 항목 불필요).
run_cmd "5-10" "전체 VM(virt-launcher) Pod의 memory request 확인" "oc get pods -A -l kubevirt.io=virt-launcher -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,NODE:.spec.nodeName,REQ:.spec.containers[*].resources.requests.memory" -- oc get pods -A -l kubevirt.io=virt-launcher -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,NODE:.spec.nodeName,REQ:.spec.containers[*].resources.requests.memory

# FailedScheduling은 특정 Pod명을 미리 알아야 하는 진단 명령이었으나, 현재 클러스터에
# 실제로 발생 중인 이벤트를 직접 조회하면 대상을 몰라도 자동 점검 가능(없으면 "정상").
run_cmd "5-11" "VM 스케줄링 실패(FailedScheduling) 이벤트 확인" "oc get events -A --field-selector reason=FailedScheduling --sort-by=.lastTimestamp" -- oc get events -A --field-selector reason=FailedScheduling --sort-by=.lastTimestamp

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
        if len(parts) >= 6:
            # idx | name | avail | prog | deg | verdict
            co_rows.append({"idx": parts[0], "name": parts[1], "avail": parts[2],
                             "prog": parts[3], "deg": parts[4], "verdict": parts[5]})
        else:
            # jq 미설치 환경: "idx | name | <oc 원본 라인>" 3필드뿐 — 판정 불가로 기록(크래시 방지)
            co_rows.append({"idx": parts[0], "name": parts[1] if len(parts) > 1 else "?",
                             "avail": "", "prog": "", "deg": "", "verdict": "[jq 없음 - 원본 확인]"})
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
co_unjudged = sum(1 for r in co_rows if "jq 없음" in r["verdict"])
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

# ---------------------------------------------------------------- CO grid
def co_chip(r):
    if "jq 없음" in r["verdict"] or "조회 실패" in r["verdict"]:
        cls = "co-unjudged"
    elif "정상" in r["verdict"]:
        cls = "co-ok"
    elif "주의" in r["verdict"]:
        cls = "co-warn"
    else:
        cls = "co-crit"
    return f'<div class="co-chip {cls}" title="{esc(r["name"])}: AVAILABLE={esc(r["avail"])} PROGRESSING={esc(r["prog"])} DEGRADED={esc(r["deg"])}"><span class="co-dot"></span>{esc(r["name"])}</div>'

co_grid_html = "".join(co_chip(r) for r in co_rows)
extra_co_html = ""
if extra_co_names:
    chips = "".join(f'<div class="co-chip co-unknown"><span class="co-dot"></span>{esc(n)}</div>' for n in extra_co_names)
    extra_co_html = f'''<div class="co-extra">
      <div class="co-extra-label">⚑ 고정 32개 목록 밖 Operator (신규 발견 — 별도 확인 필요)</div>
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

def item_block(it, open_attn=True):
    label, cls = STATUS_LABEL[it["status"]]
    open_attr = " open" if (it["status"] == "attention" and open_attn) else ""
    body = esc(it["body"]) if it["body"].strip() else "(출력 없음)"
    return f'''<details class="item{open_attr}">
      <summary>
        <span class="item-num">{esc(it["num"])}</span>
        <span class="item-desc">{esc(it["desc"])}</span>
        <span class="item-status {cls}">{label}</span>
      </summary>
      <div class="item-body">
        <div class="item-cmd">$ {esc(it["cmd"])}</div>
        <pre>{body}</pre>
      </div>
    </details>'''

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

.co-grid{display:flex; flex-wrap:wrap; gap:6px}
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
.item-num{font-family:"IBM Plex Mono"; color:var(--ink-faint); font-size:12px; flex:none; width:52px}
.item-desc{flex:1; min-width:0}
.item-status{font-size:11px; font-weight:600; padding:3px 9px; border-radius:999px; flex:none}
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
  body{background:#fff; padding:0; color:#000}
  .cover{border-bottom:2px solid #000; break-after:avoid}
  .topbar{position:static; backdrop-filter:none; margin:0 0 18px; border-bottom:1px solid #999}
  .btn-print{display:none}
  .item{border:1px solid #999; break-inside:avoid}
  .item summary::before{display:none}
  .item-body pre{max-height:none; overflow:visible; border-color:#999; white-space:pre-wrap; word-break:break-all}
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
    <div class="block-head"><span class="sec-no">02</span><h2>Cluster Operator 상태</h2><span class="count">고정 32개 + 목록 외 __EXTRA_COUNT__개</span></div>
    <div class="card">
      <div class="co-grid">__CO_GRID_HTML__</div>
      __EXTRA_CO_HTML__
    </div>
  </section>

  <section class="block">
    <div class="block-head"><span class="sec-no">부록</span><h2>이번 점검 자동 탐지 대상</h2><span class="count">실행마다 무작위 재선정</span></div>
    <div class="tgt-grid">__TARGETS_HTML__</div>
  </section>

  <section class="block">
    <div class="block-head"><span class="sec-no">03</span><h2>API 연동 확인</h2><span class="count">__C3_OK__/__C3_TOTAL__ 건 수집</span></div>
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
</main>

<footer>
  <span>본 리포트는 OCP-HCK-Score.sh에 의해 자동 생성되었습니다 &middot; 항목 번호는 OCP_Virtualization_정기점검_체크리스트.xlsx 시트 구성과 동일합니다</span>
  <span>판정은 사람이 xlsx에 최종 기입 &middot; 종료 __END__</span>
</footer>

<script>
window.addEventListener('beforeprint', function () {
  document.querySelectorAll('details').forEach(function (d) { d.open = true; });
});
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
  echo -e "${YELLOW}⚠ 총 ${FAIL_COUNT}개 항목에서 명령 실행 실패가 감지되었습니다 — 리포트를 확인하세요.${NC}"
  exit 1
fi
exit 0
