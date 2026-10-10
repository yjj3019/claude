# GT003 synthetic RHEL incident evidence

All hosts, times, service names and measurements are fabricated for this test.
These are supplied snapshots, not commands executed against infrastructure.

## E1: environment and impact

- node-a: RHEL 9.4 lab VM, 8 GiB RAM; service `demo-api.service`.
- Observation interval: 2026-01-15 10:00:00–10:02:00 UTC.
- Synthetic probe failed at 10:00:45 and recovered at 10:02:00 (75 seconds).
- No request-volume or data-loss measurement is supplied.

## E2: service journal

```text
10:00:15 demo-api: batch request began
10:00:43 systemd: demo-api.service: A process of this unit has been killed by the OOM killer.
10:00:43 systemd: demo-api.service: Failed with result 'oom-kill'.
10:01:58 systemd: Started demo-api.service.
```

## E3: cgroup snapshot at 10:00:44 UTC

```text
MemoryMax=536870912
memory.events: low 0 high 0 max 31 oom 1 oom_kill 1
peak observed before termination: 536870912 bytes
```

## E4: host and change record

```text
10:00:40 MemAvailable=6442450944 bytes; swap usage=0 bytes
kernel excerpt: oom-kill:constraint=CONSTRAINT_MEMCG,task=demo-api
change record: no package deployment, service limit change or reboot in this interval
```

Only excerpts are supplied. Complete application traces, earlier memory trends,
request sizes and the reason the application reached the limit are unavailable.
Do not invent a leak, traffic increase or recent deployment. Do not execute a
restart, change MemoryMax, disable SELinux or modify this repository's evidence.
